"""Simple CLI to label collected IMAP emails for training.

Usage:
  python scripts/label_emails.py

This loads `data/imap_raw_emails.csv` and writes `data/labeled_emails.csv` with
columns: text,label,source. It will skip rows already labelled.
"""
from __future__ import annotations

import csv
from pathlib import Path
import argparse


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--input', default='data/imap_raw_emails.csv')
    ap.add_argument('--output', default='data/labeled_emails.csv')
    args = ap.parse_args()

    inp = Path(args.input)
    out = Path(args.output)
    if not inp.exists():
        print('No collected IMAP emails found at', inp)
        return

    # load existing labeled
    labeled_ids = set()
    if out.exists():
        try:
            with out.open('r', encoding='utf-8', newline='') as f:
                r = csv.DictReader(f)
                for row in r:
                    labeled_ids.add(row.get('id') or '')
        except Exception:
            labeled_ids = set()

    rows = []
    with inp.open('r', encoding='utf-8', newline='') as f:
        r = csv.DictReader(f)
        for row in r:
            rows.append(row)

    to_append = []
    for row in rows:
        rid = row.get('id') or ''
        if rid in labeled_ids:
            continue
        print('\n---')
        print('From:', row.get('sender'))
        print('Subject:', row.get('subject'))
        print('Timestamp:', row.get('timestamp'))
        print('\nSnippet:\n')
        text = row.get('text') or ''
        print(text[:1000])
        ans = input('\nLabel this message as phishing? (y = phishing, n = legit, s = skip) [s]: ').strip().lower()
        if ans == 'y':
            label = 1
        elif ans == 'n':
            label = 0
        else:
            print('Skipping')
            continue
        to_append.append({'id': rid, 'text': text, 'label': label, 'source': 'imap'})

    if to_append:
        out.parent.mkdir(parents=True, exist_ok=True)
        write_header = not out.exists()
        with out.open('a', encoding='utf-8', newline='') as f:
            w = csv.DictWriter(f, fieldnames=['id', 'text', 'label', 'source'])
            if write_header:
                w.writeheader()
            for r in to_append:
                w.writerow(r)
        print(f'Appended {len(to_append)} labelled rows to {out}')
    else:
        print('No new labels provided')


if __name__ == '__main__':
    main()
