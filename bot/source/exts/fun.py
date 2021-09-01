import discord
from discord.ext import commands
from ..core import botbase, context
from ..utils import converters, errors, functions


class Fun(commands.Cog):
    def __init__(self, bot: botbase.Bot):
        self.bot = bot
        self.snekbox_url: str = "http://localhost:8060/eval"

    @commands.command(description="Runs Python code.", aliases=["exec", "execute"])
    async def run(
        self,
        ctx: context.CustomContext,
        *,
        code: converters.CodeConverter(add_function=False),
    ):
        try:
            async with self.bot.session.post(
                url=self.snekbox_url, json={"input": code}
            ) as response:

                if response.status != 200:

                    raise errors.ProcessError(
                        f"Calling snekbox returned a bad status code: `{response.status}`"
                    )
                data = await response.json()
                print(data)
                stdout: str = data.get("stdout")
                return_code = data.get("returncode")
                lines = stdout.splitlines()
                too_long = False
                if len(lines) > 10:
                    too_long = True
                output = "\n".join(
                    [
                        f"{str(index + 1).zfill(3)} | {line}"
                        for index, line in enumerate(lines[:10])
                    ]
                )
                if return_code == 0:
                    emoji = ":white_check_mark:"
                else:
                    emoji = ":x:"
                if not output:
                    output = "[No output]"
                    emoji = ":warning:"
                if return_code == 137:
                    content = f"{ctx.author.mention} {emoji}, your eval job ran out of memory."
                else:
                    content = f"{ctx.author.mention} {emoji}, your eval job returned code {return_code}."
                if too_long:
                    output += "\n... | (too many lines)"
                if stdout == "":
                    output = "[No output]"
                content += f"\n```\n{output}\n```"
                if too_long:
                    url = await functions.paste(
                        self.bot, "\n".join([line for _, line in enumerate(lines)])
                    )
                    content += f"\nFull output in: {url}"
                await ctx.send(content=content)
        except Exception as error:
            raise errors.ProcessError("Docker container is currently down.")


def setup(bot: botbase.Bot):
    bot.add_cog(Fun(bot))
