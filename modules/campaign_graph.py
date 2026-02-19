"""
Module #8: Campaign Graph
Uses NetworkX to correlate signals and detect coordinated fraud campaigns.
"""
import logging
import re
from datetime import datetime, timezone
from typing import Dict, List, Optional
from urllib.parse import urlparse

import networkx as nx

logger = logging.getLogger(__name__)


def _extract_domain(value: str) -> Optional[str]:
    """Extract domain from a URL or email address."""
    if not value:
        return None
    # Email address
    if "@" in value and "://" not in value:
        return value.split("@")[-1].lower().strip()
    # URL
    try:
        parsed = urlparse(value if "://" in value else "http://" + value)
        return parsed.hostname.lower() if parsed.hostname else None
    except Exception:
        return None


class CampaignGraph:
    """
    Builds a graph of entities (domains, senders, file hashes, caller IDs)
    to detect coordinated fraud campaigns.
    """

    def __init__(self):
        self.graph = nx.Graph()
        self.signals: List[Dict] = []
        self._entity_registry: Dict[str, List[str]] = {}  # entity → [signal_ids]

    def reset(self) -> None:
        """Clear all signals and graph state."""
        self.graph = nx.Graph()
        self.signals = []
        self._entity_registry = {}

    def add_signal(
        self,
        signal_type: str,
        data: Dict,
        timestamp: Optional[str] = None,
    ) -> str:
        """
        Add a fraud signal to the graph.

        Args:
            signal_type: 'email' | 'url' | 'voice' | 'attachment' | 'generic'
            data: dict with relevant fields (domain, sender, url, filename, hash, etc.)
            timestamp: ISO timestamp string

        Returns:
            signal_id: unique identifier for this signal
        """
        ts = timestamp or datetime.now(timezone.utc).isoformat()
        signal_id = f"{signal_type}_{len(self.signals)}"

        signal = {
            "signal_id": signal_id,
            "signal_type": signal_type,
            "timestamp": ts,
            "data": data,
            "entities": [],
        }

        # Add signal node
        self.graph.add_node(signal_id, type="signal", signal_type=signal_type, timestamp=ts)

        # Extract entities and add to graph
        entities = self._extract_entities(signal_type, data)

        for entity_type, entity_value in entities:
            entity_id = f"{entity_type}:{entity_value}"
            signal["entities"].append(entity_id)

            # Add entity node
            if not self.graph.has_node(entity_id):
                self.graph.add_node(entity_id, type="entity", entity_type=entity_type, value=entity_value)

            # Edge: signal → entity
            self.graph.add_edge(signal_id, entity_id, relation="has_entity")

            # Register entity
            if entity_id not in self._entity_registry:
                self._entity_registry[entity_id] = []
            self._entity_registry[entity_id].append(signal_id)

            # Create edges between signals that share the same entity
            for existing_signal in self._entity_registry[entity_id]:
                if existing_signal != signal_id:
                    self.graph.add_edge(
                        existing_signal,
                        signal_id,
                        relation="shared_entity",
                        entity=entity_id,
                    )

        self.signals.append(signal)
        logger.debug(f"Added signal {signal_id} with entities: {entities}")
        return signal_id

    def _extract_entities(self, signal_type: str, data: Dict) -> List[tuple]:
        """Extract (entity_type, entity_value) pairs from signal data."""
        entities = []

        # Domain extraction
        for field in ("domain", "url", "sender", "email"):
            val = data.get(field)
            if val:
                domain = _extract_domain(val) if field != "domain" else val.lower().strip()
                if domain:
                    entities.append(("domain", domain))

        # Sender
        sender = data.get("sender", "")
        if sender and "@" in sender:
            entities.append(("sender", sender.lower().strip()))

        # File hash
        for field in ("hash", "md5", "sha256"):
            val = data.get(field)
            if val:
                entities.append(("file_hash", str(val).lower()))

        # Caller ID
        caller = data.get("caller_id") or data.get("phone")
        if caller:
            entities.append(("caller_id", str(caller).strip()))

        # IP address
        ip = data.get("ip") or data.get("ip_address")
        if ip:
            entities.append(("ip", str(ip).strip()))

        # Extract domains from free text
        text = data.get("text", "") or data.get("email_text", "")
        if text:
            found_domains = re.findall(r"\b(?:[a-z0-9\-]+\.)+(?:com|net|org|xyz|io|co|uk|info|biz)\b", text.lower())
            for d in set(found_domains):
                entities.append(("domain_in_text", d))

        return list(set(entities))  # deduplicate

    def correlate(self) -> Dict:
        """
        Analyse the current graph to detect coordinated campaigns.

        Returns:
            {
                'is_coordinated': bool,
                'connected_components': int,
                'signal_count': int,
                'timeline': [{signal_id, signal_type, timestamp, entities}],
                'connected_entities': [entity_value, ...],
                'correlation_strength': 0-1,
                'campaign_summary': str
            }
        """
        if not self.signals:
            return {
                "is_coordinated": False,
                "connected_components": 0,
                "signal_count": 0,
                "timeline": [],
                "connected_entities": [],
                "correlation_strength": 0.0,
                "campaign_summary": "No signals analysed yet.",
            }

        signal_nodes = [n for n, d in self.graph.nodes(data=True) if d.get("type") == "signal"]
        entity_nodes = [n for n, d in self.graph.nodes(data=True) if d.get("type") == "entity"]

        # Find connected components among signal nodes
        signal_subgraph = self.graph.subgraph(signal_nodes)
        components = list(nx.connected_components(signal_subgraph))
        num_components = len(components)

        # Determine if signals are coordinated:
        # Coordinated = all signals connected into one component
        max_component_size = max(len(c) for c in components) if components else 0
        is_coordinated = max_component_size == len(signal_nodes) and len(signal_nodes) > 1

        # Correlation strength = largest component / total signals
        correlation_strength = round(max_component_size / max(len(signal_nodes), 1), 2)

        # Timeline (sorted by timestamp)
        timeline = []
        for sig in sorted(self.signals, key=lambda s: s["timestamp"]):
            timeline.append({
                "signal_id": sig["signal_id"],
                "signal_type": sig["signal_type"],
                "timestamp": sig["timestamp"],
                "entities": sig["entities"],
            })

        # Shared entities
        shared_entities = [
            self.graph.nodes[e]["value"]
            for e in entity_nodes
            if len(self._entity_registry.get(e, [])) > 1
        ]

        # Campaign summary
        if is_coordinated:
            summary = (
                f"COORDINATED CAMPAIGN DETECTED: {len(signal_nodes)} signals share "
                f"{len(shared_entities)} common entities ({', '.join(str(e) for e in shared_entities[:5])})."
            )
        else:
            summary = (
                f"{len(signal_nodes)} independent signals detected across "
                f"{num_components} disconnected components."
            )

        return {
            "is_coordinated": is_coordinated,
            "connected_components": num_components,
            "signal_count": len(signal_nodes),
            "timeline": timeline,
            "connected_entities": shared_entities,
            "correlation_strength": correlation_strength,
            "campaign_summary": summary,
        }
