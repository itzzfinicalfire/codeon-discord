import logging
import os
from typing import Any

REDACT_KEYS = {"PTERO_APPLICATION_API_KEY", "DISCORD_TOKEN"}


def _redact(value: Any) -> Any:
    if not isinstance(value, str):
        return value
    if any(secret in value for secret in os.environ.get("PTERO_APPLICATION_API_KEY", "")):
        return "***redacted***"
    return value


def get_logger(name: str = "ptero-bot") -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        level = os.environ.get("LOG_LEVEL", "INFO").upper()
        logger.setLevel(level)
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger


def redact_dict(data: dict) -> dict:
    redacted = {}
    for key, value in data.items():
        if key in REDACT_KEYS:
            redacted[key] = "***redacted***"
        else:
            redacted[key] = _redact(value)
    return redacted
