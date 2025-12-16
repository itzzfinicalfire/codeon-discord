from __future__ import annotations

import discord
from discord import app_commands

from src.db.store import ConfigStore
from src.ptero.client import PterodactylClient
from src.rbac.roles import ensure_has_role, infer_required_roles
from src.ui.components import Paginator
from src.ui.embeds import list_embeds
from src.utils.errors import PermissionDenied, PteroAPIError


class ServerDatabases(app_commands.Group):
    def __init__(self, client: PterodactylClient, store: ConfigStore):
        super().__init__(name="serverdb", description="Search server databases")
        self.client = client
        self.store = store

    @app_commands.command(name="list", description="List databases for server")
    async def list(self, interaction: discord.Interaction, server_id: int):  # type: ignore[override]
        await ensure_has_role(
            interaction,
            required_roles=infer_required_roles(write=False),
            command_name="serverdb.list",
            store=self.store,
        )
        data = await self.client.get(f"/api/application/servers/{server_id}/databases")
        items = [item.get("attributes", {}) for item in data.get("data", [])]
        await Paginator(list_embeds("Server databases", items)).send(interaction)

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        if isinstance(error, (PermissionDenied, PteroAPIError)):
            await interaction.response.send_message(str(error), ephemeral=True)
        else:
            await interaction.response.send_message("Unexpected error", ephemeral=True)
