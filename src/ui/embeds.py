from __future__ import annotations

import datetime
from typing import Any, Dict, List

import discord


def summary_embed(title: str, data: Dict[str, Any], *, color: int = 0x2F3136) -> discord.Embed:
    embed = discord.Embed(title=title, color=color, timestamp=datetime.datetime.utcnow())
    for key, value in data.items():
        embed.add_field(name=key, value=str(value), inline=False)
    return embed


def list_embeds(title: str, items: List[Dict[str, Any]], *, page_size: int = 5) -> List[discord.Embed]:
    pages: List[discord.Embed] = []
    for i in range(0, len(items), page_size):
        chunk = items[i : i + page_size]
        embed = discord.Embed(title=title, color=0x5865F2)
        for row in chunk:
            name = row.get("name") or row.get("id") or "item"
            desc = "\n".join(f"{k}: {v}" for k, v in row.items())
            embed.add_field(name=str(name), value=desc[:1024], inline=False)
        embed.set_footer(text=f"Page {len(pages)+1}")
        pages.append(embed)
    return pages or [discord.Embed(title=title, description="No results", color=0x5865F2)]
