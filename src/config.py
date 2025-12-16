"""
Simple, user-editable configuration for the Pterodactyl Discord bot.

Edit the variables below to match your environment. Environment variables with
the same names can override these values at runtime, but no external .env file
is required.
"""
from __future__ import annotations

import os

# Discord bot credentials
DISCORD_TOKEN: str = os.getenv("DISCORD_TOKEN", "your_discord_bot_token")
DISCORD_CLIENT_ID: str = os.getenv("DISCORD_CLIENT_ID", "your_discord_client_id")
# Optional guild ID for faster command sync during development
DISCORD_GUILD_ID: str = os.getenv("DISCORD_GUILD_ID", "")

# Enable privileged intents (members/presences) only if explicitly requested.
# This must also be toggled on in the Discord Developer Portal for the bot.
USE_PRIVILEGED_INTENTS: bool = os.getenv("USE_PRIVILEGED_INTENTS", "false").lower() in {
    "1",
    "true",
    "yes",
}

# Pterodactyl Application API settings
PTERO_BASE_URL: str = os.getenv("PTERO_BASE_URL", "https://panel.example.com")
PTERO_APPLICATION_API_KEY: str = os.getenv("PTERO_APPLICATION_API_KEY", "your_application_api_key")

# Optional SQLite database path for bot configuration storage
PTERO_BOT_DB: str = os.getenv("PTERO_BOT_DB", "bot.db")

# Optional comma-separated role IDs that should always be treated as allowed for RBAC
# checks (in addition to the default role names or per-command overrides). Example:
#   ADDITIONAL_ALLOWED_ROLE_IDS="123456789012345678,987654321098765432"
ADDITIONAL_ALLOWED_ROLE_IDS = [
    int(role_id.strip())
    for role_id in os.getenv("ADDITIONAL_ALLOWED_ROLE_IDS", "").split(",")
    if role_id.strip().isdigit()
]


def as_dict() -> dict[str, str]:
    """Return the configuration as a dictionary for debugging or display."""
    return {
        "DISCORD_TOKEN": DISCORD_TOKEN,
        "DISCORD_CLIENT_ID": DISCORD_CLIENT_ID,
        "DISCORD_GUILD_ID": DISCORD_GUILD_ID,
        "USE_PRIVILEGED_INTENTS": USE_PRIVILEGED_INTENTS,
        "PTERO_BASE_URL": PTERO_BASE_URL,
        "PTERO_APPLICATION_API_KEY": PTERO_APPLICATION_API_KEY,
        "PTERO_BOT_DB": PTERO_BOT_DB,
        "ADDITIONAL_ALLOWED_ROLE_IDS": ADDITIONAL_ALLOWED_ROLE_IDS,
    }


def validate_required() -> list[str]:
    """Return a list of validation errors for required settings.

    This helps catch placeholder values early so the bot can fail fast with a
    clear message instead of confusing login errors.
    """

    errors: list[str] = []

    if not DISCORD_TOKEN or DISCORD_TOKEN == "your_discord_bot_token":
        errors.append("DISCORD_TOKEN is missing or still set to the placeholder")

    if not DISCORD_CLIENT_ID or DISCORD_CLIENT_ID == "your_discord_client_id":
        errors.append("DISCORD_CLIENT_ID is missing or still set to the placeholder")

    if not PTERO_BASE_URL or PTERO_BASE_URL == "https://panel.example.com":
        errors.append("PTERO_BASE_URL is missing or still set to the placeholder")

    if not PTERO_APPLICATION_API_KEY or PTERO_APPLICATION_API_KEY == "your_application_api_key":
        errors.append(
            "PTERO_APPLICATION_API_KEY is missing or still set to the placeholder"
        )

    return errors


def diagnostic_flags() -> dict[str, str]:
    """Return human-readable flags for common startup issues."""

    errors = validate_required()
    joined = ",".join(errors)

    flags = {
        "discord_token": "set" if "DISCORD_TOKEN is missing" not in joined else "missing",
        "discord_client_id": "set" if "DISCORD_CLIENT_ID is missing" not in joined else "missing",
        "ptero_base_url": "set" if "PTERO_BASE_URL is missing" not in joined else "missing",
        "ptero_application_api_key": "set"
        if "PTERO_APPLICATION_API_KEY is missing" not in joined
        else "missing",
        "privileged_intents": "enabled" if USE_PRIVILEGED_INTENTS else "disabled",
        "guild_scoped_sync": "enabled" if DISCORD_GUILD_ID else "global",
        "db_path": PTERO_BOT_DB or "bot.db",
    }

    return flags

__all__ = [
    "DISCORD_TOKEN",
    "DISCORD_CLIENT_ID",
    "DISCORD_GUILD_ID",
    "USE_PRIVILEGED_INTENTS",
    "PTERO_BASE_URL",
    "PTERO_APPLICATION_API_KEY",
    "PTERO_BOT_DB",
    "ADDITIONAL_ALLOWED_ROLE_IDS",
    "as_dict",
    "validate_required",
    "diagnostic_flags",
]
