# Fendi

A multipurpose Discord bot written in Python with [discord.py](https://github.com/Rapptz/discord.py) 1.7.x.
It covers moderation helpers, a message-based ranking system, server and user info commands,
status cycling and a few fun commands. Data is stored in local SQLite databases, so there is no
external database to set up.

> **Legacy project:** it targets discord.py 1.7.3 (Python 3.8-3.9). It has not been ported to
> discord.py 2.x.

## Commands

The default prefix is `>` and can be changed per server with `setprefix`.

| Area | Commands |
|---|---|
| Admin | `setprefix`, `prefix`, `add_owner`, `remove_owner`, `owners` |
| Ranking | `leaderboard`, `whitelist`, `blacklist`, `whitelisted` |
| Info | `ping`, `uptime`, `serverinfo`, `userinfo`, `roleinfo`, `avatar`, `stats`, `membercount`, `invite`, `about` |
| Utility | `serverbanner`, `servericon`, `enlarge`, `urban`, `revav`, `snipe`, `editsnipe` |
| Fun | `pp`, `iq`, `thotrate`, `gayrate`, `height` |
| Owner only | `reset_lb`, `reset_user`, `sleave`, `reload`, `reloadall`, `servers`, `toggle`, `logout`, `cds` |
| Status (owner only) | `cycles`, `cycles_add`, `cycles_remove`, `cycles-delay`, `cycle` |

## Setup

1. Create a bot in the [Discord Developer Portal](https://discord.com/developers/applications) and
   enable the Presence and Server Members privileged intents (the bot requests `Intents.all()`).
2. Install the dependencies (a virtual environment is recommended):
   ```bash
   pip install -r requirements.txt
   ```
3. Create your configuration:
   ```bash
   cp info/config.example.json info/config.json
   ```
   Fill in `token` and your Discord user ID(s) under `owners`.
   Alternatively set the environment variables `DISCORD_TOKEN` and `OWNER_IDS` (comma separated);
   see `.env.example`.
4. Run the bot:
   ```bash
   python fendi.py
   ```

The `data/` folder (SQLite databases and `status.json`) is created automatically on first run and is
git-ignored.

## Project layout

```
fendi.py        entry point: creates the bot and loads every cog
cogs/           one file per feature area (admin, ranking, fun, ...)
utils/config.py  settings, paths and owner IDs (env vars override info/config.json)
utils/checks.py  is_owner / is_admin permission checks
utils/prefix.py  per-server prefix lookup
utils/helpers.py shared embeds and helper functions
info/           configuration template
```

## Security

Never commit `info/config.json` or a real token. If a token ever leaks, regenerate it in the
Developer Portal immediately.

## License

[MIT](LICENSE)
