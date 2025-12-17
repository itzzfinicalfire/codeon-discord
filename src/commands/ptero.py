from __future__ import annotations

import discord
from discord import app_commands

from src import config
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
        # Command catalogue for /ptero help. Update when adding/removing commands.
        self._catalogue = {
            "ptero": [
                {"display": "/ptero ping", "override": "ptero.ping", "roles": infer_required_roles(write=False)},
                {"display": "/ptero whoami", "override": "ptero.whoami", "roles": infer_required_roles(write=False)},
                {"display": "/ptero config", "override": "ptero.config", "roles": infer_required_roles(write=True)},
                {"display": "/ptero help", "override": "ptero.help", "roles": infer_required_roles(write=False)},
                {
                    "display": "/ptero diagnostics",
                    "override": "ptero.diagnostics",
                    "roles": infer_required_roles(write=False),
                },
            ],
            "servers": [
                {"display": "/servers list", "override": "servers.list", "roles": infer_required_roles(write=False)},
                {"display": "/servers info", "override": "servers.info", "roles": infer_required_roles(write=False)},
                {"display": "/servers create", "override": "servers.create", "roles": infer_required_roles(write=True)},
                {"display": "/servers update", "override": "servers.update", "roles": infer_required_roles(write=True)},
                {"display": "/servers suspend", "override": "servers.suspend", "roles": infer_required_roles(write=True)},
                {"display": "/servers unsuspend", "override": "servers.unsuspend", "roles": infer_required_roles(write=True)},
                {"display": "/servers reinstall", "override": "servers.reinstall", "roles": infer_required_roles(write=True)},
                {"display": "/servers delete", "override": "servers.delete", "roles": infer_required_roles(delete=True)},
                {"display": "/servers set-owner", "override": "servers.set-owner", "roles": infer_required_roles(write=True)},
                {"display": "/servers allocations", "override": "servers.allocations", "roles": infer_required_roles(write=True)},
                {"display": "/servers databases", "override": "servers.databases", "roles": infer_required_roles(write=True)},
            ],
            "users": [
                {"display": "/users list", "override": "users.list", "roles": infer_required_roles(write=False)},
                {"display": "/users info", "override": "users.info", "roles": infer_required_roles(write=False)},
                {"display": "/users create", "override": "users.create", "roles": infer_required_roles(write=True)},
                {"display": "/users update", "override": "users.update", "roles": infer_required_roles(write=True)},
                {"display": "/users delete", "override": "users.delete", "roles": infer_required_roles(delete=True)},
            ],
            "nodes": [
                {"display": "/nodes list", "override": "nodes.list", "roles": infer_required_roles(write=False)},
                {"display": "/nodes info", "override": "nodes.info", "roles": infer_required_roles(write=False)},
                {"display": "/nodes create", "override": "nodes.create", "roles": infer_required_roles(write=True)},
                {"display": "/nodes update", "override": "nodes.update", "roles": infer_required_roles(write=True)},
                {"display": "/nodes delete", "override": "nodes.delete", "roles": infer_required_roles(delete=True)},
                {"display": "/nodes allocations", "override": "nodes.allocations", "roles": infer_required_roles(write=True)},
            ],
            "locations": [
                {"display": "/locations list", "override": "locations.list", "roles": infer_required_roles(write=False)},
                {"display": "/locations create", "override": "locations.create", "roles": infer_required_roles(write=True)},
                {"display": "/locations update", "override": "locations.update", "roles": infer_required_roles(write=True)},
                {"display": "/locations delete", "override": "locations.delete", "roles": infer_required_roles(delete=True)},
            ],
            "nests/eggs": [
                {"display": "/nests list", "override": "nests.list", "roles": infer_required_roles(write=False)},
                {"display": "/nests info", "override": "nests.info", "roles": infer_required_roles(write=False)},
                {"display": "/eggs list", "override": "eggs.list", "roles": infer_required_roles(write=False)},
                {"display": "/eggs info", "override": "eggs.info", "roles": infer_required_roles(write=False)},
            ],
            "allocations": [
                {"display": "/allocations search", "override": "allocations.search", "roles": infer_required_roles(write=False)},
                {"display": "/allocations create", "override": "allocations.create", "roles": infer_required_roles(write=True)},
                {"display": "/allocations delete", "override": "allocations.delete", "roles": infer_required_roles(delete=True)},
            ],
            "db hosts": [
                {"display": "/dbhosts list", "override": "dbhosts.list", "roles": infer_required_roles(write=False)},
                {"display": "/dbhosts create", "override": "dbhosts.create", "roles": infer_required_roles(write=True)},
                {"display": "/dbhosts update", "override": "dbhosts.update", "roles": infer_required_roles(write=True)},
                {"display": "/dbhosts delete", "override": "dbhosts.delete", "roles": infer_required_roles(delete=True)},
            ],
            "server databases": [
                {"display": "/serverdb list", "override": "serverdb.list", "roles": infer_required_roles(write=False)},
                {"display": "/serverdb search", "override": "serverdb.search", "roles": infer_required_roles(write=False)},
                {"display": "/serverdb delete", "override": "serverdb.delete", "roles": infer_required_roles(delete=True)},
            ],
        }

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

    @app_commands.command(name="diagnostics", description="Show setup and config status")
    async def diagnostics(self, interaction: discord.Interaction):
        await ensure_has_role(
            interaction,
            required_roles=infer_required_roles(write=False),
            command_name="ptero.diagnostics",
            store=self.store,
        )

        flags = config.diagnostic_flags()
        errors = config.validate_required()

        status_map = {
            "discord_token": "Discord token",
            "discord_client_id": "Discord client ID",
            "ptero_base_url": "Pterodactyl base URL",
            "ptero_application_api_key": "Pterodactyl application API key",
        }

        status_fields: dict[str, str] = {}
        for key, label in status_map.items():
            status = flags.get(key, "missing")
            icon = "✅" if status == "set" else "⚠️"
            status_fields[label] = f"{icon} {status}"

        status_fields["Privileged intents"] = (
            "✅ enabled (toggle in Discord Developer Portal too)"
            if flags.get("privileged_intents") == "enabled"
            else "ℹ️ disabled (enable if you need member/presence data)"
        )
        status_fields["Command sync scope"] = (
            f"Guild-scoped: {config.DISCORD_GUILD_ID}" if config.DISCORD_GUILD_ID else "Global"
        )
        status_fields["Config DB path"] = flags.get("db_path", "bot.db")

        embed = summary_embed("Bot diagnostics", status_fields)
        if errors:
            embed.set_footer(text="Resolve ⚠️ items above and restart the bot.")

        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def build_help_embed(self) -> discord.Embed:
        overrides = await self.store.all_overrides()
        embed = summary_embed("Command catalogue", {})
        embed.description = (
            "Default required roles are shown per command. "
            "If a command has an override in the database, those roles take precedence."
        )

        for group, commands in self._catalogue.items():
            lines = []
            for entry in commands:
                override_roles = overrides.get(entry["override"], [])
                roles = override_roles or entry["roles"]
                lines.append(f"• {entry['display']} — {', '.join(roles)}")
            embed.add_field(name=group, value="\n".join(lines) or "No commands", inline=False)
        return embed

    @app_commands.command(name="help", description="List commands and required roles")
    async def help(self, interaction: discord.Interaction):
        await ensure_has_role(
            interaction,
            required_roles=infer_required_roles(write=False),
            command_name="ptero.help",
            store=self.store,
        )
        embed = await self.build_help_embed()
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
