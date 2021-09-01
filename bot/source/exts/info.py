import typing
from discord.ext import commands
from ..core import botbase, context
import discord


class Info(commands.Cog):
    def __init__(self, bot: botbase.Bot):
        self.bot = bot

    @commands.command(name="is-blacklisted")
    async def is_blacklisted(self, ctx: context.CustomContext):
        is_guild_blacklisted = await self.bot.is_blacklisted(ctx.guild.id)
        is_user_blacklisted = await self.bot.is_blacklisted(ctx.author.id)
        embed = self.bot.build_embed(
            user=ctx.author,
            description=f"**Guild blacklisted:** `{is_guild_blacklisted}`\n**User blacklisted**: `{is_user_blacklisted}`",
        )
        await ctx.send(embed=embed)


def setup(bot: botbase.Bot):
    bot.add_cog(Info(bot=bot))
