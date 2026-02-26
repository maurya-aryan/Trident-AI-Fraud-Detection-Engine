"""Data contract for ingestion: Signal.

This model is intentionally lightweight and serialisable. It represents a
normalized event extracted from various sources (email, WhatsApp, SMS, webhooks
and others) that can be consumed by the TRIDENT pipeline.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import uuid

from pydantic import BaseModel, Field


class Signal(BaseModel):
    """Normalized signal used across ingestion adapters and workers.

    Fields:
      id: unique identifier for the signal (UUID string)
      source: short source name, e.g. 'email', 'whatsapp', 'slack', 'webhook'
      raw_payload: original event payload (kept for auditing)
      parsed_text: extracted textual content to feed into detectors
      subject: optional subject/title (emails)
      sender: canonical sender identifier (email address or phone)
      recipients: list of recipient identifiers
      attachments: list of small dicts describing attachments
      timestamp: ISO timestamp of the original event (UTC)
      metadata: arbitrary dict for connector-specific fields
    """

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source: str
    raw_payload: Optional[Dict[str, Any]] = None
    parsed_text: Optional[str] = None
    subject: Optional[str] = None
    sender: Optional[str] = None
    recipients: List[str] = Field(default_factory=list)
    attachments: List[Dict[str, Any]] = Field(default_factory=list)
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def to_trident_input(self) -> Dict[str, Any]:
        """Create a dict compatible with `core.data_models.FraudSignal`.

        Note: attachments are left as-is; worker will decide how to store or
        pass paths to the scanner. This keeps ingestion lightweight.
        """
        return {
            "email_text": self.parsed_text,
            "email_subject": self.subject,
            "attachment_path": None,
            "url": self.metadata.get("url"),
            "voice_path": self.metadata.get("voice_path"),
            "timestamp": self.timestamp,
            "sender": self.sender,
            "metadata": self.metadata,
        }

    @classmethod
    def from_webhook(cls, source: str, payload: Dict[str, Any]) -> "Signal":
        """Small helper to normalise common webhook payloads into Signal.

        This method is intentionally permissive: a connector should adapt
        fields as required and fill metadata for later enrichment.
        """
        return cls(
            source=source,
            raw_payload=payload,
            parsed_text=payload.get("text") or payload.get("message") or payload.get("body"),
            subject=payload.get("subject"),
            sender=payload.get("from") or payload.get("sender") or payload.get("phone"),
            recipients=payload.get("to") or payload.get("recipients") or [],
            attachments=payload.get("attachments") or [],
            metadata=payload.get("metadata") or {},
        )
