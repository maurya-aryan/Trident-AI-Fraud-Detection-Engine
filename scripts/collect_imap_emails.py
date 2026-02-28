"""Collect recent emails from IMAP and save to CSV for labelling/training.

Usage:
  Set IMAP_HOST, IMAP_USER, IMAP_PASSWORD in env (or rely on defaults).
  python scripts/collect_imap_emails.py --limit 200 --mark-seen

This script will fetch the most recent messages (by UID) from INBOX,
parse them using `ingest.imap_adapter.parse_email_bytes` and write a CSV
`data/imap_raw_emails.csv` containing: id, subject, sender, timestamp, text.
"""
from __future__ import annotations

import os
import csv
import argparse
import imaplib
import sys
from pathlib import Path

# ensure repo root on path so imports resolve when running from scripts/
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ingest.imap_adapter import parse_email_bytes


IMAP_HOST = os.environ.get("IMAP_HOST", "imap.gmail.com")
IMAP_USER = os.environ.get("IMAP_USER")
IMAP_PASSWORD = os.environ.get("IMAP_PASSWORD")


def fetch(limit: int = 200, mark_seen: bool = False, mailbox: str = "INBOX"):
    if not IMAP_USER or not IMAP_PASSWORD:
        print("Please set IMAP_USER and IMAP_PASSWORD environment variables.")
        return

    imap = imaplib.IMAP4_SSL(IMAP_HOST)
    imap.login(IMAP_USER, IMAP_PASSWORD)
    imap.select(mailbox)

    try:
        typ, data = imap.search(None, 'ALL')
        if typ != 'OK':
            print('Search failed', typ)
            return

        uids = data[0].split() if data and data[0] else []
        # take most recent
        uids = uids[-limit:]

        out_path = Path('data/imap_raw_emails.csv')
        out_path.parent.mkdir(parents=True, exist_ok=True)
        seen_ids = set()
        if out_path.exists():
            try:
                with out_path.open('r', encoding='utf-8', newline='') as f:
                    reader = csv.DictReader(f)
                    for r in reader:
                        seen_ids.add(r.get('id') or '')
            except Exception:
                seen_ids = set()

        with out_path.open('a', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['id', 'subject', 'sender', 'timestamp', 'text'])
            if out_path.stat().st_size == 0:
                writer.writeheader()

            for uid in uids:
                try:
                    typ, msg_data = imap.fetch(uid, '(RFC822)')
                    if typ != 'OK' or not msg_data:
                        continue
                    raw = msg_data[0][1]
                    sig = parse_email_bytes(raw)
                    row_id = uid.decode('utf-8') if isinstance(uid, bytes) else str(uid)
                    if row_id in seen_ids:
                        continue

                    writer.writerow({
                        'id': row_id,
                        'subject': sig.subject or '',
                        'sender': sig.sender or '',
                        'timestamp': sig.timestamp or '',
                        'text': (sig.parsed_text or '').replace('\r', '').replace('\n', '\n'),
                    })
                    seen_ids.add(row_id)

                    if mark_seen:
                        try:
                            imap.store(uid, '+FLAGS', '\\Seen')
                        except Exception:
                            pass
                except Exception as exc:
                    print('Failed to fetch uid', uid, exc)
        print(f'Wrote/updated {out_path}')
    finally:
        try:
            imap.logout()
        except Exception:
            pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--limit', type=int, default=200, help='Max messages to fetch (most recent)')
    ap.add_argument('--mark-seen', action='store_true', help='Mark messages as seen')
    ap.add_argument('--mailbox', type=str, default='INBOX')
    args = ap.parse_args()

    fetch(limit=args.limit, mark_seen=args.mark_seen, mailbox=args.mailbox)


if __name__ == '__main__':
    main()
