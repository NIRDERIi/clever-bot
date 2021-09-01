from __future__ import annotations
import aiohttp
from discord.ext import commands
from ..core import botbase


class ProcessError(commands.CommandError):

    pass


class BadStatus(Exception):
    def __init__(self, *args: object):
        super().__init__(*args)


class EnvError(Exception):

    pass


class StartUpError(Exception):

    pass
