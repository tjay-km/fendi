"""Fendi - a multipurpose Discord bot built on discord.py 1.7.3.

Run with ``python fendi.py``. See README.md for configuration.
"""
import datetime
import logging

import aiohttp
import colorama
import discord
from colorama import Fore
from discord.ext import commands

from utils import helpers
from utils.checks import user_is_admin
from utils.config import COGS_DIR, DB_FILE, DEFAULT_PREFIX, OWNER_IDS, TOKEN
from utils.database import Database

log = logging.getLogger("fendi")


class Fendi(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=DEFAULT_PREFIX,
            description="Fendi commands",
            help_command=None,
            case_insensitive=True,
            intents=discord.Intents.all(),
            owner_ids=set(OWNER_IDS),
        )
        self.db = Database(DB_FILE, DEFAULT_PREFIX)
        self.http_session = None  # type: aiohttp.ClientSession
        self.start_time = datetime.datetime.utcnow()
        self._ready_once = False

        self.add_check(self._guild_only)
        self.after_invoke(self._admins_skip_cooldowns)

    # --------------------------------------------------------------- lifecycle
    async def start(self, *args, **kwargs):
        await self.db.connect()
        self.http_session = aiohttp.ClientSession()
        await super().start(*args, **kwargs)

    async def close(self):
        try:
            await super().close()
        finally:
            if self.http_session is not None:
                await self.http_session.close()
            await self.db.close()

    def load_cogs(self) -> None:
        names = sorted(path.stem for path in COGS_DIR.glob("*.py") if not path.name.startswith("_"))
        for index, name in enumerate(names):
            helpers.progress_bar(index, len(names), "Loading cogs")
            try:
                self.load_extension(f"cogs.{name}")
            except commands.ExtensionError:
                log.exception("Could not load cogs.%s", name)

    # ------------------------------------------------------------------ hooks
    async def get_prefix(self, message):
        prefix = self.db.prefix_for(message.guild.id) if message.guild else DEFAULT_PREFIX
        return commands.when_mentioned_or(prefix)(self, message)

    @staticmethod
    def _guild_only(ctx: commands.Context) -> bool:
        if ctx.guild is None:
            raise commands.NoPrivateMessage()
        return True

    async def _admins_skip_cooldowns(self, ctx: commands.Context) -> None:
        if ctx.command is not None and await user_is_admin(ctx):
            ctx.command.reset_cooldown(ctx)

    # ----------------------------------------------------------------- events
    async def on_ready(self):
        if self._ready_once:
            log.info("Reconnected as %s", self.user)
            return
        self._ready_once = True

        helpers.clear_console()
        helpers.print_banner()
        log.info("Logged in as %s (%s)", self.user, self.user.id)
        log.info("Serving %s servers with %s members", len(self.guilds), sum(g.member_count for g in self.guilds))
        log.info("Default prefix: %s", DEFAULT_PREFIX)
        log.info("Invite: %s", discord.utils.oauth_url(self.user.id, permissions=discord.Permissions(8)))

    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        await self.process_commands(message)

        if message.guild and message.content.strip() in (f"<@{self.user.id}>", f"<@!{self.user.id}>"):
            prefix = self.db.prefix_for(message.guild.id)
            await message.channel.send(embed=helpers.info_embed(f"My prefix here is `{prefix}`"), delete_after=30)

    async def on_command(self, ctx: commands.Context):
        log.info("[%s] #%s %s: %s", ctx.guild, ctx.channel, ctx.author, ctx.message.content)

    async def on_guild_join(self, guild: discord.Guild):
        log.info("Joined %s (%s) with %s members", guild.name, guild.id, guild.member_count)
        await self.db.purge_guild(guild.id)  # drop data left over from an earlier stay

    async def on_guild_remove(self, guild: discord.Guild):
        log.info("Removed from %s (%s)", guild.name, guild.id)
        await self.db.purge_guild(guild.id)


def main() -> None:
    colorama.init()
    logging.basicConfig(
        format=f"[{Fore.RED}%(asctime)s{Fore.RESET}] %(message)s",
        datefmt="%d-%m-%Y %H:%M:%S",
        level=logging.INFO,
    )
    if not TOKEN:
        raise SystemExit(
            "No bot token found. Set DISCORD_TOKEN or copy info/config.example.json "
            "to info/config.json and fill it in."
        )

    helpers.set_console_title("Fendi Bot")
    bot = Fendi()
    bot.load_cogs()
    bot.run(TOKEN)


if __name__ == "__main__":
    main()
