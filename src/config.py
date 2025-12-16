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

# Pterodactyl Application API settings
PTERO_BASE_URL: str = os.getenv("PTERO_BASE_URL", "https://panel.example.com")
PTERO_APPLICATION_API_KEY: str = os.getenv("PTERO_APPLICATION_API_KEY", "your_application_api_key")

# Optional SQLite database path for bot configuration storage
PTERO_BOT_DB: str = os.getenv("PTERO_BOT_DB", "bot.db")


def as_dict() -> dict[str, str]:
    """Return the configuration as a dictionary for debugging or display."""
    return {
        "DISCORD_TOKEN": DISCORD_TOKEN,
        "DISCORD_CLIENT_ID": DISCORD_CLIENT_ID,
        "DISCORD_GUILD_ID": DISCORD_GUILD_ID,
        "PTERO_BASE_URL": PTERO_BASE_URL,
        "PTERO_APPLICATION_API_KEY": PTERO_APPLICATION_API_KEY,
        "PTERO_BOT_DB": PTERO_BOT_DB,
    }

__all__ = [
    "DISCORD_TOKEN",
    "DISCORD_CLIENT_ID",
    "DISCORD_GUILD_ID",
    "PTERO_BASE_URL",
    "PTERO_APPLICATION_API_KEY",
    "PTERO_BOT_DB",
    "as_dict",
]
