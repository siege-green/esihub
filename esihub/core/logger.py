import json
import logging
from typing import Any, Dict


class ESIHubLogger:
    def __init__(self, name: str, level: int = logging.INFO):
        self.logger = logging.getLogger(name)
        self.set_level(level)
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def set_level(self, level: int):
        self.logger.setLevel(level)

    def _format_log(self, message: str, extra: Dict[str, Any] = None) -> str:
        log_data = {"message": message}
        if extra:
            log_data.update(extra)
        return json.dumps(log_data)

    def debug(self, message: str, extra: Dict[str, Any] = None):
        self.logger.debug(self._format_log(message, extra))

    def info(self, message: str, extra: Dict[str, Any] = None):
        self.logger.info(self._format_log(message, extra))

    def warning(self, message: str, extra: Dict[str, Any] = None):
        self.logger.warning(self._format_log(message, extra))

    def error(self, message: str, extra: Dict[str, Any] = None, exc_info: bool = False):
        self.logger.error(self._format_log(message, extra), exc_info=exc_info)

    def critical(
        self, message: str, extra: Dict[str, Any] = None, exc_info: bool = False
    ):
        self.logger.critical(self._format_log(message, extra), exc_info=exc_info)


esihub_logger = ESIHubLogger("esihub")


def configure_logging(config):
    log_level = getattr(logging, config.get("LOG_LEVEL", "INFO").upper())
    esihub_logger.set_level(log_level)
