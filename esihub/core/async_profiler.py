import time
from functools import wraps
from typing import Callable, Dict, List

from .logger import esihub_logger


def profile(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        result = await func(*args, **kwargs)
        end_time = time.time()

        execution_time = end_time - start_time
        esihub_logger.info(
            f"Function {func.__name__} took {execution_time:.4f} seconds to execute"
        )

        return result

    return wrapper


class ESIHubAsyncProfiler:
    def __init__(self):
        self.function_times: Dict[str, List[float]] = {}

    async def profile_coroutine(self, coroutine):
        start_time = time.time()
        result = await coroutine
        end_time = time.time()

        execution_time = end_time - start_time
        coroutine_name = coroutine.__name__

        if coroutine_name not in self.function_times:
            self.function_times[coroutine_name] = []

        self.function_times[coroutine_name].append(execution_time)

        return result

    def print_stats(self):
        for func_name, times in self.function_times.items():
            avg_time = sum(times) / len(times)
            min_time = min(times)
            max_time = max(times)

            esihub_logger.info(f"Function: {func_name}")
            esihub_logger.info(f"  Calls: {len(times)}")
            esihub_logger.info(f"  Average time: {avg_time:.4f} seconds")
            esihub_logger.info(f"  Min time: {min_time:.4f} seconds")
            esihub_logger.info(f"  Max time: {max_time:.4f} seconds")

    async def run_profiled(self, func: Callable, *args, **kwargs):
        return await self.profile_coroutine(func(*args, **kwargs))
