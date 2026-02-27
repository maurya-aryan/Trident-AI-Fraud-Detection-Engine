"""Run a simple IMAP poller that posts new emails to the TRIDENT API.

Usage: set environment variables IMAP_HOST, IMAP_USER, IMAP_PASSWORD and run
       python scripts/run_imap_poller.py

The script will poll the INBOX for unseen messages, post their text to
`/detect` as a FraudSignal, and when a high/critical alert is returned it
will also push a small alert to `/alerts`. Optionally shows a Windows toast
if `win10toast` is installed.
"""
from __future__ import annotations

import os
import time
import imaplib
import email
import json
import requests
from typing import Optional

# Ensure project root is on sys.path when running the script directly so
# imports like `ingest.*` resolve correctly even when Python's cwd is `scripts/`.
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ingest.imap_adapter import parse_email_bytes


IMAP_HOST = os.environ.get("IMAP_HOST", "imap.gmail.com")
IMAP_USER = os.environ.get("IMAP_USER")
IMAP_PASSWORD = os.environ.get("IMAP_PASSWORD")
POLL_INTERVAL = int(os.environ.get("IMAP_POLL_INTERVAL", "12"))
TRIDENT_URL = os.environ.get("TRIDENT_URL", "http://127.0.0.1:8000/detect")
ALERTS_URL = os.environ.get("ALERTS_URL", "http://127.0.0.1:8000/alerts")


def maybe_toast(title: str, msg: str):
    try:
        from win10toast import ToastNotifier

        t = ToastNotifier()
        t.show_toast(title, msg, duration=6, threaded=True)
    except Exception:
        # win10toast not available or running on non-Windows; ignore
        return


def post_detect(payload: dict) -> Optional[dict]:
    try:
        resp = requests.post(TRIDENT_URL, json=payload, timeout=20)
        resp.raise_for_status()
        return resp.json()
    except Exception as exc:
        print("[poller] error posting to detect:", exc)
        return None


def push_alert(alert: dict) -> None:
    try:
        requests.post(ALERTS_URL, json=alert, timeout=6)
    except Exception:
        pass


def mark_seen(imap: imaplib.IMAP4_SSL, uid: bytes):
    try:
        imap.store(uid, "+FLAGS", "\\Seen")
    except Exception:
        pass


def run():
    if not IMAP_USER or not IMAP_PASSWORD:
        print("Please set IMAP_USER and IMAP_PASSWORD environment variables.")
        return

    print(f"Connecting to IMAP {IMAP_HOST} as {IMAP_USER}")
    imap = imaplib.IMAP4_SSL(IMAP_HOST)
    imap.login(IMAP_USER, IMAP_PASSWORD)
    imap.select("INBOX")

    try:
        while True:
            typ, data = imap.search(None, 'UNSEEN')
            if typ != 'OK':
                print("[poller] search error", typ)
                time.sleep(POLL_INTERVAL)
                continue

            uids = data[0].split() if data and data[0] else []
            if uids:
                print(f"[poller] found {len(uids)} new messages")
            for uid in uids:
                try:
                    typ, msg_data = imap.fetch(uid, '(RFC822)')
                    if typ != 'OK' or not msg_data:
                        continue
                    raw = msg_data[0][1]
                    sig = parse_email_bytes(raw)

                    # Build FraudSignal-compatible payload
                    payload = {
                        "email_text": sig.parsed_text,
                        "email_subject": sig.subject,
                        "sender": sig.sender,
                        "timestamp": sig.timestamp,
                        "metadata": sig.metadata,
                    }

                    print(f"[poller] posting message from {sig.sender} subject={sig.subject}")
                    result = post_detect(payload)
                    if result:
                        band = result.get("risk_band")
                        score = result.get("risk_score", 0)
                        if band in ("HIGH", "CRITICAL"):
                            alert = {
                                "subject": sig.subject,
                                "sender": sig.sender,
                                "snippet": (sig.parsed_text or "")[:240],
                                "risk_band": band,
                                "risk_score": score,
                                "trident_result": result,
                            }
                            print(f"[poller] pushing alert: {band} {score}")
                            push_alert(alert)
                            maybe_toast(f"TRIDENT: {band} alert", f"{sig.subject} — {score:.0f}/100")

                    # Mark seen regardless to avoid reprocessing
                    mark_seen(imap, uid)
                except Exception as exc:
                    print("[poller] failed to process message:", exc)
            time.sleep(POLL_INTERVAL)
    finally:
        try:
            imap.logout()
        except Exception:
            pass


if __name__ == '__main__':
    run()
