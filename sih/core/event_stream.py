"""
High-Throughput Event Streaming Bus
"""
from typing import Callable, Dict, List, Any
import asyncio

class StreamEventBus:
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = {}

    def subscribe(self, topic: str, handler: Callable):
        if topic not in self.subscribers:
            self.subscribers[topic] = []
        self.subscribers[topic].append(handler)

    async def publish(self, topic: str, payload: Dict[str, Any]):
        handlers = self.subscribers.get(topic, [])
        for h in handlers:
            if asyncio.iscoroutinefunction(h):
                await h(payload)
            else:
                h(payload)
