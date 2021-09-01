from __future__ import annotations

import functools
import typing
from ..core import context, botbase
from discord.ext import commands
from ..utils import errors


def is_admin():
    def wrapper(func):
        @functools.wraps(func)
        async def check(*args, **kwargs):
            ctx: typing.Optional[context.CustomContext] = args[0]
            if not isinstance(ctx, context.CustomContext) or isinstance(
                ctx, commands.Cog
            ):
                ctx = args[1]
                if not isinstance(ctx, context.CustomContext):
                    raise errors.ProcessError(
                        f"Inner error getting context.Context object."
                    )

            bot: botbase.Bot = ctx.bot
            if ctx.author.id not in bot.admin:
                raise errors.ProcessError(
                    "This command is restricted to bot admins only!"
                )
            return await func(*args, **kwargs)

        return check

    return wrapper


def is_allowed():
    def wrapper(func):
        @functools.wraps(func)
        async def check(*args, **kwargs):
            ctx: typing.Optional[context.CustomContext] = args[0]
            if not isinstance(ctx, context.CustomContext) or isinstance(
                ctx, commands.Cog
            ):
                ctx = args[1]
                if not isinstance(ctx, context.CustomContext):
                    raise errors.ProcessError(
                        "Inner error getting context.Context object."
                    )

            bot: botbase.Bot = ctx.bot
            if ctx.author.id not in bot.allowed_users:
                raise errors.ProcessError(
                    "This command is restricted to bot allowed users only!"
                )
            return await func(*args, **kwargs)

        return check

    return wrapper
