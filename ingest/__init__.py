"""Ingest package: adapters and models for normalising external events into TRIDENT Signals.

This package provides a small, framework-agnostic Signal data contract and a base
adapter interface to begin wiring webhooks, pollers and other ingestion adapters.
"""

from .models import Signal
from .adapter import BaseAdapter, WebhookAdapter

__all__ = ["Signal", "BaseAdapter", "WebhookAdapter"]
