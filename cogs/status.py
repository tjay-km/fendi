"""Bot presence: a default status plus optional cycling through a list of statuses.

Settings persist in ``data/status.json``.
"""
import json
import random

import discord
from discord.ext import commands, tasks

from utils import helpers
from utils.config import STATUS_FILE, STREAM_URL

MIN_DELAY_SECONDS = 12  # Discord rate-limits presence updates
DEFAULT_SETTINGS = {"default": "fendi", "cycling": False, "delay": 30, "statuses": []}
ACTIVITY_TYPES = (
    discord.ActivityType.playing,
    discord.ActivityType.watching,
    discord.ActivityType.listening,
    discord.ActivityType.streaming,
)
ONLINE_STATUSES = (discord.Status.online, discord.Status.idle, discord.Status.dnd)


def _load_settings() -> dict:
    try:
        stored = json.loads(STATUS_FILE.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        stored = {}
    return {**DEFAULT_SETTINGS, **stored}


def _split_statuses(text: str):
    return [item.strip() for item in text.split(";") if item.strip()]


def _activity(name: str, activity_type: discord.ActivityType) -> discord.BaseActivity:
    if activity_type is discord.ActivityType.streaming:
        return discord.Streaming(name=name, url=STREAM_URL)
    return discord.Activity(type=activity_type, name=name)


class Status(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.settings = _load_settings()
        self.cycle_statuses.change_interval(seconds=self.settings["delay"])
        if bot.is_ready() and self.settings["cycling"]:  # reloaded while running
            self.cycle_statuses.start()

    async def cog_check(self, ctx):
        if await self.bot.is_owner(ctx.author):
            return True
        raise commands.NotOwner("Only the bot owner can use that command.")

    def cog_unload(self):
        self.cycle_statuses.cancel()

    def _save(self) -> None:
        STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)
        STATUS_FILE.write_text(json.dumps(self.settings, indent=4), encoding="utf-8")

    async def _apply_default(self) -> None:
        await self.bot.change_presence(activity=_activity(self.settings["default"], discord.ActivityType.streaming))

    def _status_list(self) -> str:
        return "\n".join(f"• {name}" for name in self.settings["statuses"]) or "None"

    # ---------------------------------------------------------------- presence
    @tasks.loop(seconds=DEFAULT_SETTINGS["delay"])
    async def cycle_statuses(self):
        if not self.settings["statuses"]:
            return
        activity = _activity(random.choice(self.settings["statuses"]), random.choice(ACTIVITY_TYPES))
        await self.bot.change_presence(activity=activity, status=random.choice(ONLINE_STATUSES))

    @cycle_statuses.before_loop
    async def _before_cycle(self):
        await self.bot.wait_until_ready()

    @commands.Cog.listener()
    async def on_ready(self):
        if self.settings["cycling"] and self.settings["statuses"]:
            if not self.cycle_statuses.is_running():
                self.cycle_statuses.start()
        else:
            await self._apply_default()

    # ---------------------------------------------------------------- commands
    @commands.command(name="cycles", aliases=["cycle-info"], description="Lists the cycling statuses and delay.")
    async def cycles(self, ctx):
        embed = discord.Embed(title="Statuses", colour=helpers.random_colour())
        embed.add_field(name="Cycling", value="On" if self.settings["cycling"] else "Off", inline=True)
        embed.add_field(name="Delay", value=f"{self.settings['delay']}s", inline=True)
        embed.add_field(name="Default", value=self.settings["default"], inline=True)
        embed.add_field(name="Statuses", value=self._status_list(), inline=False)
        await ctx.send(embed=embed)

    @commands.command(name="cycles_add", aliases=["cycles-add", "cyclesadd", "add-cycle", "cycle-add", "addcycles",
                                                  "add-cycles", "cycleadd", "addcycle"],
                      description="Adds statuses to the cycle. Separate several with ';'.")
    async def cycles_add(self, ctx, *, statuses: str):
        new = [name for name in _split_statuses(statuses) if name not in self.settings["statuses"]]
        if not new:
            return await ctx.send(embed=helpers.error_embed("Those statuses are already in the cycle."))
        self.settings["statuses"].extend(new)
        self._save()
        embed = helpers.success_embed(f"Added {len(new)} status(es).")
        embed.add_field(name="All Statuses", value=self._status_list())
        await ctx.send(embed=embed)

    @commands.command(name="cycles_remove", aliases=["cycles-remove", "cyclesremove", "remove-cycle", "cycle-remove",
                                                     "removecycles", "remove-cycles", "cycleremove", "removecycle",
                                                     "delcycle", "del-cycle", "delcycles"],
                      description="Removes statuses from the cycle. Separate several with ';'.")
    async def cycles_remove(self, ctx, *, statuses: str):
        removed = [name for name in _split_statuses(statuses) if name in self.settings["statuses"]]
        if not removed:
            return await ctx.send(embed=helpers.error_embed("None of those statuses are in the cycle."))
        self.settings["statuses"] = [name for name in self.settings["statuses"] if name not in removed]
        self._save()
        embed = helpers.success_embed(f"Removed {len(removed)} status(es).")
        embed.add_field(name="Remaining Statuses", value=self._status_list())
        await ctx.send(embed=embed)

    @commands.command(name="cycles-delay", aliases=["delay"], description="Sets how many seconds each status shows for.")
    async def cycles_delay(self, ctx, seconds: int):
        if seconds < MIN_DELAY_SECONDS:
            return await ctx.send(embed=helpers.error_embed(f"The delay must be at least {MIN_DELAY_SECONDS} seconds."))
        self.settings["delay"] = seconds
        self._save()
        self.cycle_statuses.change_interval(seconds=seconds)
        await ctx.send(embed=helpers.success_embed(f"Statuses now change every {seconds} seconds."))

    @commands.command(name="cycle", aliases=["cycle-start", "start-cycle"], description="Turns status cycling on or off.")
    async def cycle(self, ctx, state: str):
        state = state.lower()
        if state not in ("on", "off"):
            return await ctx.send(embed=helpers.error_embed("Use `on` or `off`."))

        if state == "on":
            if not self.settings["statuses"]:
                return await ctx.send(embed=helpers.error_embed("Add some statuses with `cycles_add` first."))
            self.settings["cycling"] = True
            if not self.cycle_statuses.is_running():
                self.cycle_statuses.start()
        else:
            self.settings["cycling"] = False
            self.cycle_statuses.cancel()
            await self._apply_default()

        self._save()
        await ctx.send(embed=helpers.success_embed(f"Status cycling is **{state}**."))

    @commands.command(name="cds", aliases=["change-default-status", "default"],
                      description="Changes the default status shown when cycling is off.")
    async def cds(self, ctx, *, status: str):
        self.settings["default"] = status
        self._save()
        if not self.settings["cycling"]:
            await self._apply_default()
        await ctx.send(embed=helpers.success_embed(f"The default status is now **{status}**."))


def setup(bot):
    bot.add_cog(Status(bot))
