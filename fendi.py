"""Fendi - a Discord bot (discord.py 1.7.x).

Run with ``python fendi.py``. See README.md for configuration.
"""
import datetime
import logging

import colorama
import discord
from colorama import Fore
from discord.ext import commands

from utils import helpers
from utils.config import COGS_DIR, TOKEN
from utils.prefix import get_prefix

colorama.init()

logging.basicConfig(
    format=f"[{Fore.RED}%(asctime)s{Fore.RESET}] %(message)s",
    datefmt="%d-%m-%Y %H:%M:%S",
    level=logging.INFO,
)

client = commands.Bot(
    command_prefix=get_prefix,
    help_command=None,
    self_bot=False,
    intents=discord.Intents.all(),
)
helpers.title("Fendi Bot")

start = datetime.datetime.now()


@client.event
async def on_message(message):
    await client.process_commands(message)

    if client.user.mention in message.content:
        prefix = await get_prefix(client, message)
        await message.channel.send(f"```prefix is {prefix}```", delete_after=30)


@client.event
async def on_guild_join(guild):
    logging.info(f"Just added to {guild.name}, {guild.id} with {len(guild.members)} members")


@client.event
async def on_guild_remove(guild):
    logging.info(f"Just removed from {guild.name}, {guild.id} with {len(guild.members)} members")


def load_cogs():
    cogs = sorted(p.stem for p in COGS_DIR.glob("*.py") if not p.name.startswith("__"))
    for index, name in enumerate(cogs):
        helpers.print_percent_done(index, len(cogs), 50, "Loading up the cogs...")
        try:
            client.load_extension(f"cogs.{name}")
            print(f"{name}.py loaded")
        except Exception as exc:
            logging.error(f"Could not load cogs.{name}: {exc}")


if __name__ == "__main__":
    if not TOKEN:
        raise SystemExit(
            "No bot token found. Set DISCORD_TOKEN or copy info/config.example.json "
            "to info/config.json and fill it in."
        )
    load_cogs()
    client.run(TOKEN, bot=True, reconnect=True)
