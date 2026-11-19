"""SQLite storage shared by every cog.

A single connection is opened when the bot starts. Values read on every message
(prefixes, tracked channels) and on every command (bot admins) are cached in
memory, so the hot paths never touch the disk.
"""
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import aiosqlite

SCHEMA = """
PRAGMA journal_mode = WAL;

CREATE TABLE IF NOT EXISTS prefixes (
    guild  INTEGER PRIMARY KEY,
    prefix TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS admins (
    guild INTEGER NOT NULL,
    user  INTEGER NOT NULL,
    PRIMARY KEY (guild, user)
);

CREATE TABLE IF NOT EXISTS tracked_channels (
    channel INTEGER PRIMARY KEY,
    guild   INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_tracked_channels_guild ON tracked_channels (guild);

CREATE TABLE IF NOT EXISTS messages (
    guild         INTEGER NOT NULL,
    user          INTEGER NOT NULL,
    message_count INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (guild, user)
);
CREATE INDEX IF NOT EXISTS idx_messages_leaderboard ON messages (guild, message_count DESC);
"""


class Database:
    def __init__(self, path: Path, default_prefix: str):
        self._path = path
        self._default_prefix = default_prefix
        self._conn: Optional[aiosqlite.Connection] = None
        self._prefixes: Dict[int, str] = {}
        self._admins: Dict[int, Set[int]] = {}
        self._tracked: Set[int] = set()
        self._pending_writes = False

    # ------------------------------------------------------------------ setup
    async def connect(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = await aiosqlite.connect(str(self._path))
        await self._conn.executescript(SCHEMA)
        await self._conn.commit()

        self._prefixes = dict(await self._fetchall("SELECT guild, prefix FROM prefixes"))
        for guild, user in await self._fetchall("SELECT guild, user FROM admins"):
            self._admins.setdefault(guild, set()).add(user)
        self._tracked = {channel for (channel,) in await self._fetchall("SELECT channel FROM tracked_channels")}

    async def close(self) -> None:
        if self._conn is not None:
            await self.flush()
            await self._conn.close()
            self._conn = None

    @property
    def _db(self) -> aiosqlite.Connection:
        if self._conn is None:
            raise RuntimeError("Database is not connected.")
        return self._conn

    async def _fetchall(self, sql: str, params: tuple = ()) -> List[tuple]:
        async with self._db.execute(sql, params) as cursor:
            return list(await cursor.fetchall())

    async def _scalar(self, sql: str, params: tuple = ()):
        async with self._db.execute(sql, params) as cursor:
            row = await cursor.fetchone()
        return row[0] if row else None

    async def _write(self, sql: str, params: tuple = ()) -> int:
        """Run one statement, commit, and return the number of affected rows."""
        async with self._db.execute(sql, params) as cursor:
            affected = cursor.rowcount
        await self._db.commit()
        return affected

    async def flush(self) -> None:
        """Commit batched message-count updates."""
        if self._pending_writes:
            await self._db.commit()
            self._pending_writes = False

    # --------------------------------------------------------------- prefixes
    def prefix_for(self, guild_id: int) -> str:
        return self._prefixes.get(guild_id, self._default_prefix)

    async def set_prefix(self, guild_id: int, prefix: str) -> None:
        if prefix == self._default_prefix:
            await self._write("DELETE FROM prefixes WHERE guild = ?", (guild_id,))
            self._prefixes.pop(guild_id, None)
            return
        await self._write(
            "INSERT INTO prefixes (guild, prefix) VALUES (?, ?) "
            "ON CONFLICT (guild) DO UPDATE SET prefix = excluded.prefix",
            (guild_id, prefix),
        )
        self._prefixes[guild_id] = prefix

    # ----------------------------------------------------------------- admins
    def is_admin(self, guild_id: int, user_id: int) -> bool:
        return user_id in self._admins.get(guild_id, ())

    def admins(self, guild_id: int) -> List[int]:
        return sorted(self._admins.get(guild_id, ()))

    async def add_admin(self, guild_id: int, user_id: int) -> bool:
        added = await self._write("INSERT OR IGNORE INTO admins (guild, user) VALUES (?, ?)", (guild_id, user_id))
        self._admins.setdefault(guild_id, set()).add(user_id)
        return added > 0

    async def remove_admin(self, guild_id: int, user_id: int) -> bool:
        removed = await self._write("DELETE FROM admins WHERE guild = ? AND user = ?", (guild_id, user_id))
        self._admins.get(guild_id, set()).discard(user_id)
        return removed > 0

    # ------------------------------------------------------- tracked channels
    def is_tracked(self, channel_id: int) -> bool:
        return channel_id in self._tracked

    async def tracked_channels(self, guild_id: int) -> List[int]:
        rows = await self._fetchall("SELECT channel FROM tracked_channels WHERE guild = ? ORDER BY channel", (guild_id,))
        return [channel for (channel,) in rows]

    async def track_channel(self, guild_id: int, channel_id: int) -> bool:
        added = await self._write(
            "INSERT OR IGNORE INTO tracked_channels (channel, guild) VALUES (?, ?)", (channel_id, guild_id)
        )
        self._tracked.add(channel_id)
        return added > 0

    async def untrack_channel(self, guild_id: int, channel_id: int) -> bool:
        removed = await self._write(
            "DELETE FROM tracked_channels WHERE channel = ? AND guild = ?", (channel_id, guild_id)
        )
        self._tracked.discard(channel_id)
        return removed > 0

    # --------------------------------------------------------- message counts
    async def add_message(self, guild_id: int, user_id: int) -> None:
        """Count one message. Committed in batches by :meth:`flush`."""
        async with self._db.execute(
            "INSERT INTO messages (guild, user, message_count) VALUES (?, ?, 1) "
            "ON CONFLICT (guild, user) DO UPDATE SET message_count = message_count + 1",
            (guild_id, user_id),
        ):
            pass
        self._pending_writes = True

    async def message_stats(self, guild_id: int, user_id: int) -> Tuple[int, int, int]:
        """Return ``(message_count, rank, ranked_users)`` for a member."""
        count = await self._scalar(
            "SELECT message_count FROM messages WHERE guild = ? AND user = ?", (guild_id, user_id)
        ) or 0
        rank = await self._scalar(
            "SELECT COUNT(*) + 1 FROM messages WHERE guild = ? AND message_count > ?", (guild_id, count)
        )
        total = await self._scalar("SELECT COUNT(*) FROM messages WHERE guild = ?", (guild_id,))
        return count, rank, total

    async def leaderboard(self, guild_id: int, limit: int = 10) -> List[Tuple[int, int]]:
        """Return ``(user_id, message_count)`` pairs, highest first."""
        return await self._fetchall(
            "SELECT user, message_count FROM messages WHERE guild = ? ORDER BY message_count DESC LIMIT ?",
            (guild_id, limit),
        )

    async def reset_guild_messages(self, guild_id: int) -> int:
        return await self._write("DELETE FROM messages WHERE guild = ?", (guild_id,))

    async def reset_user_messages(self, guild_id: int, user_id: int) -> int:
        return await self._write("DELETE FROM messages WHERE guild = ? AND user = ?", (guild_id, user_id))

    # ------------------------------------------------------------------ guilds
    async def purge_guild(self, guild_id: int) -> None:
        """Delete everything stored for a guild."""
        for table in ("prefixes", "admins", "tracked_channels", "messages"):
            async with self._db.execute(f"DELETE FROM {table} WHERE guild = ?", (guild_id,)):
                pass
        await self._db.commit()

        self._prefixes.pop(guild_id, None)
        self._admins.pop(guild_id, None)
        self._tracked = {channel for (channel,) in await self._fetchall("SELECT channel FROM tracked_channels")}
