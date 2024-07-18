from typing import Dict, Any

from .logger import esihub_logger
from ..exceptions import (
    ESIHubAuthenticationError,
    ESIHubRateLimitError,
    ESIHubClientError,
    ESIHubServerError,
    ESIHubError,
)


class ESIHubErrorHandler:
    @staticmethod
    async def handle_error(status_code: int, response_data: Dict[str, Any]) -> None:
        error_message = response_data.get("error", "Unknown error")
        if 400 <= status_code < 500:
            if status_code == 401:
                raise ESIHubAuthenticationError(
                    f"Authentication failed: {error_message}",
                    status_code,
                    response_data,
                )
            elif status_code == 403:
                raise ESIHubAuthenticationError(
                    f"Insufficient permissions: {error_message}",
                    status_code,
                    response_data,
                )
            elif status_code == 420:
                raise ESIHubRateLimitError(
                    f"Rate limit exceeded: {error_message}", status_code, response_data
                )
            else:
                raise ESIHubClientError(
                    f"Client error: {error_message}", status_code, response_data
                )
        elif status_code >= 500:
            raise ESIHubServerError(
                f"Server error: {error_message}", status_code, response_data
            )
        else:
            raise ESIHubError(
                f"Unexpected error: {error_message}", status_code, response_data
            )

    @staticmethod
    def log_error(error: Exception) -> None:
        if isinstance(error, ESIHubError):
            esihub_logger.error(
                f"{error.__class__.__name__}: {str(error)}",
                extra={"status_code": error.status_code, "details": error.details},
            )
        else:
            esihub_logger.error(f"Unexpected error: {str(error)}", exc_info=True)
