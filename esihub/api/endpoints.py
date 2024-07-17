from typing import Any, Callable, Coroutine, Dict

from ..core.logger import get_logger
from ..utils import parse_path_params, replace_path_params

logger = get_logger(__name__)


def generate_endpoint_method(
    client, method: str, path: str, operation_id: str
) -> Callable[..., Coroutine[Any, Any, Dict[str, Any]]]:
    path_params = parse_path_params(path)

    async def endpoint_method(**kwargs) -> Dict[str, Any]:
        logger.debug(f"Calling endpoint: {operation_id}")
        path_args = {k: kwargs.pop(k) for k in path_params if k in kwargs}
        formatted_path = replace_path_params(path, **path_args)
        return await client.request(method=method, path=formatted_path, **kwargs)

    endpoint_method.__name__ = operation_id
    endpoint_method.__doc__ = f"{method.upper()} {path}"

    return endpoint_method


def generate_endpoints(client):
    for path, methods in client.swagger_spec["paths"].items():
        for method, details in methods.items():
            if "operationId" in details:
                setattr(
                    client,
                    details["operationId"],
                    generate_endpoint_method(
                        client, method, path, details["operationId"]
                    ),
                )
