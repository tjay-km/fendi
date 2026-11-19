# Fendi

A multipurpose Discord bot I built in Python. It ran across multiple community servers and
reached **100k+ members at its peak**. It handled message-activity leaderboards, server
moderation helpers, info commands, rotating statuses and a few fun commands.

> **Archived project.** Fendi is no longer running and isn't maintained. It deliberately stays on
> **discord.py 1.7.3** (the version it ran on) and has not been ported to discord.py 2.x. The code
> was cleaned up and refactored for publishing, but it is kept as a record of the project rather than
> a bot to deploy today.

Building it taught me asynchronous Python, event-driven design, SQLite, caching hot paths,
and how to structure a growing codebase into modules.

## Features

- **Activity leaderboard**: admins choose which channels count, and the bot ranks members by
  messages sent (`rank`, `leaderboard`).
- **Per-server settings**: custom prefix and a list of server-level bot admins.
- **Info commands**: server, member, role, avatar, icon and banner lookups.
- **Utility**: Urban Dictionary search, emoji enlarging, reverse avatar search and message sniping.
- **Rotating presence**: the owner can cycle the bot's status through a list on a timer.
- **Owner tools**: reload cogs, toggle commands, leave servers and reset leaderboards.

## Commands

The default prefix is `>`. You can also mention the bot instead of using a prefix.

| Category | Commands |
|---|---|
| Admin | `setprefix`, `prefix`, `add_owner`, `remove_owner`, `owners` |
| Ranking | `rank`, `leaderboard`, `whitelist`, `blacklist`, `whitelisted` |
| Info | `ping`, `uptime`, `stats`, `invite`, `about`, `serverinfo`, `membercount`, `servericon`, `serverbanner`, `userinfo`, `roleinfo`, `avatar` |
| Utility | `enlarge`, `urban`, `revav`, `snipe`, `editsnipe` |
| Fun | `pp`, `iq`, `height` |
| Status (owner) | `cycles`, `cycles_add`, `cycles_remove`, `cycles-delay`, `cycle`, `cds` |
| Owner | `reset_lb`, `reset_user`, `servers`, `sleave`, `reload`, `reloadall`, `toggle`, `logout` |

`help` lists every command you're allowed to use, and `help <command>` shows its usage.

## How it works

```
fendi.py            Bot subclass: startup, prefix lookup, global checks, guild join/leave cleanup
cogs/               one module per feature area, loaded automatically at startup
utils/config.py     settings from env vars or info/config.json, plus paths and constants
utils/database.py   single SQLite connection with in-memory caches for hot lookups
utils/checks.py     bot-owner and per-server admin permission checks
utils/helpers.py    embed builders, time formatting and console output
```

- **One database, cached reads.** Prefixes, admins and tracked channels are loaded into memory at
  startup. The prefix and channel checks that run on *every message* never touch the disk.
- **Batched writes.** Message counts are upserted in memory and committed every 30 seconds instead
  of once per message. SQLite runs in WAL mode.
- **Background tasks.** Status cycling uses `discord.ext.tasks` rather than a blocking loop.
- **Central error handling.** `cogs/errors.py` turns command errors into short replies and logs
  anything unexpected with a traceback.
- **Admins skip cooldowns.** A single bot-wide `after_invoke` hook resets cooldowns for admins.

## Running it (for reference)

Requirements: Python 3.8 or 3.9 (discord.py 1.7.3 doesn't support newer versions), and a bot with
the **Presence** and **Server Members** privileged intents enabled.

```bash
pip install -r requirements.txt
cp info/config.example.json info/config.json   # add your token and Discord user ID(s)
python fendi.py
```

Instead of the config file, you can set `DISCORD_TOKEN`, `OWNER_IDS` (comma separated) and
`DEFAULT_PREFIX` as environment variables. See `.env.example`. Runtime data (the SQLite database
and `status.json`) is written to `data/`, which is git-ignored.

## License

[MIT](LICENSE)
