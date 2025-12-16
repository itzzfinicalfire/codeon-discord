import logging
import os
from typing import Any

REDACT_KEYS = {"PTERO_APPLICATION_API_KEY", "DISCORD_TOKEN"}


def _mask_secret(value: str) -> str:
    """Return a partially masked version of a secret value."""

    if not value:
        return "***redacted***"
    if len(value) <= 8:
        return "***redacted***"
    return f"{value[:4]}...{value[-4:]}"


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
            redacted[key] = _mask_secret(value) if isinstance(value, str) else "***redacted***"
        else:
            redacted[key] = value
    return redacted
