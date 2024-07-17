import os
from typing import Any, Dict


class ESIConfig:
    def __init__(self):
        self.config: Dict[str, Any] = {
            "ESI_CLIENT_ID": os.getenv("ESI_CLIENT_ID"),
            "ESI_CLIENT_SECRET": os.getenv("ESI_CLIENT_SECRET"),
            "ESI_CALLBACK_URL": os.getenv("ESI_CALLBACK_URL"),
            "ESI_BASE_URL": os.getenv("ESI_BASE_URL", "https://esi.evetech.net"),
            "ESI_REDIS_URL": os.getenv("ESI_REDIS_URL", "redis://localhost"),
            "ESI_LOG_LEVEL": os.getenv("ESI_LOG_LEVEL", "INFO"),
        }

    def get(self, key: str, default: Any = None) -> Any:
        return self.config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self.config[key] = value


esi_config = ESIConfig()
