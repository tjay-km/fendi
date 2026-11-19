import discord, json, asyncio, random
from discord.ext import commands
from utils import helpers
from utils.checks import is_owner
from utils.config import STATUS_FILE
from utils.prefix import get_prefix

activities = json.loads(open(STATUS_FILE,"r").read())

colors = [
            discord.ActivityType.watching,
            discord.ActivityType.playing,
            discord.ActivityType.listening,
            discord.ActivityType.streaming
        ]

statuses = [
            discord.Status.idle,
            discord.Status.online,
            discord.Status.dnd
        ]

class Status(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.command(name='cycles', description="Displays the current statuses available to cycle and their delays.", aliases=['cycle-info'])
    @commands.check(is_owner)
    async def cycles(self, ctx):
        text = ""
        for c in activities['cycle']:
            if c == 1:
                text += c 
            else:
                text += c + " "
        embed=discord.Embed(title="Statuses", color=helpers.RandomColor())
        embed.add_field(name="Statuses:", value=text, inline=False)
        embed.add_field(name="Delay:", value=activities['delay'], inline=False)
        await ctx.send(embed=embed)
    
    @commands.command(name='cycles_add', description="Allows you to add more statuses to cycle.", aliases=['cycles-add','cyclesadd','add-cycle', "cycle-add","addcycles",'add-cycles','cycleadd','addcycle'])
    @commands.check(is_owner)
    async def cycles_add(self, ctx, *, cycle = None):
        if cycle == None:
            await ctx.send(embed=helpers.error(f"Specify statuses to remoe.\nE.g -> {await get_prefix(self, ctx)}cycles-add [Cycle1];[Cycle2]"),delete_after=10)
        else:
            msg = await ctx.send(content = "", embed=discord.Embed(description=f"✅ Attempting to add mentioned statuses...", colour=0x43b581))
            for n in cycle.split(";"):
                if n in activities['cycle']:
                    await msg.edit(content="",embed=helpers.error(f"The status **{n}** already exists."), delete_after=10)
                else: 
                    # msg = await ctx.send(embed=helpers.success("Adding new statuses..."))
                    activities['cycle'].append(n)
                    open(STATUS_FILE, 'w+').write(json.dumps(activities, indent=4, sort_keys=True))
                    embed = discord.Embed(title="New Statuses have been added", colour=0x43b581)
                    embed.add_field(name="New Statuses:",value=n, inline=True)
                    text = ""
                    for c in activities['cycle']:
                        if c == 1:
                            text += c 
                        else:
                            text += c + " "
                    embed.add_field(name="All Statuses",value=text, inline=True)
                    await msg.edit(content = "",embed=embed)
            
    @commands.command(name='cycles_remove', description="Allows you to add more statuses to cycle.", aliases=['cycles-remove','cyclesremove','remove-cycle', "cycle-remove","removecycles",'remove-cycles','cycleremove','removecycle','delcycle','del-cycle','delcycles'])
    @commands.check(is_owner)
    async def cycles_remove(self, ctx, *, cycle):
        if cycle == None:
            await ctx.send(embed=helpers.error(f"Specify statuses to remove.\nE.g -> {await get_prefix(self, ctx)}cycles-remove [Cycle1];[Cycle2]"),delete_after=10)
        else:
            msg = await ctx.send(content = "", embed=discord.Embed(description=f"✅ Attempting to remove mentioned statuses...", colour=0x43b581))
            for o in cycle.split(";"):
                if o in activities['cycle']:
                    activities['cycle'].remove(str(o))
                    open(STATUS_FILE, 'w+').write(json.dumps(activities, indent=4, sort_keys=True))
                    embed = discord.Embed(title="Deleted Status", color=discord.Color.red())
                    embed.add_field(name=f"Removed Status:",value=o, inline=True)
                    text = ""
                    for c in activities['cycle']:
                        if c == 1:
                            text += c 
                        else:
                            text += c + " "
                            
                    embed.add_field(name="Remaining Statuses:",value=text, inline=True)
                    await asyncio.sleep(3)
                    await msg.edit(content = "",embed=embed)
                else: 
                    await asyncio.sleep(3)
                    await msg.edit(content="",embed=helpers.error(f"The status **{o}** doesn't exist."),delete_after=10)

    @commands.command(name='cycles-delay', description="Allows you to change how often the statuses are cycled.", aliases=['delay'])
    @commands.check(is_owner)
    async def cycles_delay(self, ctx, delay: int):
        if delay:
            activities['delay'] = delay
            open(STATUS_FILE, 'w+').write(json.dumps(activities, indent=4, sort_keys=True))
            await ctx.send(embed=helpers.success(f"Changed the delay to {delay}."))
    
    @commands.command(name='cycle', description="Toggles on/off the cycling of statuses.", aliases=['cycle-start','start-cycle'])
    @commands.check(is_owner)
    async def cycle(self, ctx, toggle: str):
        if toggle.lower() == "on": 
            msg = await ctx.send(content="",embed=discord.Embed(description=f"✅ Toggling Status Cycling...", colour=0x43b581))
            text = ""
            for c in activities['cycle']:
                if c == 1:
                    text += c 
                else:
                    text += c + " "
            activities["cycle_status"] = "on"
            open(STATUS_FILE, 'w+').write(json.dumps(activities, indent=4, sort_keys=True))
            embed = discord.Embed(title="Cycling Statuses Is **ON**", color=discord.Color.green())
            embed.add_field(name="Statuses", value=text)
            embed.add_field(name="Delay", value=activities['delay'])
            await asyncio.sleep(3)
            await msg.edit(content="",embed=embed)
            while activities["cycle_status"] == "on":
                await self.bot.change_presence(activity=discord.Activity(type=random.choice(colors),name=random.choice(activities['cycle']),url="https://twitch.tv/fendi"),status=random.choice(statuses))
                await asyncio.sleep(activities['delay'])
            else: return
        
        if toggle.lower() == "off":
            msg = await ctx.send(content="",embed=helpers.getembed("Toggling Status Cycling..."))
            activities["cycle_status"] = "off"
            open(STATUS_FILE, 'w+').write(json.dumps(activities, indent=4, sort_keys=True))
            await asyncio.sleep(3)
            await msg.edit(content="", emebed=helpers.success(f"Status Cycling is: `{activities['cycle_status']}`...\nDefault Status is now **on**."))
            await self.bot.change_presence(activity=discord.Streaming(name=activities['default'],url="https://twitch.tv/fendi"))
        
    

def setup(bot):
    bot.add_cog(Status(bot))
