"""Utility commands: emoji enlarging, Urban Dictionary, reverse image search and sniping."""
import datetime
import re
from urllib.parse import quote
from typing import Dict, Optional

import aiohttp
import discord
from discord.ext import commands

from utils import helpers

URBAN_API = "https://api.urbandictionary.com/v0/define"
REVERSE_SEARCH_URL = "https://lens.google.com/uploadbyurl?url={}"
MAX_DESCRIPTION = 2000
BLOCKED_SNIPE_TEXT = ("discord.gg/", "discord.com/invite/", "/invite/")


def _shorten(text: str, limit: int = MAX_DESCRIPTION) -> str:
    return text if len(text) <= limit else text[: limit - 1] + "…"


class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._deleted: Dict[int, dict] = {}
        self._edited: Dict[int, dict] = {}

    # ----------------------------------------------------------------- tools
    @commands.command(name="enlarge", aliases=["resize"], description="Shows a custom emoji at full size.")
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def enlarge(self, ctx, emoji: discord.PartialEmoji):
        embed = discord.Embed(colour=ctx.author.colour)
        embed.set_author(name=f":{emoji.name}:", icon_url=self.bot.user.avatar_url)
        embed.set_image(url=str(emoji.url))
        await ctx.send(embed=embed)

    @commands.command(name="urban", aliases=["ud"], description="Looks a term up on Urban Dictionary.")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def urban(self, ctx, *, term: str):
        data = None
        try:
            async with self.bot.http_session.get(URBAN_API, params={"term": term}) as response:
                if response.status == 200:
                    data = await response.json()
        except aiohttp.ClientError:
            pass
        if data is None:
            return await ctx.send(embed=helpers.error_embed("Urban Dictionary is unavailable right now."))

        definitions = data.get("list") or []
        if not definitions:
            return await ctx.send(embed=helpers.error_embed(f"No Urban Dictionary entry for **{term}**."))

        entry = definitions[0]
        embed = discord.Embed(
            title=entry["word"],
            url=entry.get("permalink") or discord.Embed.Empty,
            description=_shorten(re.sub(r"[\[\]]", "", entry["definition"])),
            colour=ctx.author.colour,
        )
        embed.add_field(name="Author", value=entry.get("author") or "Unknown")
        embed.add_field(name="Written", value=(entry.get("written_on") or "")[:10] or "Unknown")
        embed.set_footer(text=f"\U0001f44d {entry.get('thumbs_up', 0)} | \U0001f44e {entry.get('thumbs_down', 0)}")
        await ctx.send(embed=embed)

    @commands.command(name="revav", description="Reverse image searches a member's avatar.")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def revav(self, ctx, *, member: discord.Member = None):
        member = member or ctx.author
        avatar = str(member.avatar_url_as(static_format="png", size=1024))
        embed = discord.Embed(
            description=f"[Reverse search {member.display_name}'s avatar]({REVERSE_SEARCH_URL.format(quote(avatar, safe=''))})",
            colour=ctx.author.colour,
        )
        embed.set_thumbnail(url=avatar)
        await ctx.send(embed=embed)

    # ------------------------------------------------------------------ snipe
    @commands.command(name="snipe", aliases=["s"], description="Shows the last deleted message in this channel.")
    async def snipe(self, ctx):
        entry = self._deleted.get(ctx.channel.id)
        if entry is None:
            return await ctx.send(embed=helpers.error_embed("Nothing to snipe!"), delete_after=5)

        embed = discord.Embed(description=entry["content"], timestamp=entry["at"], colour=ctx.author.colour)
        embed.set_author(name=entry["author"], icon_url=entry["avatar"])
        if entry["image"]:
            embed.set_image(url=entry["image"])
        await ctx.send(embed=embed)

    @commands.command(name="editsnipe", aliases=["esnipe"], description="Shows the last edited message in this channel.")
    async def editsnipe(self, ctx):
        entry = self._edited.get(ctx.channel.id)
        if entry is None:
            return await ctx.send(embed=helpers.error_embed("Nothing to snipe!"), delete_after=5)

        embed = discord.Embed(
            description=_shorten(f"**Before**\n{entry['before']}\n**After**\n{entry['after']}"),
            timestamp=entry["at"],
            colour=ctx.author.colour,
        )
        embed.set_author(name=entry["author"], icon_url=entry["avatar"])
        await ctx.send(embed=embed)

    @staticmethod
    def _snipeable(message: discord.Message) -> bool:
        if message.author.bot or message.guild is None:
            return False
        content = message.content.lower()
        return not any(blocked in content for blocked in BLOCKED_SNIPE_TEXT)

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if not self._snipeable(message):
            return
        image: Optional[str] = message.attachments[0].proxy_url if message.attachments else None
        self._deleted[message.channel.id] = {
            "author": str(message.author),
            "avatar": str(message.author.avatar_url),
            "content": _shorten(message.content),
            "image": image,
            "at": datetime.datetime.utcnow(),
        }

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        if before.content == after.content or not self._snipeable(before) or not self._snipeable(after):
            return
        self._edited[before.channel.id] = {
            "author": str(before.author),
            "avatar": str(before.author.avatar_url),
            "before": before.content,
            "after": after.content,
            "at": after.edited_at or datetime.datetime.utcnow(),
        }


def setup(bot):
    bot.add_cog(Utility(bot))
