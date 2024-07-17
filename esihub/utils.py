import json
import os
from typing import Any, Dict

from .core.logger import get_logger

logger = get_logger(__name__)


def load_swagger_spec(file_name: str = "swagger.json") -> Dict[str, Any]:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, file_name)
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"Swagger file not found: {file_path}")
        raise
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON in Swagger file: {file_path}")
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


def generate_cache_key(method: str, url: str, params: Dict[str, Any]) -> str:
    return f"{method}:{url}:{json.dumps(params, sort_keys=True)}"
