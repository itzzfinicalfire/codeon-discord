from __future__ import annotations

import discord
from discord import app_commands

from src.db.store import ConfigStore
from src.ptero.client import PterodactylClient
from src.rbac.roles import ensure_has_role, infer_required_roles
from src.ui.components import Paginator
from src.ui.embeds import list_embeds, summary_embed
from src.utils.errors import PermissionDenied, PteroAPIError


class DatabaseHosts(app_commands.Group):
    def __init__(self, client: PterodactylClient, store: ConfigStore):
        super().__init__(name="dbhosts", description="Manage database hosts")
        self.client = client
        self.store = store

    @app_commands.command(name="list", description="List database hosts")
    async def list(self, interaction: discord.Interaction):  # type: ignore[override]
        await ensure_has_role(
            interaction,
            required_roles=infer_required_roles(write=False),
            command_name="dbhosts.list",
            store=self.store,
        )
        data = await self.client.get("/api/application/database-hosts")
        items = [item.get("attributes", {}) for item in data.get("data", [])]
        await Paginator(list_embeds("Database hosts", items)).send(interaction)

    @app_commands.command(name="info", description="Database host info")
    async def info(self, interaction: discord.Interaction, host_id: int):
        await ensure_has_role(
            interaction,
            required_roles=infer_required_roles(write=False),
            command_name="dbhosts.info",
            store=self.store,
        )
        data = await self.client.get(f"/api/application/database-hosts/{host_id}")
        await interaction.response.send_message(
            embed=summary_embed("Database host", data.get("attributes", {})), ephemeral=True
        )

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        if isinstance(error, (PermissionDenied, PteroAPIError)):
            await interaction.response.send_message(str(error), ephemeral=True)
        else:
            await interaction.response.send_message("Unexpected error", ephemeral=True)
