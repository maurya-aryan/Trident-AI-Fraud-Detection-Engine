"""
TRIDENT IMAP Poller Service - Async Background Task

Replaces subprocess.Popen + threading with clean async implementation.
Integrated with FastAPI lifespan for graceful startup/shutdown.
"""
import asyncio
import imaplib
import logging
import sys
from pathlib import Path
from typing import Optional
import requests

# Ensure project root is importable
ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from backend.config import settings
from ingest.imap_processor import IMAPProcessor
import core.token_store as token_store

logger = logging.getLogger(__name__)


class IMAPPoller:
    """
    Async IMAP poller that runs as a background task.

    Usage:
        poller = IMAPPoller()
        await poller.start()  # Begin polling in background
        # ... application runs ...
        await poller.stop()   # Graceful shutdown
    """

    def __init__(self):
        self.task: Optional[asyncio.Task] = None
        self.running = False
        self.imap: Optional[imaplib.IMAP4_SSL] = None
        self.processor = IMAPProcessor(settings.IMAP_PROCESSOR_FILE)

    async def start(self):
        """Start the poller background task."""
        if self.task and not self.task.done():
            logger.warning("Poller already running")
            return

        self.running = True
        self.task = asyncio.create_task(self._poll_loop())
        logger.info("IMAP poller started")

    async def stop(self):
        """Stop the poller and cleanup resources."""
        if not self.running:
            return

        logger.info("Stopping IMAP poller...")
        self.running = False

        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass

        if self.imap:
            try:
                self.imap.logout()
            except Exception:
                pass
            self.imap = None

        logger.info("IMAP poller stopped")

    def _connect_imap(self) -> imaplib.IMAP4_SSL:
        """
        Create authenticated IMAP connection using stored credentials or env vars.
        Supports Google OAuth2 and basic auth.
        """
        owner_id = "default"
        creds = token_store.get_credentials(owner_id)

        # Try OAuth2 first (Google)
        if creds:
            logger.info(f"Found stored credentials for {owner_id} ({creds['provider']})")

            if creds['provider'] == 'google':
                refresh_token = creds['secret']
                client_id = creds['meta'].get('client_id')
                client_secret = creds['meta'].get('client_secret')
                token_uri = creds['meta'].get('token_uri', 'https://oauth2.googleapis.com/token')

                if client_id and client_secret:
                    try:
                        data = {
                            'client_id': client_id,
                            'client_secret': client_secret,
                            'refresh_token': refresh_token,
                            'grant_type': 'refresh_token',
                        }
                        r = requests.post(token_uri, data=data)
                        r.raise_for_status()
                        access_token = r.json().get('access_token')

                        auth_str = f"user={creds['email']}\x01auth=Bearer {access_token}\x01\x01"

                        imap = imaplib.IMAP4_SSL(settings.IMAP_HOST)
                        imap.authenticate('XOAUTH2', lambda x: auth_str.encode())
                        return imap
                    except Exception as e:
                        logger.error(f"XOAUTH2 authentication failed: {e}")

            elif creds['provider'] == 'basic':
                host = creds['meta'].get('host', settings.IMAP_HOST)
                imap = imaplib.IMAP4_SSL(host)
                imap.login(creds['email'], creds['secret'])
                return imap

        # Fallback to environment variables
        if settings.IMAP_USER and settings.IMAP_PASSWORD:
            logger.info(f"Using IMAP credentials from environment")
            imap = imaplib.IMAP4_SSL(settings.IMAP_HOST)
            imap.login(settings.IMAP_USER, settings.IMAP_PASSWORD)
            return imap

        raise ValueError("No valid IMAP credentials found in token_store or environment")

    async def _poll_loop(self):
        """
        Main polling loop - runs continuously until stopped.
        Handles connection drops and errors with automatic retry.
        """
        logger.info(f"Polling IMAP server every {settings.IMAP_POLL_INTERVAL}s")

        while self.running:
            try:
                # Establish connection if needed
                if self.imap is None:
                    try:
                        logger.info(f"Connecting to IMAP {settings.IMAP_HOST}")
                        self.imap = self._connect_imap()
                        logger.info(f"Connected to {settings.IMAP_HOST}")
                    except Exception as exc:
                        logger.error(f"Connection failed: {exc}")
                        await asyncio.sleep(settings.IMAP_POLL_INTERVAL)
                        continue

                # Check for new messages
                await self._check_inbox()

                # Sleep before next poll
                await asyncio.sleep(settings.IMAP_POLL_INTERVAL)

            except asyncio.CancelledError:
                logger.info("Poller task cancelled")
                break

            except (imaplib.IMAP4.abort, imaplib.IMAP4.error, OSError) as exc:
                # Connection lost - reconnect on next iteration
                logger.error(f"IMAP connection lost: {exc}. Will reconnect...")
                try:
                    self.imap.logout()
                except Exception:
                    pass
                self.imap = None
                await asyncio.sleep(settings.IMAP_POLL_INTERVAL)

            except Exception as exc:
                # Unexpected error - log and continue
                logger.exception(f"Unexpected error in poll loop: {exc}")
                await asyncio.sleep(settings.IMAP_POLL_INTERVAL)

    async def _check_inbox(self):
        """Check INBOX for UNSEEN messages and process them."""
        if not self.imap:
            return

        # Re-select INBOX to refresh message count
        self.imap.select("INBOX")
        logger.debug("Checking for UNSEEN messages...")

        typ, data = self.imap.search(None, 'UNSEEN')
        if typ != 'OK':
            logger.error(f"IMAP search failed: {typ}")
            return

        uids = data[0].split() if data and data[0] else []

        if uids:
            logger.info(f"Found {len(uids)} new messages")
        else:
            logger.debug("No new messages")
            return

        for uid in uids:
            try:
                typ, msg_data = self.imap.fetch(uid, '(RFC822)')
                if typ != 'OK' or not msg_data:
                    continue

                raw = msg_data[0][1]
                signal = self.processor.process_email(uid, raw)

                if signal is None:
                    logger.debug(f"Message {uid} already processed")
                    continue

                # Build payload for /detect endpoint
                payload = {
                    "email_text": signal.parsed_text,
                    "email_subject": signal.subject,
                    "sender": signal.sender,
                    "timestamp": signal.timestamp,
                    "metadata": signal.metadata,
                }

                logger.info(f"Processing: {signal.subject} from {signal.sender}")

                # Post to TRIDENT detection endpoint
                result = await self._post_detect(payload)

                if result:
                    band = result.get("risk_band")
                    score = result.get("risk_score", 0)

                    # Push alert to /alerts endpoint
                    alert = {
                        "subject": signal.subject,
                        "sender": signal.sender,
                        "email_text": signal.parsed_text or "",
                        "snippet": (signal.parsed_text or "")[:240],
                        "risk_band": band,
                        "risk_score": score,
                        "trident_result": result,
                    }

                    await self._push_alert(alert)
                    logger.info(f"Alert: {band} ({score:.1f}) - {signal.subject}")

                # Mark as seen if configured
                if settings.IMAP_MARK_SEEN:
                    self.imap.uid('STORE', uid, '+FLAGS', '\\Seen')

            except Exception as exc:
                logger.error(f"Failed to process message {uid}: {exc}")

    async def _post_detect(self, payload: dict) -> Optional[dict]:
        """Post email to TRIDENT detection endpoint (blocking call in executor)."""
        def _post():
            try:
                resp = requests.post(
                    settings.TRIDENT_URL,
                    json=payload,
                    timeout=90
                )
                resp.raise_for_status()
                return resp.json()
            except Exception as exc:
                logger.error(f"Error posting to /detect: {exc}")
                return None

        # Run blocking HTTP request in thread pool
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _post)

    async def _push_alert(self, alert: dict):
        """Push alert to /alerts endpoint (blocking call in executor)."""
        def _push():
            try:
                requests.post(
                    settings.ALERTS_URL,
                    json=alert,
                    timeout=6
                )
            except Exception as exc:
                logger.error(f"Error pushing alert: {exc}")

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, _push)


# Global poller instance
_poller: Optional[IMAPPoller] = None


def get_poller() -> IMAPPoller:
    """Get or create the global poller instance."""
    global _poller
    if _poller is None:
        _poller = IMAPPoller()
    return _poller
