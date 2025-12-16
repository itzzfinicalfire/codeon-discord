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
]
