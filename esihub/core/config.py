import os
from typing import Any, Dict


class ESIHubConfig:
    def __init__(self):
        self.config: Dict[str, Any] = {
            "ESI_CLIENT_ID": os.getenv("ESI_CLIENT_ID"),
            "ESI_CLIENT_SECRET": os.getenv("ESI_CLIENT_SECRET"),
            "ESI_CALLBACK_URL": os.getenv("ESI_CALLBACK_URL"),
            "ESI_BASE_URL": os.getenv("ESI_BASE_URL", "https://esi.evetech.net"),
            "ESI_USER_AGENT": os.getenv("ESI_USER_AGENT", "ESIHub/1.0"),
            "ESI_RETRY_ATTEMPTS": int(os.getenv("ESI_RETRY_ATTEMPTS", "3")),
            "ESI_RATE_LIMIT": int(os.getenv("ESI_RATE_LIMIT", "150")),
            "REDIS_URL": os.getenv("REDIS_URL"),
            "LOG_LEVEL": os.getenv("LOG_LEVEL", "INFO"),
            "USE_HTTPS": os.getenv("USE_HTTPS", "True").lower() == "true",
            "MAX_CONCURRENT_REQUESTS": int(os.getenv("MAX_CONCURRENT_REQUESTS", "100")),
            "MAX_CONNECTIONS": int(os.getenv("MAX_CONNECTIONS", "100")),
            "DRY_RUN": os.getenv("DRY_RUN", "False").lower() == "true",
        }

    def get(self, key: str, default: Any = None) -> Any:
        return self.config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self.config[key] = value

    def update(self, config: Dict[str, Any]) -> None:
        self.config.update(config)


esi_config = ESIHubConfig()
