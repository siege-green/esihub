import asyncio
from typing import Callable, Awaitable, Any, List

from .logger import esihub_logger


class ESIHubBackgroundTaskManager:
    def __init__(self):
        self.tasks: List[asyncio.Task] = []
        self.queue: asyncio.PriorityQueue = asyncio.PriorityQueue()
        self.running = False

    async def start(self):
        self.running = True
        self.process_queue_task = asyncio.create_task(self._process_queue())

    async def stop(self):
        self.running = False
        # Cancel all running tasks
        for task in self.tasks:
            task.cancel()
        # Await their completion to ensure they are properly cleaned up
        await asyncio.gather(*self.tasks, return_exceptions=True)
        # Ensure process_queue_task is also cancelled and awaited
        self.process_queue_task.cancel()
        await asyncio.gather(self.process_queue_task, return_exceptions=True)

    async def add_task(
        self,
        coroutine: Callable[..., Awaitable[Any]],
        *args,
        priority: int = 0,
        **kwargs,
    ):
        await self.queue.put((-priority, coroutine, args, kwargs))

    async def _process_queue(self):
        while self.running:
            try:
                _, coroutine, args, kwargs = await self.queue.get()
                task = asyncio.create_task(coroutine(*args, **kwargs))
                self.tasks.append(task)
                task.add_done_callback(self._task_done)
            except asyncio.CancelledError:
                break
            except Exception as e:
                esihub_logger.error(f"Error processing background task: {str(e)}")
        # Cleanup when stopping
        while not self.queue.empty():
            try:
                self.queue.get_nowait()
            except asyncio.QueueEmpty:
                break

    def _task_done(self, task: asyncio.Task):
        if task in self.tasks:
            self.tasks.remove(task)
        try:
            task.result()
        except asyncio.CancelledError:
            pass
        except Exception as e:
            esihub_logger.error(f"Background task failed: {str(e)}")
