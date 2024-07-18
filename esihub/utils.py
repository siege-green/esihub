import asyncio
import json
import os
from functools import wraps
from typing import Dict, Any, Callable

from .core.logger import esihub_logger


def load_swagger_spec(file_path: str = None) -> Dict[str, Any]:
    if file_path is None:
        file_path = os.path.join(os.path.dirname(__file__), "swagger.json")

    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        esihub_logger.error(f"Swagger spec file not found: {file_path}")
        raise
    except json.JSONDecodeError:
        esihub_logger.error(f"Invalid JSON in Swagger spec file: {file_path}")
        raise


def parse_path_params(path: str) -> Dict[str, Any]:
    params = {}
    parts = path.split("/")
    for part in parts:
        if part.startswith("{") and part.endswith("}"):
            param_name = part[1:-1]
            params[param_name] = None
    return params


def replace_path_params(path: str, **kwargs: Any) -> str:
    for key, value in kwargs.items():
        path = path.replace(f"{{{key}}}", str(value))
    return path


def retry_with_exponential_backoff(
    max_retries: int = 3, base_delay: float = 1, max_delay: float = 60
):
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any):
            retries = 0
            while True:
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    retries += 1
                    if retries > max_retries:
                        raise
                    delay = min(base_delay * (2 ** (retries - 1)), max_delay)
                    esihub_logger.warning(
                        f"Retry {retries}/{max_retries} after {delay:.2f}s. Error: {str(e)}"
                    )
                    await asyncio.sleep(delay)

        return wrapper

    return decorator


def validate_url(url: str) -> bool:
    from urllib.parse import urlparse

    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception as e:
        esihub_logger.error(f"Error validating URL: {str(e)}")
        return False


def validate_input(input_str: str, pattern: str) -> bool:
    import re

    return bool(re.match(pattern, input_str))
