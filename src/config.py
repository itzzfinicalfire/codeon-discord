"""
Simple, user-editable configuration for the Pterodactyl Discord bot.

Edit the variables below to match your environment. Environment variables with
the same names can override these values at runtime, but no external .env file
is required.
"""
from __future__ import annotations

# Discord bot credentials
DISCORD_TOKEN: str = "MTQ1MDQ5NTQwNjgzOTQzMTI3OQ.G_KlAf.7OvpMsIH6N1qrb7UUYta2kfvz0dpBJkrGJUh-Y"
DISCORD_CLIENT_ID: str = "1450495406839431279"
# Optional guild ID for faster command sync during development
DISCORD_GUILD_ID: str = ""

# Pterodactyl Application API settings
PTERO_BASE_URL: str = "https://ctrl.codeon.codes/"
PTERO_APPLICATION_API_KEY: str = "ptla_Cx4lUd3DrVv3h0sa1NgTQZzE4uuSK0xzl26z7OxKo6s"

# Optional SQLite database path for bot configuration storage
PTERO_BOT_DB: str = "bot.db"


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
