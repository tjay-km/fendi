"""Commands for the bot owner(s) only."""
import logging

import discord
from discord.ext import commands

from utils import helpers
from utils.config import COGS_DIR

log = logging.getLogger("fendi")


class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        if await self.bot.is_owner(ctx.author):
            return True
        raise commands.NotOwner("Only the bot owner can use that command.")

    # -------------------------------------------------------------- leaderboard
    @commands.command(name="reset_lb", aliases=["resetlb", "reset", "lb-reset", "reset-lb"],
                      description="Clears a server's message leaderboard (defaults to this server).")
    async def reset_lb(self, ctx, guild_id: int = None):
        guild = self.bot.get_guild(guild_id) if guild_id else ctx.guild
        if guild is None:
            return await ctx.send(embed=helpers.error_embed("Could not find that server."), delete_after=5)
        removed = await self.bot.db.reset_guild_messages(guild.id)
        log.info("Reset leaderboard for %s (%s): %s members cleared", guild.name, guild.id, removed)
        await ctx.send(embed=helpers.success_embed(f"Cleared **{removed}** members from {guild.name}'s leaderboard."))

    @commands.command(name="reset_user", aliases=["resetuser", "resetu", "user-reset", "reset-user"],
                      description="Clears a user's message count in this server.")
    async def reset_user(self, ctx, *, user: discord.User):
        if not await self.bot.db.reset_user_messages(ctx.guild.id, user.id):
            return await ctx.send(embed=helpers.info_embed(f"{user} has no messages recorded here."))
        log.info("Reset message count for %s (%s) in %s", user, user.id, ctx.guild.id)
        await ctx.send(embed=helpers.success_embed(f"Cleared {user.mention}'s message count."))

    # ------------------------------------------------------------------- servers
    @commands.command(name="servers", description="Lists the bot's 5 largest servers.")
    async def servers(self, ctx):
        largest = sorted(self.bot.guilds, key=lambda guild: guild.member_count, reverse=True)[:5]
        lines = [f"**{guild.name}** - {guild.member_count} members" for guild in largest]
        embed = discord.Embed(description="\n".join(lines) or "No servers.", colour=ctx.author.colour)
        embed.set_author(name=f"{self.bot.user.name}'s Top Servers", icon_url=self.bot.user.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(name="sleave", description="Makes the bot leave a server (defaults to this server).")
    async def sleave(self, ctx, guild_id: int = None):
        guild = self.bot.get_guild(guild_id) if guild_id else ctx.guild
        if guild is None:
            return await ctx.send(embed=helpers.error_embed("Could not find that server."), delete_after=5)
        if guild != ctx.guild:
            await ctx.send(embed=helpers.success_embed(f"Leaving **{guild.name}** ({guild.member_count} members)."))
        await guild.leave()

    # ----------------------------------------------------------------- the bot
    @commands.command(name="reload", description="Reloads one cog.")
    async def reload(self, ctx, cog: str):
        try:
            self.bot.reload_extension(f"cogs.{cog}")
        except commands.ExtensionError as error:
            return await ctx.send(embed=helpers.error_embed(f"Could not reload **{cog}**: {error}"))
        await ctx.send(embed=helpers.success_embed(f"Reloaded **{cog}**."))

    @commands.command(name="reloadall", description="Reloads every cog.")
    async def reloadall(self, ctx):
        failed = []
        for path in sorted(COGS_DIR.glob("*.py")):
            if path.name.startswith("_"):
                continue
            try:
                self.bot.reload_extension(f"cogs.{path.stem}")
            except commands.ExtensionError:
                log.exception("Could not reload cogs.%s", path.stem)
                failed.append(path.stem)
        if failed:
            return await ctx.send(embed=helpers.error_embed(f"Failed to reload: {', '.join(failed)}"))
        await ctx.send(embed=helpers.success_embed("Reloaded every cog."))

    @commands.command(name="toggle", description="Enables or disables a command.")
    async def toggle(self, ctx, *, command_name: str):
        command = self.bot.get_command(command_name)
        if command is None:
            return await ctx.send(embed=helpers.error_embed("That command doesn't exist."))
        if command == ctx.command:
            return await ctx.send(embed=helpers.error_embed("You can't disable this command."))
        command.enabled = not command.enabled
        state = "enabled" if command.enabled else "disabled"
        await ctx.send(embed=helpers.success_embed(f"**{command.qualified_name}** is now {state}."))

    @commands.command(name="logout", description="Shuts the bot down.")
    async def logout(self, ctx):
        await ctx.send(embed=helpers.success_embed("Logging out... \U0001f44b"))
        await self.bot.close()


def setup(bot):
    bot.add_cog(Owner(bot))
