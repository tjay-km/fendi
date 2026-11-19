"""Per-guild command prefix lookup."""
import aiosqlite

from utils.config import DEFAULT_PREFIX, db_path


async def get_prefix(client, message):
    """Return the prefix for the message's guild, storing the default on first use."""
    guild = getattr(message, "guild", None)
    if guild is None:
        return DEFAULT_PREFIX
    async with aiosqlite.connect(db_path("prefix")) as db:
        await db.execute("CREATE TABLE IF NOT EXISTS prefixes (guild INTEGER, prefix TEXT, UNIQUE(guild))")
        async with db.execute("SELECT prefix FROM prefixes WHERE guild = ?", (guild.id,)) as cursor:
            row = await cursor.fetchone()
        if row:
            return row[0]
        await db.execute("REPLACE INTO prefixes (guild, prefix) VALUES (?, ?)", (guild.id, DEFAULT_PREFIX))
        await db.commit()
        return DEFAULT_PREFIX
