from typing import Any, Dict

from .logger import esihub_logger
from ..models import ESIHubResponse


class ESIHubDryRunMode:
    def __init__(self, client):
        self.client = client

    async def request(self, method: str, path: str, **kwargs: Any) -> ESIHubResponse:
        esihub_logger.info(f"Dry run request: {method} {path}")
        esihub_logger.info(f"Request parameters: {kwargs}")

        # Validate the request parameters here
        self._validate_params(kwargs)

        # Simulate a successful response with echo
        mock_response = ESIHubResponse(
            status=200,
            headers={"Content-Type": "application/json"},
            data=kwargs,
        )

        esihub_logger.info(f"Dry run response: {mock_response}")
        return mock_response

    def _validate_params(self, params: Dict[str, Any]) -> None:
        # Add any parameter validation logic here
        # For example, check if required parameters are present
        required_params = self._get_required_params(params.get("path", ""))
        for param in required_params:
            if param not in params:
                esihub_logger.warning(f"Missing required parameter: {param}")

    def _get_required_params(self, path: str) -> list:
        # This method should return a list of required parameters for the given path
        # You would typically implement this based on the ESI API specification
        return []
