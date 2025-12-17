from __future__ import annotations

import discord
from discord import Interaction
from typing import Iterable, List, Set

from src import config
from src.db.store import ConfigStore
from src.utils.errors import PermissionDenied

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
    allowed_roles_raw: Set[str] = set(override_roles) if override_roles else set(required_roles)
    allowed_role_ids: Set[int] = {int(role) for role in allowed_roles_raw if role.isdigit()}
    allowed_role_ids.update(config.ADDITIONAL_ALLOWED_ROLE_IDS)
    allowed_role_names: Set[str] = {role for role in allowed_roles_raw if not role.isdigit()}

    if any(role.id in allowed_role_ids or role.name in allowed_role_names for role in member.roles):
        return
    raise PermissionDenied(
        "You need one of these roles to run this command: "
        f"{', '.join(sorted({*allowed_role_names, *[str(rid) for rid in allowed_role_ids]}))}"
    )


def infer_required_roles(write: bool = False, delete: bool = False) -> List[str]:
    if delete:
        return list(DELETE_ONLY_ROLES)
    if write:
        return list(WRITE_ROLES)
    return list(DEFAULT_READ_ROLES)
