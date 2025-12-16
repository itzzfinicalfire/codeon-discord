from __future__ import annotations

import discord
from typing import Callable, List, Optional


class ConfirmView(discord.ui.View):
    def __init__(self, *, timeout: int = 30):
        super().__init__(timeout=timeout)
        self.value: Optional[bool] = None

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):  # type: ignore[override]
        self.value = True
        await interaction.response.defer()
        self.stop()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):  # type: ignore[override]
        self.value = False
        await interaction.response.defer()
        self.stop()


class Paginator(discord.ui.View):
    def __init__(self, pages: List[discord.Embed], *, timeout: int = 120):
        super().__init__(timeout=timeout)
        self.pages = pages
        self.index = 0
        self.message: Optional[discord.Message] = None
        self.update_state()

    def update_state(self) -> None:
        self.children[0].disabled = self.index <= 0  # type: ignore[index]
        self.children[1].disabled = self.index >= len(self.pages) - 1  # type: ignore[index]

    async def on_timeout(self) -> None:
        for child in self.children:
            child.disabled = True
        if self.message:
            await self.message.edit(view=self)

    async def send(self, interaction: discord.Interaction) -> None:
        if not self.pages:
            await interaction.response.send_message("No results", ephemeral=True)
            return
        await interaction.response.send_message(embed=self.pages[self.index], view=self, ephemeral=True)
        self.message = await interaction.original_response()

    @discord.ui.button(label="Prev", style=discord.ButtonStyle.secondary)
    async def prev(self, interaction: discord.Interaction, button: discord.ui.Button):  # type: ignore[override]
        if self.index > 0:
            self.index -= 1
        self.update_state()
        await interaction.response.edit_message(embed=self.pages[self.index], view=self)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.primary)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):  # type: ignore[override]
        if self.index < len(self.pages) - 1:
            self.index += 1
        self.update_state()
        await interaction.response.edit_message(embed=self.pages[self.index], view=self)
