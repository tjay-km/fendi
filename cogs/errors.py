"""Turns command errors into short, friendly replies and logs unexpected ones."""
import logging

import discord
from discord.ext import commands

from utils import helpers

log = logging.getLogger("fendi")

IGNORED = (commands.CommandNotFound, commands.NoPrivateMessage, discord.Forbidden, discord.NotFound)
NOT_FOUND = (commands.MemberNotFound, commands.UserNotFound, commands.ChannelNotFound,
             commands.RoleNotFound, commands.PartialEmojiConversionFailure)


class Errors(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
        error = getattr(error, "original", error)
        name = ctx.author.display_name

        if isinstance(error, IGNORED):
            return
        if isinstance(error, commands.CommandOnCooldown):
            message = f"That command is on cooldown. Try again in {helpers.humanize_seconds(error.retry_after)}."
        elif isinstance(error, commands.MissingRequiredArgument):
            message = f"**{error.param.name}** is a required argument."
        elif isinstance(error, NOT_FOUND):
            message = str(error)
        elif isinstance(error, commands.BadArgument):
            message = f"Invalid argument: {error}"
        elif isinstance(error, commands.MissingPermissions):
            message = f"**{name}**, you're missing the permissions to do that."
        elif isinstance(error, commands.BotMissingPermissions):
            message = f"**{self.bot.user.name}** is missing the permissions to do that."
        elif isinstance(error, commands.DisabledCommand):
            message = "That command is disabled."
        elif isinstance(error, commands.CheckFailure):
            message = str(error) or f"**{name}**, you don't have access to that command."
        else:
            log.error("Error in command %s", ctx.command, exc_info=(type(error), error, error.__traceback__))
            message = "Something went wrong running that command."

        await ctx.send(embed=helpers.error_embed(message), delete_after=8)


def setup(bot):
    bot.add_cog(Errors(bot))
