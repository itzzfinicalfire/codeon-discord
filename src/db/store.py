import asyncio
import os
from typing import Dict, List, Optional

import aiosqlite

DB_PATH = os.environ.get("PTERO_BOT_DB", "bot.db")


class ConfigStore:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._lock = asyncio.Lock()

    async def init(self) -> None:
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "CREATE TABLE IF NOT EXISTS config (key TEXT PRIMARY KEY, value TEXT)"
            )
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS command_overrides (
                    command TEXT PRIMARY KEY,
                    roles TEXT
                )
                """
            )
            await db.commit()

    async def set_config(self, key: str, value: str) -> None:
        async with self._lock:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    "INSERT INTO config(key, value) VALUES(?, ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                    (key, value),
                )
                await db.commit()

    async def get_config(self, key: str) -> Optional[str]:
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT value FROM config WHERE key=?", (key,)) as cur:
                row = await cur.fetchone()
                return row[0] if row else None

    async def set_command_override(self, command: str, roles: List[str]) -> None:
        roles_csv = ",".join(roles)
        async with self._lock:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    "INSERT INTO command_overrides(command, roles) VALUES(?, ?) ON CONFLICT(command) DO UPDATE SET roles=excluded.roles",
                    (command, roles_csv),
                )
                await db.commit()

    async def get_command_override(self, command: str) -> List[str]:
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT roles FROM command_overrides WHERE command=?", (command,)
            ) as cur:
                row = await cur.fetchone()
                if not row:
                    return []
                return [role for role in row[0].split(",") if role]

    async def all_overrides(self) -> Dict[str, List[str]]:
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT command, roles FROM command_overrides") as cur:
                rows = await cur.fetchall()
                return {command: roles.split(",") if roles else [] for command, roles in rows}
