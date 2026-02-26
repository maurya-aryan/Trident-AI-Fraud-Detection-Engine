# TRIDENT — Ingestion Architecture & Data Contract

This document summarises the proposed ingestion architecture, the `Signal`
data contract, and practical recommendations for taking TRIDENT from a
single-process prototype to an automated multi-source detection platform.

## Goals

- Accept events from email, WhatsApp (Twilio), SMS, Slack, webhooks, and voice
- Normalise events into a single canonical `Signal` that workers can process
- Decouple ingestion from processing using a broker (Redis/Celery or RabbitMQ)
- Persist signals and results for audit, investigation, and retraining

## Data contract — `Signal`

Key fields (implemented in `ingest.models.Signal`):

- `id` (str): UUID string for the signal
- `source` (str): e.g. `email`, `whatsapp`, `slack`, `webhook`
- `raw_payload` (dict | optional): original incoming payload saved for audits
- `parsed_text` (str | optional): main extracted textual content for detectors
- `subject` (str | optional): e.g. email subject or headline
- `sender` (str | optional): canonical sender (email address or phone number)
- `recipients` (list[str]): recipient identifiers
- `attachments` (list[dict]): small dicts describing attachments (filename, mime, size)
- `timestamp` (ISO str): event timestamp in UTC
- `metadata` (dict): connector-specific keys (url, message_sid, thread_id)

The `Signal.to_trident_input()` helper prepares a minimal dict compatible
with `core.data_models.FraudSignal` so the worker can call `TRIDENT.detect_fraud`.

## High level architecture

1. Ingest adapters (webhooks, pollers) normalise events into `Signal` and
   enqueue to a broker. Adapters handle authentication and signature checks.
2. Broker (Redis + RQ/Celery or RabbitMQ + Celery) queues work items.
3. Worker processes dequeue Signals, optionally persist the Signal, call
   `TRIDENT.detect_fraud` (or `TRIDENT.process_signal`), persist results and
   trigger alerts/actions based on risk band.
4. Campaign graph state can be persisted in Postgres or Redis to make
   correlation robust across worker restarts.

## Sync vs Async

- Use synchronous HTTP webhooks for inbound connectors (Twilio, Slack). Webhooks
  should perform basic validation and acknowledge quickly (200/202).
- Use an async worker model (broker + worker) to run heavy detectors (XGBoost,
  virus scanning, model downloads) outside the request lifecycle.

## Broker & Persistence recommendations

- Broker: Redis + RQ (simple) or Celery (more features). Redis is lightweight
  for local dev and scales well for low-to-medium throughput.
- Persistence: Postgres for signals and results; use SQLAlchemy + Alembic.
- Attachments: store binaries on disk (or S3) and persist paths in DB.

## Security, privacy & compliance

- Encrypt attachments at rest if storing sensitive files.
- Redact PII in logs; store raw payloads in a restricted store with limited
  retention.
- Provide configuration toggles to disable third-party enrichers.

## Next practical steps (MVP)

1. Wire a webhook receiver (FastAPI router) that uses `ingest.adapter.WebhookAdapter`.
2. Add Redis + RQ and a tiny `workers/processor.py` that receives Signals and
   calls the TRIDENT pipeline. Persist results in a simple JSON store or Postgres.
3. Implement Twilio WhatsApp sandbox notes and a testing guide (ngrok).

## Example minimal sequence

1. Twilio webhook → `POST /ingest/webhook` → adapter.parse_and_enqueue() → enqueue
2. Worker dequeues → calls `TRIDENT.detect_fraud` → persist result and alert

---

See `ingest/models.py` and `ingest/adapter.py` for the initial scaffolding.
