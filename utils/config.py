"""Settings, paths and constants.

Secrets are read from environment variables first, then ``info/config.json``,
so nothing sensitive lives in the source tree.
"""
import json
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
COGS_DIR = BASE_DIR / "cogs"
CONFIG_FILE = BASE_DIR / "info" / "config.json"
DATA_DIR = BASE_DIR / "data"
DB_FILE = DATA_DIR / "fendi.db"
STATUS_FILE = DATA_DIR / "status.json"

STREAM_URL = "https://twitch.tv/fendi"
SUPPORT_INVITE = "https://discord.gg/fendi"


def _load_config_file() -> dict:
    try:
        return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {}


def _parse_ids(raw) -> frozenset:
    """Accept a list, a single ID or a comma separated string and keep only numeric IDs."""
    if isinstance(raw, (str, int)):
        raw = str(raw).split(",")
    return frozenset(int(item) for item in map(str, raw or []) if item.strip().isdigit())


_CONFIG = _load_config_file()

TOKEN = os.getenv("DISCORD_TOKEN") or _CONFIG.get("token")
DEFAULT_PREFIX = os.getenv("DEFAULT_PREFIX") or _CONFIG.get("prefix", ">")
OWNER_IDS = _parse_ids(os.getenv("OWNER_IDS") or _CONFIG.get("owners"))
