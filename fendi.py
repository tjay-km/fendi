import discord, sys, os, logging, colorama, json, datetime, requests, re, pymongo, aiosqlite, asyncio
from colorama import Fore
from urllib.parse import quote_plus
from discord.ext import commands
from cogs import extort
from utils import util
colorama.init()

# Try environment variables first, then config file
token = os.getenv('DISCORD_TOKEN')
if not token:
    config_path = os.path.join(os.path.dirname(__file__), 'info', 'config.json')
    if os.path.exists(config_path):
        info = json.loads(open(config_path, "r").read())
        token = info['token']
    else:
        raise ValueError("DISCORD_TOKEN environment variable not set and config.json not found")

async def get_prefix(client, message):
    db_path = os.path.join(os.path.dirname(__file__), 'data', 'prefix.db')
    async with aiosqlite.connect(db_path) as db:
        async with db.cursor() as cursor:
            await cursor.execute("SELECT prefix FROM prefixes WHERE guild = ?", (message.guild.id,))
            data = await cursor.fetchone()
            if data: 
                return data[0]
            else: 
                await cursor.execute("REPLACE INTO prefixes (prefix, guild) VALUES (?, ?)",(">", message.guild.id,))
                await cursor.execute("SELECT prefix FROM prefixes WHERE guild = ?",(message.guild.id,))
                data = await cursor.fetchone()
                if data: 
                    await cursor.execute("UPDATE prefixes SET prefix = ? WHERE guild = ?",(">",message.guild.id,))
                return ">"
        
webhook = os.getenv('WEBHOOK_URL')
if not webhook and 'info' in locals():
    webhook = info.get('webhook', '')
logging.basicConfig(format=f"[{Fore.RED}%(asctime)s{Fore.RESET}] %(message)s", datefmt="%d-%m-%Y %H:%M:%S", level=logging.INFO)
client = commands.Bot(command_prefix=get_prefix,help_command=None,self_bot=False, intents=discord.Intents.all())  # type: ignore
extort.title("Fendi Bot")

start = datetime.datetime.now() 

@client.event
async def on_message(message):
    await client.process_commands(message)
    # if message.author.id == client.user.id:
    #     return
    
    if client.user.mention in message.content:
        text = f"```prefix is {await get_prefix(client,message)}```"
        try:
            await message.edit(content=text,delete_after=30) 
        except:
            await message.channel.send(text)
    
@client.event
async def on_guild_join(guild):
    logging.info(f"Just added to {guild.name}, {guild.id} with {len(guild.members)} members")

@client.event
async def on_guild_remove(guild):
    logging.info(f"Just removed from {guild.name}, {guild.id} with {len(guild.members)} members")
            
    
if __name__ == "__main__":
    cogs_dir = os.path.join(os.path.dirname(__file__), 'cogs')
    cogs = os.listdir(cogs_dir)
    for x in range(len(cogs)):
        extort.print_percent_done(x, len(cogs), 50, "Loading up the cogs...")
        if cogs[x].endswith(".py") and not cogs[x].startswith("__") and not "extort" in cogs[x]:
            client.load_extension(f"cogs.{cogs[x][:-3]}")
            print(f"{cogs[x]} loaded")
    client.run(token,bot=True,reconnect=True)
