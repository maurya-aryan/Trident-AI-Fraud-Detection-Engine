"""Simple IMAP connectivity test helper.

Usage:
  Set the environment variables IMAP_HOST, IMAP_USER, IMAP_PASSWORD in your
  PowerShell session, activate the venv, then run:

    python scripts/test_imap.py

This script logs into the IMAP server, lists a few mailboxes, and prints the
UNSEEN message count for INBOX.
"""
import os
import imaplib
import sys


def main():
    host = os.environ.get('IMAP_HOST', 'imap.gmail.com')
    user = os.environ.get('IMAP_USER')
    pw = os.environ.get('IMAP_PASSWORD')

    if not user or not pw:
        print('Please set IMAP_USER and IMAP_PASSWORD in this terminal session.')
        return 2

    try:
        print(f'Connecting to IMAP host {host} as {user}...')
        M = imaplib.IMAP4_SSL(host)
        M.login(user, pw)
        print('IMAP login OK')
        typ, boxes = M.list()
        print('Mailboxes sample:', boxes[:5])
        M.select('INBOX')
        typ, data = M.search(None, 'UNSEEN')
        unseen = data[0].split() if data and data[0] else []
        print('UNSEEN count in INBOX:', len(unseen))
        M.logout()
        return 0
    except Exception as exc:
        print('IMAP/test error:', exc)
        return 3


if __name__ == '__main__':
    sys.exit(main())
