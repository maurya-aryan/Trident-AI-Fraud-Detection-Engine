"""Utility to remove the IMAP \Seen flag for messages.

Use with caution. By default this will unmark messages received in the last
`--days` days (default 7). Pass `--all` to unmark every message in the mailbox.

Requires IMAP_HOST, IMAP_USER, IMAP_PASSWORD environment variables.

Example:
  # unmark messages from last 7 days
  python scripts/unmark_seen_imap.py --days 7

  # unmark all messages (use carefully)
  python scripts/unmark_seen_imap.py --all
"""
from __future__ import annotations

import os
import argparse
import imaplib
import datetime
import sys

# ensure imports work when running from scripts/
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

IMAP_HOST = os.environ.get("IMAP_HOST", "imap.gmail.com")
IMAP_USER = os.environ.get("IMAP_USER")
IMAP_PASSWORD = os.environ.get("IMAP_PASSWORD")


def unmark_all(mailbox: str = 'INBOX'):
    if not IMAP_USER or not IMAP_PASSWORD:
        print('Please set IMAP_USER and IMAP_PASSWORD environment variables.')
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
        print(f'Found {len(uids)} messages; removing \Seen flag for all...')
        for uid in uids:
            try:
                imap.store(uid, '-FLAGS', '\\Seen')
            except Exception as exc:
                print('Failed to unmark', uid, exc)
        print('Done')
    finally:
        try:
            imap.logout()
        except Exception:
            pass


def unmark_since(days: int = 7, mailbox: str = 'INBOX'):
    if not IMAP_USER or not IMAP_PASSWORD:
        print('Please set IMAP_USER and IMAP_PASSWORD environment variables.')
        return
    imap = imaplib.IMAP4_SSL(IMAP_HOST)
    imap.login(IMAP_USER, IMAP_PASSWORD)
    imap.select(mailbox)
    try:
        cutoff = (datetime.datetime.utcnow() - datetime.timedelta(days=days)).strftime('%d-%b-%Y')
        # Search SINCE cutoff date (IMAP uses dd-Mon-YYYY)
        typ, data = imap.search(None, 'SINCE', cutoff)
        if typ != 'OK':
            print('Search failed', typ)
            return
        uids = data[0].split() if data and data[0] else []
        print(f'Found {len(uids)} messages since {cutoff}; removing \Seen flag...')
        for uid in uids:
            try:
                imap.store(uid, '-FLAGS', '\\Seen')
            except Exception as exc:
                print('Failed to unmark', uid, exc)
        print('Done')
    finally:
        try:
            imap.logout()
        except Exception:
            pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--all', action='store_true', help='Unmark all messages')
    ap.add_argument('--days', type=int, default=7, help='Unmark messages since N days ago')
    ap.add_argument('--mailbox', type=str, default='INBOX')
    args = ap.parse_args()

    if args.all:
        confirm = input('Are you sure you want to remove Seen from ALL messages? (yes/no): ').strip().lower()
        if confirm != 'yes':
            print('Aborted')
            return
        unmark_all(mailbox=args.mailbox)
    else:
        unmark_since(days=args.days, mailbox=args.mailbox)


if __name__ == '__main__':
    main()
