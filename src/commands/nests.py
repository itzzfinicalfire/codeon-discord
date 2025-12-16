from __future__ import annotations

import discord
from discord import app_commands

from src.db.store import ConfigStore
from src.ptero.client import PterodactylClient
from src.rbac.roles import ensure_has_role, infer_required_roles
from src.ui.components import Paginator
from src.ui.embeds import list_embeds, summary_embed
from src.utils.errors import PermissionDenied, PteroAPIError


class Nests(app_commands.Group):
    def __init__(self, client: PterodactylClient, store: ConfigStore):
        super().__init__(name="nests", description="Manage nests/eggs")
        self.client = client
        self.store = store

    @app_commands.command(name="list", description="List nests")
    async def list(self, interaction: discord.Interaction):  # type: ignore[override]
        await ensure_has_role(
            interaction,
            required_roles=infer_required_roles(write=False),
            command_name="nests.list",
            store=self.store,
        )
        data = await self.client.get("/api/application/nests")
        items = [item.get("attributes", {}) for item in data.get("data", [])]
        await Paginator(list_embeds("Nests", items)).send(interaction)

    @app_commands.command(name="info", description="Nest details")
    async def info(self, interaction: discord.Interaction, nest_id: int):
        await ensure_has_role(
            interaction,
            required_roles=infer_required_roles(write=False),
            command_name="nests.info",
            store=self.store,
        )
        data = await self.client.get(f"/api/application/nests/{nest_id}")
        await interaction.response.send_message(
            embed=summary_embed("Nest", data.get("attributes", {})), ephemeral=True
        )

    @app_commands.command(name="eggs", description="List eggs for nest")
    async def eggs(self, interaction: discord.Interaction, nest_id: int):
        await ensure_has_role(
            interaction,
            required_roles=infer_required_roles(write=False),
            command_name="eggs.list",
            store=self.store,
        )
        data = await self.client.get(f"/api/application/nests/{nest_id}/eggs")
        items = [item.get("attributes", {}) for item in data.get("data", [])]
        await Paginator(list_embeds("Eggs", items)).send(interaction)

    @app_commands.command(name="egg-info", description="Egg details")
    async def egg_info(self, interaction: discord.Interaction, egg_id: int):
        await ensure_has_role(
            interaction,
            required_roles=infer_required_roles(write=False),
            command_name="eggs.info",
            store=self.store,
        )
        data = await self.client.get(f"/api/application/eggs/{egg_id}")
        await interaction.response.send_message(
            embed=summary_embed("Egg", data.get("attributes", {})), ephemeral=True
        )

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        if isinstance(error, (PermissionDenied, PteroAPIError)):
            await interaction.response.send_message(str(error), ephemeral=True)
        else:
            await interaction.response.send_message("Unexpected error", ephemeral=True)
