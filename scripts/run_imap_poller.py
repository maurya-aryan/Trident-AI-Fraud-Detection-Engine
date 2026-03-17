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

import config
from ingest.imap_adapter import parse_email_bytes
from ingest.imap_processor import IMAPProcessor

IMAP_HOST = os.environ.get("IMAP_HOST", "imap.gmail.com")
IMAP_USER = os.environ.get("IMAP_USER")
IMAP_PASSWORD = os.environ.get("IMAP_PASSWORD")
POLL_INTERVAL = int(os.environ.get("IMAP_POLL_INTERVAL", "12"))
IMAP_MARK_SEEN = str(os.environ.get("IMAP_MARK_SEEN", "false")).lower() in ("1", "true", "yes")
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
        resp = requests.post(TRIDENT_URL, json=payload, timeout=90)
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
    if IMAP_MARK_SEEN:
        imap.uid('STORE', uid, '+FLAGS', '\\Seen')

def connect_imap() -> imaplib.IMAP4_SSL:
    """Create a fresh authenticated IMAP connection."""
    imap = imaplib.IMAP4_SSL(IMAP_HOST)
    imap.login(IMAP_USER, IMAP_PASSWORD)
    return imap


def log(msg: str):
    """Print immediately without buffering"""
    print(f"[poller] {msg}", flush=True)

def run():
    if not IMAP_USER or not IMAP_PASSWORD:
        log("Please set IMAP_USER and IMAP_PASSWORD environment variables.")
        return

    imap_processor = IMAPProcessor(config.IMAP_PROCESSOR_FILE)
    imap: Optional[imaplib.IMAP4_SSL] = None

    while True:
        # --- (Re)connect if we have no live connection ---
        if imap is None:
            try:
                log(f"Connecting to IMAP {IMAP_HOST} as {IMAP_USER}")
                imap = connect_imap()
                log(f"Success! Connected to {IMAP_HOST}")
            except Exception as exc:
                import traceback
                log(f"Connection failed: {exc}")
                traceback.print_exc(file=sys.stdout)
                log(f"Retrying in {POLL_INTERVAL}s …")
                time.sleep(POLL_INTERVAL)
                continue

        try:
            # Re-select INBOX every cycle so the server refreshes its
            # message-count state and exposes emails that arrived since the
            # last poll.  Without this, SEARCH UNSEEN only sees messages
            # present when the mailbox was first selected.
            imap.select("INBOX")
            log("Checking for UNSEEN messages...")

            typ, data = imap.search(None, 'UNSEEN')
            if typ != 'OK':
                log(f"search error {typ}")
                time.sleep(POLL_INTERVAL)
                continue

            uids = data[0].split() if data and data[0] else []
            if uids:
                log(f"found {len(uids)} new messages")
            else:
                log("No new messages found. Waiting...")
                
            for uid in uids:
                try:
                    typ, msg_data = imap.fetch(uid, '(RFC822)')
                    if typ != 'OK' or not msg_data:
                        continue
                    raw = msg_data[0][1]
                    signal = imap_processor.process_email(uid, raw)
                    if signal is None:
                        log(f"message already processed: {uid}")
                        continue

                    # Build FraudSignal-compatible payload
                    payload = {
                        "email_text": signal.parsed_text,
                        "email_subject": signal.subject,
                        "sender": signal.sender,
                        "timestamp": signal.timestamp,
                        "metadata": signal.metadata,
                    }

                    log(f"posting message from {signal.sender} subject={signal.subject}")
                    result = post_detect(payload)
                    if result:
                        band = result.get("risk_band")
                        score = result.get("risk_score", 0)
                        # Always push every processed email to /alerts so the
                        # dashboard shows the full picture, not only HIGH/CRITICAL.
                        alert = {
                            "subject": signal.subject,
                            "sender": signal.sender,
                            "email_text": signal.parsed_text or "",
                            "snippet": (signal.parsed_text or "")[:240],
                            "risk_band": band,
                            "risk_score": score,
                            "trident_result": result,
                        }
                        log(f"alert queued: {band} score={score:.1f} — {signal.subject}")
                        push_alert(alert)
                        # Windows toast popup only for HIGH / CRITICAL
                        if band in ("HIGH", "CRITICAL"):
                            maybe_toast(f"TRIDENT: {band} alert", f"{signal.subject} — {score:.0f}/100")

                    # Mark seen optionally to avoid reprocessing (controlled by IMAP_MARK_SEEN)
                    if IMAP_MARK_SEEN:
                        mark_seen(imap, uid)
                except Exception as exc:
                    log(f"failed to process message: {exc}")

        except (imaplib.IMAP4.abort, imaplib.IMAP4.error, OSError) as exc:
            # Connection was dropped or went stale — discard it and reconnect
            # on the next iteration instead of crashing the poller.
            log(f"IMAP connection lost ({exc}). Will reconnect …")
            try:
                imap.logout()
            except Exception:
                pass
            imap = None

        time.sleep(POLL_INTERVAL)

if __name__ == '__main__':
    run()
