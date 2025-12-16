from __future__ import annotations

import asyncio
import signal
import sys
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands

from src import config
from src.commands.allocations import Allocations
from src.commands.dbhosts import DatabaseHosts
from src.commands.locations import Locations
from src.commands.nests import Nests
from src.commands.nodes import Nodes
from src.commands.ptero import PteroAdmin
from src.commands.serverdb import ServerDatabases
from src.commands.servers import Servers
from src.commands.users import Users
from src.db.store import ConfigStore
from src.ptero.client import PteroFactory
from src.rbac.roles import ensure_has_role, infer_required_roles
from src.utils.errors import PermissionDenied, PteroAPIError
from src.utils.logger import get_logger

logger = get_logger(__name__)


def default_ephemeral(store: ConfigStore) -> bool:
    # fallback true
    async def getter() -> bool:
        value = await store.get_config("default_ephemeral")
        return value != "false"

    return getter  # type: ignore[return-value]


class PteroBot(commands.Bot):
    def __init__(self, *, intents: discord.Intents, store: ConfigStore):
        super().__init__(command_prefix="!", intents=intents)
        self.store = store
        factory = PteroFactory()
        self.ptero = factory.get_client()
        self.ptero_admin = PteroAdmin(self.ptero, store)
        self.tree.add_command(self.ptero_admin)
        self.tree.add_command(Servers(self.ptero, store))
        self.tree.add_command(Users(self.ptero, store))
        self.tree.add_command(Nodes(self.ptero, store))
        self.tree.add_command(Locations(self.ptero, store))
        self.tree.add_command(Nests(self.ptero, store))
        self.tree.add_command(Allocations(self.ptero, store))
        self.tree.add_command(DatabaseHosts(self.ptero, store))
        self.tree.add_command(ServerDatabases(self.ptero, store))

        @app_commands.command(name="help", description="Show commands and required roles")
        async def global_help(interaction: discord.Interaction):
            await ensure_has_role(
                interaction,
                required_roles=infer_required_roles(write=False),
                command_name="ptero.help",
                store=self.store,
            )
            embed = await self.ptero_admin.build_help_embed()
            await interaction.response.send_message(embed=embed, ephemeral=True)

        self.tree.add_command(global_help)

    async def _send_error(self, interaction: discord.Interaction, message: str) -> None:
        try:
            if interaction.response.is_done():
                await interaction.followup.send(message, ephemeral=True)
            else:
                await interaction.response.send_message(message, ephemeral=True)
        except Exception:  # noqa: BLE001 - best-effort error reporting
            logger.exception("Failed to send error response")

    async def on_app_command_error(self, interaction: discord.Interaction, error: Exception) -> None:
        original = getattr(error, "original", error)
        if isinstance(original, PermissionDenied):
            await self._send_error(interaction, str(original))
            return

        if isinstance(original, PteroAPIError):
            await self._send_error(
                interaction,
                f"Pterodactyl API error {original.status}: {original.details or original}",
            )
            return

        logger.exception("Unexpected error during command handling", exc_info=error)
        await self._send_error(interaction, "Unexpected error. Please try again or contact an admin.")

    async def setup_hook(self) -> None:
        await self.store.init()
        guild_id = config.DISCORD_GUILD_ID
        if guild_id:
            guild = discord.Object(int(guild_id))
            await self.tree.sync(guild=guild)
            logger.info("Commands synced to guild %s", guild_id)
        else:
            await self.tree.sync()
            logger.info("Commands synced globally")


async def main() -> None:
    token = config.DISCORD_TOKEN
    client_id = config.DISCORD_CLIENT_ID
    if not token or not client_id:
        logger.error("Missing DISCORD_TOKEN or DISCORD_CLIENT_ID in config.py or environment")
        sys.exit(1)

    intents = discord.Intents.default()
    if config.USE_PRIVILEGED_INTENTS:
        intents.members = True
        intents.presences = True
    else:
        logger.info(
            "Privileged intents disabled. Enable USE_PRIVILEGED_INTENTS and toggle intents in the Discord Developer Portal if member data is required."
        )
    store = ConfigStore(db_path=config.PTERO_BOT_DB)
    bot = PteroBot(intents=intents, store=store)

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda s=sig: asyncio.create_task(bot.close()))

    async with bot:
        try:
            await bot.start(token)
        except discord.LoginFailure as exc:
            logger.error(
                "Discord login failed: %s. Verify DISCORD_TOKEN in src/config.py or set a valid token via environment variables.",
                exc,
            )
            raise SystemExit(1) from exc


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
