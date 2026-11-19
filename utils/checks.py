"""Permission checks shared by every cog."""
import aiosqlite

from utils.config import OWNER_IDS, db_path


async def is_owner(ctx):
    """True for the bot owner(s) listed in the config."""
    return ctx.author.id in OWNER_IDS


async def is_admin(ctx):
    """True for the bot owner(s) and for users added with the add_owner command."""
    if ctx.author.id in OWNER_IDS:
        return True
    if ctx.guild is None:
        return False
    async with aiosqlite.connect(db_path("admin")) as db:
        await db.execute("CREATE TABLE IF NOT EXISTS owners (guild INTEGER, user INTEGER)")
        async with db.execute(
            "SELECT 1 FROM owners WHERE guild = ? AND user = ?", (ctx.guild.id, ctx.author.id)
        ) as cursor:
            return await cursor.fetchone() is not None
