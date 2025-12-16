from __future__ import annotations

import asyncio
import signal
import sys
from typing import Optional

import discord
from discord.ext import commands

from commands.allocations import Allocations
from commands.dbhosts import DatabaseHosts
from commands.locations import Locations
from commands.nests import Nests
from commands.nodes import Nodes
from commands.ptero import PteroAdmin
from commands.serverdb import ServerDatabases
from commands.servers import Servers
from commands.users import Users
from src import config
from db.store import ConfigStore
from ptero.client import PteroFactory
from utils.logger import get_logger

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
        self.tree.add_command(PteroAdmin(self.ptero, store))
        self.tree.add_command(Servers(self.ptero, store))
        self.tree.add_command(Users(self.ptero, store))
        self.tree.add_command(Nodes(self.ptero, store))
        self.tree.add_command(Locations(self.ptero, store))
        self.tree.add_command(Nests(self.ptero, store))
        self.tree.add_command(Allocations(self.ptero, store))
        self.tree.add_command(DatabaseHosts(self.ptero, store))
        self.tree.add_command(ServerDatabases(self.ptero, store))

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
    intents.members = True
    store = ConfigStore(db_path=config.PTERO_BOT_DB)
    bot = PteroBot(intents=intents, store=store)

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda s=sig: asyncio.create_task(bot.close()))

    async with bot:
        await bot.start(token)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
