"""Random "rating" commands. All results are random and just for fun."""
import random

import discord
from discord.ext import commands

from utils import helpers


def _subject(ctx, member: discord.Member):
    """Return the target member and how to address them ("You are" / "Name is")."""
    member = member or ctx.author
    return member, "You are" if member == ctx.author else f"{member.display_name} is"


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def _send_rating(self, ctx, text: str) -> None:
        await ctx.send(embed=discord.Embed(description=text, colour=helpers.COLOUR_NEUTRAL))

    @commands.command(name="pp", description="Measures a member's pp.")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def pp(self, ctx, *, member: discord.Member = None):
        member, _ = _subject(ctx, member)
        owner = "Your" if member == ctx.author else f"{member.display_name}'s"
        embed = discord.Embed(title=f"{owner} pp", description=f"8{'=' * random.randint(1, 15)}D",
                              colour=helpers.COLOUR_NEUTRAL)
        await ctx.send(embed=embed)

    @commands.command(name="iq", description="Rates a member's IQ.")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def iq(self, ctx, *, member: discord.Member = None):
        _, subject = _subject(ctx, member)
        await self._send_rating(ctx, f"{subject} working with an IQ of **{random.randint(1, 200)}**.")

    @commands.command(name="height", description="Guesses a member's height.")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def height(self, ctx, *, member: discord.Member = None):
        _, subject = _subject(ctx, member)
        await self._send_rating(ctx, f"{subject} **{random.randint(4, 7)}'{random.randint(0, 11)}\"** tall.")


def setup(bot):
    bot.add_cog(Fun(bot))
