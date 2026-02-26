"""IMAP helper: minimal parsing of raw email bytes into a Signal.

This module intentionally uses only the stdlib email parser so the repo
doesn't require extra heavy dependencies for basic local testing.
"""
from __future__ import annotations

from email import policy
from email.parser import BytesParser
from typing import Any, Dict, List

from ingest.models import Signal


def parse_email_bytes(raw_bytes: bytes) -> Signal:
    """Parse RFC822 bytes into a normalized `Signal`.

    The Signal will include a best-effort `parsed_text`, `subject`, `sender`,
    `recipients` and minimal `attachments` metadata (filename + size).
    """
    msg = BytesParser(policy=policy.default).parsebytes(raw_bytes)

    # Subject / addresses
    subject = msg.get("subject")
    sender = msg.get("from")
    to = msg.get_all("to", []) or []
    recipients: List[str] = []
    for r in to:
        recipients.extend([addr.strip() for addr in r.split(",") if addr.strip()])

    # Extract text/plain if available else fallback to html (stripped)
    parsed_text = None
    if msg.is_multipart():
        parts = []
        attachments: List[Dict[str, Any]] = []
        for part in msg.walk():
            ctype = part.get_content_type()
            disp = str(part.get_content_disposition() or "")
            if ctype == "text/plain" and disp != "attachment":
                try:
                    parts.append(part.get_content())
                except Exception:
                    pass
            elif disp == "attachment" or part.get_filename():
                fn = part.get_filename()
                payload = part.get_payload(decode=True) or b""
                attachments.append({"filename": fn, "size": len(payload)})
        parsed_text = "\n\n".join(parts) if parts else None
    else:
        try:
            parsed_text = msg.get_content()
        except Exception:
            parsed_text = None
        attachments = []

    sig = Signal(
        source="email",
        raw_payload={"headers": dict(msg.items())},
        parsed_text=(parsed_text or "").strip(),
        subject=subject,
        sender=sender,
        recipients=recipients,
        attachments=attachments,
        metadata={"message_id": msg.get("message-id")},
    )
    return sig
