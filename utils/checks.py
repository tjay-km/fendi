"""Permission checks.

* Bot owners come from ``OWNER_IDS`` (or the application owner when none are set)
  and use discord.py's built-in ``commands.is_owner()``.
* Bot admins are per-server and managed with the ``add_owner`` / ``remove_owner``
  commands. Bot owners are admins everywhere.
"""
from discord.ext import commands


async def user_is_admin(ctx: commands.Context) -> bool:
    if await ctx.bot.is_owner(ctx.author):
        return True
    return ctx.guild is not None and ctx.bot.db.is_admin(ctx.guild.id, ctx.author.id)


def is_admin():
    async def predicate(ctx: commands.Context) -> bool:
        if await user_is_admin(ctx):
            return True
        raise commands.CheckFailure("You need to be a bot admin in this server to use that command.")

    return commands.check(predicate)
