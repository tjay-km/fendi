"""Central configuration: paths, owner IDs and the bot token.

Values come from environment variables first, then ``info/config.json``.
Nothing secret lives in the source tree.
"""
import json
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
COGS_DIR = BASE_DIR / "cogs"
CONFIG_FILE = BASE_DIR / "info" / "config.json"
STATUS_FILE = str(DATA_DIR / "status.json")

DATA_DIR.mkdir(exist_ok=True)

_DEFAULT_STATUS = {"default": "fendi", "cycle_status": "off", "delay": 10, "cycle": []}
if not Path(STATUS_FILE).exists():
    Path(STATUS_FILE).write_text(json.dumps(_DEFAULT_STATUS, indent=4), encoding="utf-8")


def _load_file() -> dict:
    try:
        return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {}


CONFIG = _load_file()

TOKEN = os.getenv("DISCORD_TOKEN") or CONFIG.get("token")
WEBHOOK = os.getenv("WEBHOOK_URL") or CONFIG.get("webhook", "")
DEFAULT_PREFIX = CONFIG.get("prefix", ">")


def _parse_owner_ids() -> frozenset:
    raw = os.getenv("OWNER_IDS") or CONFIG.get("owners") or []
    if isinstance(raw, (str, int)):
        raw = str(raw).split(",")
    return frozenset(int(x) for x in map(str, raw) if x.strip().isdigit())


OWNER_IDS = _parse_owner_ids()


def db_path(name: str) -> str:
    """Return the path of ``data/<name>.db``."""
    return str(DATA_DIR / f"{name}.db")
