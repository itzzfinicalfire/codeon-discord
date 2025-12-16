from __future__ import annotations

import discord
from discord import Interaction
from typing import Iterable, List

from db.store import ConfigStore
from utils.errors import PermissionDenied

SUPERADMIN = "Ptero SuperAdmin"
OPERATOR = "Ptero Operator"
VIEWER = "Ptero Viewer"

WRITE_ROLES = {SUPERADMIN, OPERATOR}
DELETE_ONLY_ROLES = {SUPERADMIN}
DEFAULT_READ_ROLES = {SUPERADMIN, OPERATOR, VIEWER}


async def ensure_has_role(
    interaction: Interaction, *, required_roles: Iterable[str], command_name: str, store: ConfigStore
) -> None:
    member = interaction.user
    assert isinstance(member, discord.Member)
    override_roles = await store.get_command_override(command_name)
    allowed_roles = set(override_roles) if override_roles else set(required_roles)
    if any(role.name in allowed_roles for role in member.roles):
        return
    raise PermissionDenied(
        f"You need one of these roles to run this command: {', '.join(allowed_roles)}"
    )


def infer_required_roles(write: bool = False, delete: bool = False) -> List[str]:
    if delete:
        return list(DELETE_ONLY_ROLES)
    if write:
        return list(WRITE_ROLES)
    return list(DEFAULT_READ_ROLES)
