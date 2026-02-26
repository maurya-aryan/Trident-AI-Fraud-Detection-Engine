"""Base adapter interface and a tiny webhook adapter example.

Adapters should implement `parse_and_enqueue` which returns a `Signal`.
In a complete system the adapter would also enqueue the Signal into the chosen
broker (Redis/Celery/RQ). For the scaffold we return the Signal so the caller
or a small wrapper can perform the enqueue operation.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, Any

from .models import Signal


class BaseAdapter(ABC):
    @abstractmethod
    def parse_and_enqueue(self, raw_event: Dict[str, Any]) -> Signal:
        """Parse a raw_event and (in a full system) enqueue it for processing.

        Returns the normalized Signal instance.
        """
        raise NotImplementedError()


class WebhookAdapter(BaseAdapter):
    """Simple webhook adapter that normalises common webhook fields.

    This is intentionally minimal: connectors should subclass and perform
    any validation (signature checks, auth) prior to calling this.
    """

    def parse_and_enqueue(self, raw_event: Dict[str, Any]) -> Signal:
        # Lightweight normalisation
        source = raw_event.get("source", "webhook")
        signal = Signal.from_webhook(source=source, payload=raw_event)
        # In production, enqueue the signal to a broker here.
        return signal
