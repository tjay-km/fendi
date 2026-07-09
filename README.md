# Fendi Bot

A comprehensive Discord bot with extensive features including admin commands, fun commands, ranking system, staff commands, greetings, and miscellaneous utilities.

## Features

- **Admin Commands**: Full administrative control and moderation tools
- **Fun Commands**: Entertainment and utility commands for users
- **Ranking System**: User level and experience tracking
- **Staff Commands**: Specialized commands for staff members
- **Greetings**: Automated welcome messages for new members
- **Miscellaneous**: Various utility commands and features

## Tech Stack

- Python 3.8+
- discord.py 1.7.3
- MongoDB
- aiosqlite
- colorama
- youtube_dl
- gTTS (Google Text-to-Speech)

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `info/config.example.json` to `info/config.json`
4. Fill in your bot token and configuration details
5. Run the bot:
   ```bash
   python fendi.py
   ```

## Configuration

The bot requires a configuration file at `info/config.json` with the following structure:

```json
{
    "token": "YOUR_BOT_TOKEN_HERE",
    "prefix": ">",
    "webhook": "YOUR_WEBHOOK_URL_HERE",
    "owners": "YOUR_OWNER_ID_HERE"
}
```

Alternatively, you can use environment variables:
- `DISCORD_TOKEN`: Your bot token
- `WEBHOOK_URL`: Optional webhook URL for logging

## License

This project is for educational purposes.
