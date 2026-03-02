"""
Shared Event Bus
Simple event bus for service communication
"""

from typing import Callable, Dict, List
import logging

logger = logging.getLogger(__name__)

class EventBus:
    """Simple in-memory event bus"""
    
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = {}
    
    def subscribe(self, event_type: str, handler: Callable):
        """Subscribe to an event type"""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(handler)
    
    def publish(self, event_type: str, data: dict):
        """Publish an event"""
        if event_type in self.subscribers:
            for handler in self.subscribers[event_type]:
                try:
                    handler(data)
                except Exception as e:
                    logger.error(f"Error in event handler: {e}")

# Global event bus instance
event_bus = EventBus()
