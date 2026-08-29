"""
Multimodal Context Fusion Engine for Smart Interaction Hub
"""
from typing import Dict, Any, List
import time

class MultimodalContextFusionEngine:
    def __init__(self, ttl_seconds: int = 3600):
        self.ttl = ttl_seconds
        self.sessions: Dict[str, List[Dict[str, Any]]] = {}

    def ingest_event(self, session_id: str, modality: str, data: Dict[str, Any]) -> Dict[str, Any]:
        if session_id not in self.sessions:
            self.sessions[session_id] = []
        entry = {
            "modality": modality,
            "data": data,
            "timestamp": time.time()
        }
        self.sessions[session_id].append(entry)
        return entry

    def fuse_context(self, session_id: str) -> Dict[str, Any]:
        events = self.sessions.get(session_id, [])
        now = time.time()
        active_events = [e for e in events if (now - e["timestamp"]) <= self.ttl]
        modalities = list(set(e["modality"] for e in active_events))
        return {
            "session_id": session_id,
            "active_event_count": len(active_events),
            "modalities_present": modalities,
            "fused_at": now
        }
