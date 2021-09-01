from __future__ import annotations

from ..utils import buttons
import discord
from discord.ext import commands
import typing


class CustomContext(commands.Context):

    """
    Class to use for the bot basic Context.
    """

    async def send_confirm(
        self,
        content: typing.Optional[str] = ...,
        *,
        tts: bool = ...,
        embed: discord.Embed = ...,
        file: discord.File = ...,
        stickers: typing.Sequence[
            typing.Union[discord.GuildSticker, discord.StickerItem]
        ] = ...,
        delete_after: float = ...,
        nonce: typing.Union[str, int] = ...,
        allowed_mentions: discord.AllowedMentions = ...,
        reference: typing.Union[
            discord.Message, discord.MessageReference, discord.PartialMessage
        ] = ...,
        mention_author: bool = ...,
    ) -> typing.Tuple[discord.Message, buttons.ConfirmView]:
        confirm_view = buttons.ConfirmView(ctx=self, timeout=30.0)
        message = await self.send(
            content=content,
            tts=tts,
            embed=embed,
            file=file,
            stickers=stickers,
            delete_after=delete_after,
            nonce=nonce,
            allowed_mentions=allowed_mentions,
            reference=reference,
            mention_author=mention_author,
            view=confirm_view,
        )
        await confirm_view.wait()
        return message, confirm_view
