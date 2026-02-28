import os
from core.data_models import Signal

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
        if uid in self.processed_uids:
            return None
        signal = parse_email_bytes(raw_bytes)
        self.processed_uids.add(uid)
        self.save_processed_uids()
        return signal
