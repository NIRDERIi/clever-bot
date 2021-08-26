from __future__ import annotations
from discord.ext import commands
from ..core import botbase

class ProcessError(commands.CommandError):

    pass


class EnvError(Exception):

    pass

class StartUpError(Exception):

    pass