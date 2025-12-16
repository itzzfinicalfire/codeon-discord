from __future__ import annotations

import discord
from discord import app_commands

from db.store import ConfigStore
from ptero.client import PterodactylClient
from rbac.roles import ensure_has_role, infer_required_roles
from ui.components import ConfirmView, Paginator
from ui.embeds import list_embeds, summary_embed
from utils.errors import PermissionDenied, PteroAPIError


class Servers(app_commands.Group):
    def __init__(self, client: PterodactylClient, store: ConfigStore):
        super().__init__(name="servers", description="Manage servers")
        self.client = client
        self.store = store

    @app_commands.command(name="list", description="List servers")
    @app_commands.describe(page="Page number")
    async def list(self, interaction: discord.Interaction, page: int = 1):  # type: ignore[override]
        await ensure_has_role(
            interaction,
            required_roles=infer_required_roles(write=False),
            command_name="servers.list",
            store=self.store,
        )
        resp = await self.client.get_paginated("/api/application/servers", page=page)
        items = [self._flatten_attributes(item) for item in resp.data]
        pages = list_embeds("Servers", items)
        paginator = Paginator(pages)
        await paginator.send(interaction)

    @app_commands.command(name="info", description="Server details")
    async def info(self, interaction: discord.Interaction, server_id: int):
        await ensure_has_role(
            interaction,
            required_roles=infer_required_roles(write=False),
            command_name="servers.info",
            store=self.store,
        )
        data = await self.client.get(f"/api/application/servers/{server_id}")
        embed = summary_embed("Server", self._flatten_attributes(data.get("attributes", {})))
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="suspend", description="Suspend a server")
    async def suspend(self, interaction: discord.Interaction, server_id: int, reason: str | None = None):
        await ensure_has_role(
            interaction,
            required_roles=infer_required_roles(write=True),
            command_name="servers.suspend",
            store=self.store,
        )
        await self.client.post(f"/api/application/servers/{server_id}/suspend")
        await interaction.response.send_message(f"Server {server_id} suspended. {reason or ''}", ephemeral=True)
        await self._audit(interaction, "suspend", server_id)

    @app_commands.command(name="unsuspend", description="Unsuspend a server")
    async def unsuspend(self, interaction: discord.Interaction, server_id: int):
        await ensure_has_role(
            interaction,
            required_roles=infer_required_roles(write=True),
            command_name="servers.unsuspend",
            store=self.store,
        )
        await self.client.post(f"/api/application/servers/{server_id}/unsuspend")
        await interaction.response.send_message(f"Server {server_id} unsuspended", ephemeral=True)
        await self._audit(interaction, "unsuspend", server_id)

    @app_commands.command(name="reinstall", description="Reinstall a server")
    async def reinstall(self, interaction: discord.Interaction, server_id: int):
        await ensure_has_role(
            interaction,
            required_roles=infer_required_roles(write=True),
            command_name="servers.reinstall",
            store=self.store,
        )
        view = ConfirmView()
        await interaction.response.send_message("Confirm reinstall?", view=view, ephemeral=True)
        await view.wait()
        if view.value:
            await self.client.post(f"/api/application/servers/{server_id}/reinstall")
            await interaction.followup.send(f"Server {server_id} reinstall queued", ephemeral=True)
            await self._audit(interaction, "reinstall", server_id)
        else:
            await interaction.followup.send("Cancelled", ephemeral=True)

    @app_commands.command(name="delete", description="Delete a server")
    async def delete(self, interaction: discord.Interaction, server_id: int):
        await ensure_has_role(
            interaction,
            required_roles=infer_required_roles(delete=True),
            command_name="servers.delete",
            store=self.store,
        )
        view = ConfirmView()
        await interaction.response.send_message("Confirm delete?", view=view, ephemeral=True)
        await view.wait()
        if view.value:
            await self.client.delete(f"/api/application/servers/{server_id}")
            await interaction.followup.send(f"Server {server_id} deleted", ephemeral=True)
            await self._audit(interaction, "delete", server_id)
        else:
            await interaction.followup.send("Cancelled", ephemeral=True)

    @app_commands.command(name="set-owner", description="Change server owner")
    async def set_owner(self, interaction: discord.Interaction, server_id: int, user_id: int):
        await ensure_has_role(
            interaction,
            required_roles=infer_required_roles(write=True),
            command_name="servers.set-owner",
            store=self.store,
        )
        await self.client.post(
            f"/api/application/servers/{server_id}/transfer",
            json={"user": user_id},
        )
        await interaction.response.send_message(
            f"Server {server_id} owner set to {user_id}", ephemeral=True
        )
        await self._audit(interaction, "set-owner", server_id, extra={"user": user_id})

    async def _audit(self, interaction: discord.Interaction, action: str, server_id: int, extra: dict | None = None):
        channel_id = await self.store.get_config("audit_channel")
        if not channel_id:
            return
        channel = interaction.client.get_channel(int(channel_id))
        if not isinstance(channel, discord.TextChannel):
            return
        embed = summary_embed(
            "Server action",
            {
                "actor": interaction.user.display_name,
                "action": action,
                "server_id": server_id,
                **(extra or {}),
            },
            color=0xE67E22,
        )
        await channel.send(embed=embed)

    def _flatten_attributes(self, item: dict) -> dict:
        if "attributes" in item:
            return {**item.get("attributes", {})}
        return item

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        if isinstance(error, PermissionDenied):
            await interaction.response.send_message(str(error), ephemeral=True)
            return
        if isinstance(error, PteroAPIError):
            await interaction.response.send_message(str(error), ephemeral=True)
            return
        await interaction.response.send_message("Unexpected error", ephemeral=True)
