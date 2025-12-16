from __future__ import annotations

import discord
from discord import app_commands

from src.db.store import ConfigStore
from src.ptero.client import PterodactylClient
from src.rbac.roles import infer_required_roles, ensure_has_role
from src.ui.embeds import summary_embed
from src.utils.errors import PermissionDenied


class PteroAdmin(app_commands.Group):
    def __init__(self, client: PterodactylClient, store: ConfigStore):
        super().__init__(name="ptero", description="Pterodactyl admin commands")
        self.client = client
        self.store = store

    @app_commands.command(name="ping", description="Check bot connectivity")
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message("Pong!", ephemeral=True)

    @app_commands.command(name="whoami", description="Show API identity")
    async def whoami(self, interaction: discord.Interaction):
        await ensure_has_role(
            interaction,
            required_roles=infer_required_roles(write=False),
            command_name="ptero.whoami",
            store=self.store,
        )
        data = await self.client.get("/api/application/users", params={"per_page": 1})
        meta = data.get("meta", {})
        embed = summary_embed(
            "API token",
            {
                "Base URL": self.client.base_url,
                "Rate limit": meta.get("pagination", {}).get("total") or "unknown",
            },
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="config", description="Configure bot")
    @app_commands.describe(audit_channel="Channel for audit logs", default_ephemeral="Default ephemeral responses")
    async def config(self, interaction: discord.Interaction, audit_channel: discord.TextChannel | None = None, default_ephemeral: bool | None = None):
        await ensure_has_role(
            interaction,
            required_roles=infer_required_roles(write=True),
            command_name="ptero.config",
            store=self.store,
        )
        updates = {}
        if audit_channel:
            await self.store.set_config("audit_channel", str(audit_channel.id))
            updates["audit_channel"] = audit_channel.mention
        if default_ephemeral is not None:
            await self.store.set_config("default_ephemeral", "true" if default_ephemeral else "false")
            updates["default_ephemeral"] = default_ephemeral
        if not updates:
            await interaction.response.send_message("No changes provided", ephemeral=True)
            return
        embed = summary_embed("Configuration updated", updates)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        if isinstance(error, PermissionDenied):
            await interaction.response.send_message(str(error), ephemeral=True)
            return
        await interaction.response.send_message("Unexpected error", ephemeral=True)
