"""Message-activity ranking.

Admins choose which channels are tracked; every message in a tracked channel
adds one to the author's count for that server.
"""
import discord
from discord.ext import commands, tasks

from utils import helpers
from utils.checks import is_admin

FLUSH_INTERVAL_SECONDS = 30


class Ranking(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.flush_counts.start()

    def cog_unload(self):
        self.flush_counts.cancel()

    @tasks.loop(seconds=FLUSH_INTERVAL_SECONDS)
    async def flush_counts(self):
        """Commit message counts in batches instead of on every message."""
        await self.bot.db.flush()

    @flush_counts.before_loop
    async def _before_flush(self):
        await self.bot.wait_until_ready()

    # --------------------------------------------------------------- listeners
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or message.guild is None:
            return
        if self.bot.db.is_tracked(message.channel.id):
            await self.bot.db.add_message(message.guild.id, message.author.id)

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        await self.bot.db.reset_user_messages(member.guild.id, member.id)

    # ---------------------------------------------------------------- commands
    @commands.command(name="rank", aliases=["lvl", "msgs"], description="Shows a member's message count and rank.")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def rank(self, ctx, *, member: discord.Member = None):
        member = member or ctx.author
        if member.bot:
            return await ctx.send(embed=helpers.info_embed("Bots don't have a rank. We're above all that."))

        count, rank, total = await self.bot.db.message_stats(ctx.guild.id, member.id)
        if count == 0:
            return await ctx.send(embed=helpers.info_embed(f"**{member.display_name}** hasn't sent any tracked messages yet."))

        embed = discord.Embed(
            description=f"**{member.display_name}** has **{count}** messages.\n"
                        f"Rank **#{rank}** on the {ctx.guild.name} leaderboard.",
            colour=helpers.COLOUR_NEUTRAL,
        )
        embed.set_author(name=f"{member} | Rank", icon_url=member.avatar_url)
        helpers.set_thumbnail(embed, ctx.guild.icon_url)
        embed.set_footer(text=f"#{rank} of {total} members")
        await ctx.send(embed=embed)

    @commands.command(name="leaderboard", aliases=["lb"], description="Shows the 10 most active members.")
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def leaderboard(self, ctx):
        rows = await self.bot.db.leaderboard(ctx.guild.id)
        if not rows:
            return await ctx.send(embed=helpers.info_embed("Nobody has sent a tracked message yet."))

        lines = [f"**{index}.** <@{user_id}>: **{count}** messages" for index, (user_id, count) in enumerate(rows, start=1)]
        embed = discord.Embed(title=f"{ctx.guild.name}'s Activity Leaderboard", description="\n".join(lines),
                              colour=helpers.COLOUR_NEUTRAL)
        helpers.set_thumbnail(embed, ctx.guild.icon_url)
        await ctx.send(embed=embed)

    @commands.command(name="whitelist", aliases=["wlist", "wl"], description="Starts tracking messages in a channel.")
    @is_admin()
    async def whitelist(self, ctx, channel: discord.TextChannel):
        if not await self.bot.db.track_channel(ctx.guild.id, channel.id):
            return await ctx.send(embed=helpers.info_embed(f"{channel.mention} is already tracked."))
        await ctx.send(content=f"Now tracking {channel.mention}.", embed=await self._tracked_embed(ctx))

    @commands.command(name="blacklist", aliases=["unwhitelist", "delwhitelist", "bl"],
                      description="Stops tracking messages in a channel.")
    @is_admin()
    async def blacklist(self, ctx, channel: discord.TextChannel):
        if not await self.bot.db.untrack_channel(ctx.guild.id, channel.id):
            return await ctx.send(embed=helpers.info_embed(f"{channel.mention} isn't tracked."))
        await ctx.send(content=f"Stopped tracking {channel.mention}.", embed=await self._tracked_embed(ctx))

    @commands.command(name="whitelisted", aliases=["channels", "wlisted"], description="Lists the tracked channels.")
    @is_admin()
    async def whitelisted(self, ctx):
        await ctx.send(embed=await self._tracked_embed(ctx))

    async def _tracked_embed(self, ctx) -> discord.Embed:
        channels = await self.bot.db.tracked_channels(ctx.guild.id)
        if not channels:
            return helpers.info_embed(f"No channels are tracked in **{ctx.guild.name}**.")
        embed = discord.Embed(title=f"{ctx.guild.name}'s Tracked Channels",
                              description=helpers.numbered_mentions(channels, kind="#"),
                              colour=helpers.COLOUR_NEUTRAL)
        helpers.set_thumbnail(embed, ctx.guild.icon_url)
        return embed


def setup(bot):
    bot.add_cog(Ranking(bot))
