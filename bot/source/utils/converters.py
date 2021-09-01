from discord.ext import commands
from ..core import context
import textwrap


class CodeConverter(commands.Converter):
    def __init__(self, add_function: bool = False):
        self.add_function = add_function

    async def convert(self, ctx: context.CustomContext, argument: str):

        if argument.startswith("```py") and argument.endswith("```"):
            argument = argument[5:-3]

        if self.add_function:

            argument: str = (
                f'async def eval_job_function():\n{textwrap.indent(argument, "    ")}'
            )
        return argument
