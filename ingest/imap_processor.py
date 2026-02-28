import os
from typing import Optional
from ingest.models import Signal
from ingest.imap_adapter import parse_email_bytes

class IMAPProcessor:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.processed_uids = set()
        self.load_processed_uids()

    def load_processed_uids(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r') as f:
                self.processed_uids = set(f.read().splitlines())

    def save_processed_uids(self):
        with open(self.file_path, 'w') as f:
            f.write('\n'.join(self.processed_uids))

    def process_email(self, uid: bytes, raw_bytes: bytes) -> Optional[Signal]:
        uid_str = uid.decode() if isinstance(uid, bytes) else str(uid)
        if uid_str in self.processed_uids:
            return None
        signal = parse_email_bytes(raw_bytes)
        self.processed_uids.add(uid_str)
        self.save_processed_uids()
        return signal
