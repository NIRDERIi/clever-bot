from __future__ import annotations
from discord.ext import commands
import typing
import aiohttp
from dotenv import load_dotenv
import os
from ..utils import errors
import pathlib
import importlib
import inspect


load_dotenv()

class Bot(commands.Bot):

    def __init__(self, command_prefix, help_command, description=None, **options):
        super().__init__(command_prefix, help_command=help_command, description=description, **options)
        self.session: typing.Optional[aiohttp.ClientSession] = None
        self.INVALID_EXTENSIONS = ['__init__']


    @property
    def token(self) -> None:
        """Gets the token stored in .env file."""
        token = os.getenv('TOKEN')
        if not token:
            raise errors.EnvError('Error raised trying to get TOKEN.')

        return token

    @property
    def dsn(self) -> typing.Optional[str]:
        """Gets the dsn stored in .env file."""
        dsn = os.getenv('DSN')
        if not dsn:
            raise errors.EnvError('Error raise trying to get DSN.')
        return dsn

    def get_extensions_relative_path(self, path = 'source/exts') -> typing.Iterable:
        """Gets all extensions to load as an iterable."""
        print(os.listdir())
        for filename in os.listdir(path):
            if filename in self.INVALID_EXTENSIONS:
                continue
            iterable = pathlib.Path().glob(f'**/{filename}')
            paths = [pathlib_path for pathlib_path in iterable]
            if not paths:
                continue
            path = '.'.join(paths[0].parts)
            try:
                if not callable(importlib.import_module(path).setup) and not inspect.isfunction(importlib.import_module(path).setup):
                    continue
            except AttributeError:
                continue
            yield path.replace('.py', '')
        yield 'jishaku'

    def load_extensions(self, path='source/exts'):
        """Loads the extensions of the bot."""
        paths = [path for path in self.get_extensions_relative_path(path=path)]
        for path in paths:
            self.load_extension(path)
            print(f'Cog loaded: {path}')

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
