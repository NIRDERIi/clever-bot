from __future__ import annotations
from source.core import botbase

if __name__ == "__main__":
    bot = botbase.Bot(command_prefix="m!", help_command=None)
    bot.run(bot.token)
