"""Per-server settings: command prefix and bot admins."""
import discord
from discord.ext import commands

from utils import helpers
from utils.checks import is_admin

MAX_PREFIX_LENGTH = 5


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="setprefix", aliases=["set-prefix"], description="Changes the bot's prefix for this server.")
    @is_admin()
    @commands.has_permissions(manage_guild=True)
    async def setprefix(self, ctx, prefix: str = None):
        current = self.bot.db.prefix_for(ctx.guild.id)
        if prefix is None:
            return await ctx.send(embed=helpers.info_embed(
                f"You haven't entered a new prefix.\nThe current prefix is `{current}`."
            ))
        if len(prefix) > MAX_PREFIX_LENGTH:
            return await ctx.send(embed=helpers.error_embed(
                f"Prefixes can be at most {MAX_PREFIX_LENGTH} characters long."
            ))

        await self.bot.db.set_prefix(ctx.guild.id, prefix)
        await ctx.send(embed=helpers.success_embed(f"Updated the prefix for **{ctx.guild.name}** to `{prefix}`."))

    @commands.command(name="prefix", description="Shows the bot's prefix for this server.")
    @commands.cooldown(1, 60, commands.BucketType.channel)
    async def prefix(self, ctx):
        embed = discord.Embed(title="Prefix Settings", description=f"`{self.bot.db.prefix_for(ctx.guild.id)}`")
        embed.set_author(name=f"{ctx.guild.name}'s Prefix", icon_url=ctx.author.avatar_url)
        helpers.set_thumbnail(embed, ctx.guild.icon_url)
        await ctx.send(embed=embed)

    @commands.command(name="add_owner", aliases=["add-owner", "owner", "add"],
                      description="Makes a member a bot admin in this server.")
    @is_admin()
    async def add_owner(self, ctx, *, member: discord.Member):
        if member.bot:
            return await ctx.send(embed=helpers.error_embed("You can't make a bot an admin."))
        if not await self.bot.db.add_admin(ctx.guild.id, member.id):
            return await ctx.send(embed=helpers.info_embed(f"{member.mention} is already a bot admin."))
        await ctx.send(
            content=f"Added {member.mention} to the bot admins.",
            embed=self._admin_list_embed(ctx),
        )

    @commands.command(name="remove_owner", aliases=["remove-owner", "remove"],
                      description="Removes a member from this server's bot admins.")
    @is_admin()
    async def remove_owner(self, ctx, *, member: discord.Member):
        if not await self.bot.db.remove_admin(ctx.guild.id, member.id):
            return await ctx.send(embed=helpers.error_embed(f"{member.mention} isn't a bot admin."))
        await ctx.send(embed=helpers.success_embed(f"Removed {member.mention} from the bot admins."))

    @commands.command(name="owners", aliases=["owners-list"], description="Lists this server's bot admins.")
    @is_admin()
    async def owners(self, ctx):
        if not self.bot.db.admins(ctx.guild.id):
            return await ctx.send(embed=helpers.info_embed(f"There are no bot admins in **{ctx.guild.name}**."))
        await ctx.send(embed=self._admin_list_embed(ctx))

    def _admin_list_embed(self, ctx) -> discord.Embed:
        embed = discord.Embed(
            title=f"{ctx.guild.name}'s Bot Admins",
            description=helpers.numbered_mentions(self.bot.db.admins(ctx.guild.id)),
            colour=helpers.COLOUR_NEUTRAL,
        )
        helpers.set_thumbnail(embed, ctx.guild.icon_url)
        return embed


def setup(bot):
    bot.add_cog(Admin(bot))
