import asyncio
from typing import Any, Callable, Dict, List


class ESIHubEventSystem:
    def __init__(self):
        self.listeners: Dict[str, List[Callable]] = {}

    def on(self, event: str):
        def decorator(func: Callable):
            if event not in self.listeners:
                self.listeners[event] = []
            self.listeners[event].append(func)
            return func

        return decorator

    async def emit(self, event: str, **kwargs: Any):
        if event in self.listeners:
            await asyncio.gather(
                *(listener(**kwargs) for listener in self.listeners[event])
            )

    def remove(self, event: str, listener: Callable):
        if event in self.listeners and listener in self.listeners[event]:
            self.listeners[event].remove(listener)
