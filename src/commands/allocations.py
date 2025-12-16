from __future__ import annotations

import discord
from discord import app_commands

from db.store import ConfigStore
from ptero.client import PterodactylClient
from rbac.roles import ensure_has_role, infer_required_roles
from ui.components import Paginator
from ui.embeds import list_embeds
from utils.errors import PermissionDenied, PteroAPIError


class Allocations(app_commands.Group):
    def __init__(self, client: PterodactylClient, store: ConfigStore):
        super().__init__(name="allocations", description="Search allocations")
        self.client = client
        self.store = store

    @app_commands.command(name="search", description="Search allocations")
    @app_commands.describe(node="Filter by node id", ip="Filter by IP")
    async def search(self, interaction: discord.Interaction, node: int | None = None, ip: str | None = None):
        await ensure_has_role(
            interaction,
            required_roles=infer_required_roles(write=False),
            command_name="allocations.search",
            store=self.store,
        )
        params = {}
        if node:
            params["filter[node_id]"] = node
        if ip:
            params["filter[ip]"] = ip
        data = await self.client.get("/api/application/allocations", params=params)
        items = [item.get("attributes", {}) for item in data.get("data", [])]
        await Paginator(list_embeds("Allocations", items)).send(interaction)

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        if isinstance(error, (PermissionDenied, PteroAPIError)):
            await interaction.response.send_message(str(error), ephemeral=True)
        else:
            await interaction.response.send_message("Unexpected error", ephemeral=True)
