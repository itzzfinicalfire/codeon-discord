from __future__ import annotations

import discord
from discord import app_commands

from db.store import ConfigStore
from ptero.client import PterodactylClient
from rbac.roles import ensure_has_role, infer_required_roles
from ui.components import ConfirmView, Paginator
from ui.embeds import list_embeds, summary_embed
from utils.errors import PermissionDenied, PteroAPIError


class UserCreateModal(discord.ui.Modal, title="Create user"):
    email = discord.ui.TextInput(label="Email", required=True)
    username = discord.ui.TextInput(label="Username", required=True)
    first_name = discord.ui.TextInput(label="First name", required=True)
    last_name = discord.ui.TextInput(label="Last name", required=True)
    password = discord.ui.TextInput(label="Password", required=False, style=discord.TextStyle.short)

    def __init__(self):
        super().__init__()
        self.result: dict | None = None

    async def on_submit(self, interaction: discord.Interaction):
        self.result = {
            "email": str(self.email),
            "username": str(self.username),
            "first_name": str(self.first_name),
            "last_name": str(self.last_name),
        }
        if self.password.value:
            self.result["password"] = str(self.password)
        await interaction.response.send_message("Creating user...", ephemeral=True)


class Users(app_commands.Group):
    def __init__(self, client: PterodactylClient, store: ConfigStore):
        super().__init__(name="users", description="Manage users")
        self.client = client
        self.store = store

    @app_commands.command(name="list", description="List users")
    async def list(self, interaction: discord.Interaction, page: int = 1):  # type: ignore[override]
        await ensure_has_role(
            interaction,
            required_roles=infer_required_roles(write=False),
            command_name="users.list",
            store=self.store,
        )
        resp = await self.client.get_paginated("/api/application/users", page=page)
        items = [item.get("attributes", {}) for item in resp.data]
        pages = list_embeds("Users", items)
        paginator = Paginator(pages)
        await paginator.send(interaction)

    @app_commands.command(name="info", description="User details")
    async def info(self, interaction: discord.Interaction, user_id: int):
        await ensure_has_role(
            interaction,
            required_roles=infer_required_roles(write=False),
            command_name="users.info",
            store=self.store,
        )
        data = await self.client.get(f"/api/application/users/{user_id}")
        embed = summary_embed("User", data.get("attributes", {}))
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="create", description="Create user")
    async def create(self, interaction: discord.Interaction):
        await ensure_has_role(
            interaction,
            required_roles=infer_required_roles(write=True),
            command_name="users.create",
            store=self.store,
        )
        modal = UserCreateModal()
        await interaction.response.send_modal(modal)
        await modal.wait()
        if not modal.result:
            return
        created = await self.client.post("/api/application/users", json=modal.result)
        await interaction.followup.send(
            embed=summary_embed("User created", created.get("attributes", {})), ephemeral=True
        )
        await self._audit(interaction, "create", created.get("attributes", {}))

    @app_commands.command(name="delete", description="Delete user")
    async def delete(self, interaction: discord.Interaction, user_id: int):
        await ensure_has_role(
            interaction,
            required_roles=infer_required_roles(delete=True),
            command_name="users.delete",
            store=self.store,
        )
        view = ConfirmView()
        await interaction.response.send_message("Confirm delete?", view=view, ephemeral=True)
        await view.wait()
        if view.value:
            await self.client.delete(f"/api/application/users/{user_id}")
            await interaction.followup.send(f"User {user_id} deleted", ephemeral=True)
            await self._audit(interaction, "delete", {"user_id": user_id})
        else:
            await interaction.followup.send("Cancelled", ephemeral=True)

    async def _audit(self, interaction: discord.Interaction, action: str, payload: dict):
        channel_id = await self.store.get_config("audit_channel")
        if not channel_id:
            return
        channel = interaction.client.get_channel(int(channel_id))
        if not isinstance(channel, discord.TextChannel):
            return
        await channel.send(
            embed=summary_embed(
                "User action",
                {
                    "actor": interaction.user.display_name,
                    "action": action,
                    **payload,
                },
                color=0x00B894,
            )
        )

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        if isinstance(error, (PermissionDenied, PteroAPIError)):
            await interaction.response.send_message(str(error), ephemeral=True)
        else:
            await interaction.response.send_message("Unexpected error", ephemeral=True)
