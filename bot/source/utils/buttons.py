from __future__ import annotations

from ..core import context
from ..utils import constants

import typing
import discord


async def default_check(ctx: context.CustomContext, interaction: discord.Interaction):
    return ctx.author.id == interaction.user.id


class ConfirmView(discord.ui.View):
    def __init__(
        self,
        ctx: context.CustomContext,
        *,
        timeout: typing.Optional[float] = 180.0,
        interaction_check: typing.Optional[typing.Callable] = default_check
    ):
        self.ctx = ctx
        super().__init__(timeout=timeout)
        self.interaction_check = interaction_check
        self.value = None

    @discord.ui.button(emoji=constants.Emojis.check_mark)
    async def approve(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        self.value = True
        self.stop()

    @discord.ui.button(emoji=constants.Emojis.X)
    async def deny(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.value = False
        self.stop()

    async def on_error(
        self, error: Exception, item: discord.Item, interaction: discord.Interaction
    ) -> None:
        await self.ctx.bot.on_command_error(ctx=self.ctx, error=error)
