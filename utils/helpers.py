#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, os, random, youtube_dl, discord, asyncio, ctypes, io, datetime
from colorama import Fore
from gtts import gTTS
ytdl_format_options = {
    'format': 'bestaudio/best',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}
ffmpeg_options = {
    'options': '-vn'
}
def RandomColor(): 
    randcolor = discord.Color(random.randint(0x000000, 0xFFFFFF))
    return randcolor

def print_percent_done(index, total, bar_len, title):
    percent_done = (index+1)/total*100
    percent_done = round(percent_done, 1)
    done = round(percent_done/(100/bar_len))
    togo = bar_len-done
    done_str = '█'*int(done)
    togo_str = '░'*int(togo)
    print(f'{title}: [{done_str}{togo_str}] {percent_done}% ', end='\r')
    if round(percent_done) == 100:
        print('')
async def do_tts(message):
    f = io.BytesIO()
    tts = gTTS(text=message.lower(), lang="en-US")
    tts.write_to_fp(f)
    f.seek(0)
    return f
def date_send(text):
    print(f"[!] {text}")
def title(text):
    if sys.platform.startswith("win"): 
        ctypes.windll.kernel32.SetConsoleTitleW(text)

def getembed(text):
    #return f"""```{text}```"""
    embed = discord.Embed(
        description=text,
        color=0x36393F
    )
    return embed

def error(text):
    embed = discord.Embed(
        description="❌ " + text,
        color=0xf04947
    )
    return embed

def success(text):
    embed = discord.Embed(
        description= "✅ " + text,
        colour=0x43b581
    )
    return embed

def sort_users(json, server, user): 
    try: 
        return int(json['guild'][str(server.guild.id)]['messages'][str(user)]['message_count'])
    except KeyError: 
        return 0
    
ytdl = youtube_dl.YoutubeDL(ytdl_format_options)
class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')
    
    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:  # type: ignore
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


def clear():
    if sys.platform == "win32" or sys.platform == "win64":
        os.system("cls")
    else:
       os.system("clear")

def asciigen(length):
    asc = ''
    for x in range(int(length)):
        num = random.randrange(13000)
        asc = asc + chr(num)
    return asc

def ui(self,auth):
    print(f"""
{Fore.CYAN}

  █████▒▓█████  ███▄    █ ▓█████▄  ██▓
▓██   ▒ ▓█   ▀  ██ ▀█   █ ▒██▀ ██▌▓██▒
▒████ ░ ▒███   ▓██  ▀█ ██▒░██   █▌▒██▒
░▓█▒  ░ ▒▓█  ▄ ▓██▒  ▐▌██▒░▓█▄   ▌░██░      by extort#4444
░▒█░    ░▒████▒▒██░   ▓██░░▒████▓ ░██░
 ▒ ░    ░░ ▒░ ░░ ▒░   ▒ ▒  ▒▒▓  ▒ ░▓  
 ░       ░ ░  ░░ ░░   ░ ▒░ ░ ▒  ▒  ▒ ░
 ░ ░       ░      ░   ░ ░  ░ ░  ░  ▒ ░
           ░  ░         ░    ░     ░  
                           ░                                              
Date: {datetime.date.today().strftime('%d, %B %Y')}
{Fore.RESET}
""")


