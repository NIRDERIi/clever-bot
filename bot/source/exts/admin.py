from __future__ import annotations
import datetime
import inspect
import typing

import discord
from ..core import botbase, context
from discord.ext import commands
from ..utils import decorators, converters, functions, constants, errors
import contextlib
import io
import traceback
import importlib


class Admin(commands.Cog):
    """Cog for restricted commands"""

    def __init__(self, bot: botbase.Bot):
        self.bot = bot
        self.eval_jobs: dict[int : context.CustomContext] = {}

    def has_setup_function(self, path: str):
        module = importlib.import_module(path)
        if not callable(module.setup) or not inspect.isfunction(module.setup):
            return False
        return True

    def get_kwargs_for_eval(self, kwargs: dict, link_or_file):
        if isinstance(link_or_file, str):
            kwargs["content"] = link_or_file
        else:
            kwargs["file"] = link_or_file
        return kwargs

    @commands.command(name="blacklist")
    @decorators.is_allowed()
    async def blacklist(
        self,
        ctx: context.CustomContext,
        target: typing.Union[discord.Guild, discord.User],
        *,
        reason: str = "None provided.",
    ):
        await self.bot.pool.execute(
            """INSERT INTO blacklist VALUES($1, $2, $3, $4)""",
            target.id,
            ctx.author.id,
            reason,
            datetime.datetime.utcnow(),
        )
        embed = self.bot.build_embed(
            user=ctx.author, description=f"Blacklisted {target}"
        )
        await ctx.send(embed=embed)
        self.bot.blacklisted.append(target.id)

    @commands.command(name="unblacklist")
    @decorators.is_allowed()
    async def unblacklist(
        self,
        ctx: context.CustomContext,
        target: typing.Union[discord.Guild, discord.User],
    ):
        if target.id in self.bot.admin:
            raise errors.ProcessError("You can't blacklist a bot admin.")
        await self.bot.pool.execute(
            """DELETE FROM blacklist WHERE target = ($1)""", target.id
        )
        embed = self.bot.build_embed(
            user=ctx.author, description=f"Unblacklisted {target}"
        )
        await ctx.send(embed=embed)
        with contextlib.suppress(ValueError):
            self.bot.blacklisted.remove(target.id)

    @commands.command(name="eval")
    @decorators.is_admin()
    async def _eval(
        self,
        ctx: context.CustomContext,
        *,
        code: converters.CodeConverter(add_function=True),
    ):
        """Runs input eval code."""

        env = {"discord": discord, "ctx": ctx}
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            try:
                exec(code, env)
                return_value = await env["eval_job_function"]()
                if not return_value and return_value is None:
                    return_value = ""
                else:
                    return_value = str(return_value)
                result = str(stdout.getvalue()).replace("\n", "\n")
                result += f"{return_value}"
                kwargs = {}

                if len(result) > 1900:
                    link_or_file = await functions.paste_or_file(
                        text=result, session=self.bot.session, filename="output.txt"
                    )
                    kwargs = self.get_kwargs_for_eval(
                        kwargs=kwargs, link_or_file=link_or_file
                    )
                if not kwargs:
                    kwargs["content"] = f"{result or None}"
            except Exception as error:
                traceback_error = (
                    "\n".join(
                        traceback.format_exception(
                            type(error, error, error.__traceback__)
                        )
                    )
                    or "stderr None"
                )
                if len(traceback_error) > 1500:
                    link_or_file = await functions.paste_or_file(
                        text=traceback_error,
                        session=self.bot.session,
                        filename="error.txt",
                    )
                    kwargs = self.get_kwargs_for_eval(
                        kwargs=kwargs, link_or_file=link_or_file
                    )
                else:
                    kwargs["content"] = f"```{traceback_error or None}```"
            print(f"kwargs: {kwargs}")

            await ctx.send(**kwargs)
            self.eval_jobs[ctx.author.id] = ctx

    @commands.Cog.listener(name="on_message_edit")
    async def eval_edit(self, before: discord.Message, after: discord.Message):

        eval_command = self.bot.get_command("eval")
        ctx: context.CustomContext = await self.bot.get_context(message=after)
        if (
            ctx.valid
            and ctx.command.name == eval_command.name
            and after.author.id in self.bot.admin
        ):
            await ctx.reinvoke()

    @commands.command(name="load", aliases=["load-extension"])
    @decorators.is_allowed()
    async def _load(self, ctx: context.CustomContext, *, extension: str):
        if not extension.endswith(".py"):
            extension = f"{extension}.py"
        paths = functions.get_relative_path(extension, with_extension=False, sep=".")
        if not paths:
            raise errors.ProcessError(f"Extension {extension} not found!")
        path = paths[0]
        self.bot.load_extension(name=path)
        embed = self.bot.build_embed(
            user=ctx.author, description=f"{constants.Emojis.restart} {path}"
        )
        await ctx.send(embed=embed)

    @commands.command(name="reload")
    @decorators.is_allowed()
    async def _reload(self, ctx: context.CustomContext, *, extension: str):
        embed = self.bot.build_embed(user=ctx.author, description="")
        if extension == "~":
            extensions = [data[0] for data in self.bot.extensions.items()]
            for extension_path in extensions:
                self.bot.reload_extension(extension_path)
                embed.description += (
                    f"{constants.Emojis.restart} **{extension_path}**\n\n"
                )
        else:
            paths = functions.get_relative_path(
                extension, with_extension=False, sep="."
            )
            if not paths:
                raise errors.ProcessError("Extension {extension} not found!")
            path = paths[0]
            if not self.has_setup_function(path=path):
                raise errors.ProcessError("This path has no setup function.")
            self.bot.reload_extension(name=path)
            embed.description = f"{constants.Emojis.restart} {path}"
        await ctx.send(embed=embed)


def setup(bot: botbase.Bot):
    bot.add_cog(Admin(bot=bot))
