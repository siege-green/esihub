import asyncio
from typing import Any, Callable, Dict, List

from ..core.logger import get_logger


class ESIEventSystem:
    def __init__(self):
        self.listeners: Dict[str, List[Callable]] = {}
        self.logger = get_logger(__name__)

    def on(self, event: str) -> Callable:
        def decorator(callback: Callable) -> Callable:
            if event not in self.listeners:
                self.listeners[event] = []
            self.listeners[event].append(callback)
            self.logger.debug(f"Registered listener for event: {event}")
            return callback

        return decorator

    async def emit(self, event: str, **kwargs: Any) -> None:
        self.logger.debug(f"Emitting event: {event}")
        if event in self.listeners:
            for callback in self.listeners[event]:
                if asyncio.iscoroutinefunction(callback):
                    await callback(**kwargs)
                else:
                    callback(**kwargs)
