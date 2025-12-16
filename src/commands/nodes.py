from __future__ import annotations

import discord
from discord import app_commands

from db.store import ConfigStore
from ptero.client import PterodactylClient
from rbac.roles import ensure_has_role, infer_required_roles
from ui.components import Paginator
from ui.embeds import list_embeds, summary_embed
from utils.errors import PermissionDenied, PteroAPIError


class Nodes(app_commands.Group):
    def __init__(self, client: PterodactylClient, store: ConfigStore):
        super().__init__(name="nodes", description="Manage nodes")
        self.client = client
        self.store = store

    @app_commands.command(name="list", description="List nodes")
    async def list(self, interaction: discord.Interaction, page: int = 1):  # type: ignore[override]
        await ensure_has_role(
            interaction,
            required_roles=infer_required_roles(write=False),
            command_name="nodes.list",
            store=self.store,
        )
        resp = await self.client.get_paginated("/api/application/nodes", page=page)
        items = [item.get("attributes", {}) for item in resp.data]
        pages = list_embeds("Nodes", items)
        await Paginator(pages).send(interaction)

    @app_commands.command(name="info", description="Node details")
    async def info(self, interaction: discord.Interaction, node_id: int):
        await ensure_has_role(
            interaction,
            required_roles=infer_required_roles(write=False),
            command_name="nodes.info",
            store=self.store,
        )
        data = await self.client.get(f"/api/application/nodes/{node_id}")
        await interaction.response.send_message(
            embed=summary_embed("Node", data.get("attributes", {})), ephemeral=True
        )

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        if isinstance(error, (PermissionDenied, PteroAPIError)):
            await interaction.response.send_message(str(error), ephemeral=True)
        else:
            await interaction.response.send_message("Unexpected error", ephemeral=True)
