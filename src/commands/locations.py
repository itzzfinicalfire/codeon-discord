from __future__ import annotations

import discord
from discord import app_commands

from db.store import ConfigStore
from ptero.client import PterodactylClient
from rbac.roles import ensure_has_role, infer_required_roles
from ui.components import Paginator
from ui.embeds import list_embeds, summary_embed
from utils.errors import PermissionDenied, PteroAPIError


class Locations(app_commands.Group):
    def __init__(self, client: PterodactylClient, store: ConfigStore):
        super().__init__(name="locations", description="Manage locations")
        self.client = client
        self.store = store

    @app_commands.command(name="list", description="List locations")
    async def list(self, interaction: discord.Interaction):  # type: ignore[override]
        await ensure_has_role(
            interaction,
            required_roles=infer_required_roles(write=False),
            command_name="locations.list",
            store=self.store,
        )
        data = await self.client.get("/api/application/locations")
        items = [item.get("attributes", {}) for item in data.get("data", [])]
        pages = list_embeds("Locations", items)
        await Paginator(pages).send(interaction)

    @app_commands.command(name="info", description="Location details")
    async def info(self, interaction: discord.Interaction, location_id: int):
        await ensure_has_role(
            interaction,
            required_roles=infer_required_roles(write=False),
            command_name="locations.info",
            store=self.store,
        )
        data = await self.client.get(f"/api/application/locations/{location_id}")
        await interaction.response.send_message(
            embed=summary_embed("Location", data.get("attributes", {})), ephemeral=True
        )

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        if isinstance(error, (PermissionDenied, PteroAPIError)):
            await interaction.response.send_message(str(error), ephemeral=True)
        else:
            await interaction.response.send_message("Unexpected error", ephemeral=True)
