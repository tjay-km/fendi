"""Embed builders and console helpers shared by the bot and its cogs."""
import datetime
import math
import os
import random
import sys

import discord
from colorama import Fore

COLOUR_NEUTRAL = 0x36393F
COLOUR_SUCCESS = 0x43B581
COLOUR_ERROR = 0xF04947


# ---------------------------------------------------------------------- embeds
def info_embed(text: str) -> discord.Embed:
    return discord.Embed(description=text, colour=COLOUR_NEUTRAL)


def success_embed(text: str) -> discord.Embed:
    return discord.Embed(description=f"✅ {text}", colour=COLOUR_SUCCESS)


def error_embed(text: str) -> discord.Embed:
    return discord.Embed(description=f"❌ {text}", colour=COLOUR_ERROR)


def random_colour() -> discord.Colour:
    return discord.Colour(random.randint(0x000000, 0xFFFFFF))


def icon(asset):
    """Return an asset URL usable as an embed icon, or ``Embed.Empty`` when there is none
    (e.g. a server without an icon). discord.py 1.7 would otherwise send an empty URL."""
    return str(asset) if asset else discord.Embed.Empty


def set_thumbnail(embed: discord.Embed, asset) -> discord.Embed:
    """Set the thumbnail only when the asset exists."""
    if asset:
        embed.set_thumbnail(url=str(asset))
    return embed


def numbered_mentions(ids, kind: str = "@") -> str:
    """Render IDs as a numbered list of user (``@``) or channel (``#``) mentions."""
    return "\n".join(f"**{index}.** <{kind}{item}>" for index, item in enumerate(ids, start=1))


# ---------------------------------------------------------------------- time
def humanize_seconds(seconds: float) -> str:
    """Turn a number of seconds into text such as ``1 hour, 2 minutes and 5 seconds``."""
    seconds = math.ceil(seconds)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)

    parts = [
        f"{value} {unit}{'' if value == 1 else 's'}"
        for value, unit in ((days, "day"), (hours, "hour"), (minutes, "minute"), (seconds, "second"))
        if value
    ]
    if not parts:
        return "0 seconds"
    if len(parts) == 1:
        return parts[0]
    return ", ".join(parts[:-1]) + " and " + parts[-1]


def uptime_since(start: datetime.datetime) -> str:
    return humanize_seconds((datetime.datetime.utcnow() - start).total_seconds())


# ------------------------------------------------------------------- console
def set_console_title(text: str) -> None:
    if sys.platform.startswith("win"):
        import ctypes

        ctypes.windll.kernel32.SetConsoleTitleW(text)


def clear_console() -> None:
    os.system("cls" if sys.platform.startswith("win") else "clear")


def progress_bar(index: int, total: int, title: str, width: int = 50) -> None:
    """Print a single-line progress bar; ``index`` is zero based."""
    percent = (index + 1) / total * 100
    done = round(percent / (100 / width))
    print(f"{title}: [{'█' * done}{'░' * (width - done)}] {percent:.1f}% ", end="\r")
    if index + 1 == total:
        print()


def print_banner() -> None:
    print(f"""{Fore.CYAN}
  █████▒▓█████  ███▄    █ ▓█████▄  ██▓
▓██   ▒ ▓█   ▀  ██ ▀█   █ ▒██▀ ██▌▓██▒
▒████ ░ ▒███   ▓██  ▀█ ██▒░██   █▌▒██▒
░▓█▒  ░ ▒▓█  ▄ ▓██▒  ▐▌██▒░▓█▄   ▌░██░      by @1v1
░▒█░    ░▒████▒▒██░   ▓██░░▒████▓ ░██░
 ▒ ░    ░░ ▒░ ░░ ▒░   ▒ ▒  ▒▒▓  ▒ ░▓
 ░       ░ ░  ░░ ░░   ░ ▒░ ░ ▒  ▒  ▒ ░
 ░ ░       ░      ░   ░ ░  ░ ░  ░  ▒ ░
           ░  ░         ░    ░     ░
                           ░
Date: {datetime.date.today().strftime('%d %B %Y')}
{Fore.RESET}""")
