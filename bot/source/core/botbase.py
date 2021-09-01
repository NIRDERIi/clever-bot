from __future__ import annotations
from discord.ext import commands
import typing
import aiohttp
from dotenv import load_dotenv
import os
from ..utils import errors, functions, constants
import pathlib
import importlib
import inspect
import asyncpg
from ..core import context
import discord


load_dotenv()


class Bot(commands.Bot):

    """A bot class for easy managment and features."""

    def __init__(self, command_prefix, help_command, description=None, **options):
        """Bot class initialize."""
        super().__init__(
            command_prefix,
            help_command=help_command,
            description=description,
            **options,
        )
        self.session: typing.Optional[aiohttp.ClientSession] = None
        self.INVALID_EXTENSIONS: list[str] = ["__init__"]
        self.admin: list[discord.User.id] = [480404983372709908]
        self.allowed_users: list[discord.User.id] = [480404983372709908]
        self.pool = self.loop.run_until_complete(
            asyncpg.create_pool(dsn=self.dsn, min_size=5, max_size=5)
        )
        self.build_embed: typing.Callable = functions.build_embed
        self.prefixes: dict[discord.Guild.id : str] = {}
        self.blacklisted = []

    async def is_blacklisted(self, target_id: int):
        if target_id in self.admin:
            return False
        if target_id in self.blacklisted:
            return True
        async with self.pool.acquire(timeout=constants.Time.db_time) as conn:
            data = await conn.fetch(
                """SELECT target FROM blacklist WHERE target = ($1)""", target_id
            )
        if data:
            self.blacklisted.append(target_id)
            return True
        return False

    async def check_blacklist(self, ctx: context.CustomContext):
        if ctx.author.id in self.admin:
            return True
        if ctx.command.name == self.get_command("is-blacklisted").name:
            return True
        if await self.is_blacklisted(ctx.author.id) or await self.is_blacklisted(
            ctx.guild.id
        ):
            return False
        return True

    async def get_context(
        self,
        message: discord.Message,
        *,
        cls: context.CustomContext = context.CustomContext,
    ) -> context.CustomContext:
        return await super().get_context(message, cls=cls)

    @property
    def token(self) -> None:
        """Gets the token stored in .env file."""
        token = os.getenv("TOKEN")
        if not token:
            raise errors.EnvError("Error raised trying to get TOKEN.")

        return token

    @property
    def dsn(self) -> typing.Optional[str]:
        """Gets the dsn stored in .env file."""
        dsn = os.getenv("DSN")
        if not dsn:
            raise errors.EnvError("Error raise trying to get DSN.")
        return dsn

    def get_extensions_relative_path(self, path="source/exts") -> typing.Iterable:
        """Gets all extensions to load as an iterable."""
        for filename in os.listdir(path):
            if filename in self.INVALID_EXTENSIONS:
                continue
            iterable = pathlib.Path().glob(f"**/*{filename}")
            paths = [pathlib_path for pathlib_path in iterable]
            if not paths:
                continue
            path = ".".join(paths[0].parts).replace(".py", "")
            try:
                if not callable(
                    importlib.import_module(path).setup
                ) and not inspect.isfunction(importlib.import_module(path).setup):
                    continue
            except AttributeError:
                continue
            yield path
        yield "jishaku"

    def load_extensions(self, path="source/exts"):
        """Loads the extensions of the bot."""
        paths = [path for path in self.get_extensions_relative_path(path=path)]
        for path in paths:
            self.load_extension(path)
            print(f"Cog loaded: {path}")

    async def login(self, token: str = None) -> None:
        self.session = aiohttp.ClientSession()
        return await super().login(token)

    async def close(self):
        if self.session:
            await self.session.close()
        await super().close()

    def run(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        self.load_extensions()
        super().run(*args, **kwargs)
