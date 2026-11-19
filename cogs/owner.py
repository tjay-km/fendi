import discord, os , random, logging, aiosqlite, json

from discord.ext import commands
from utils import helpers
from utils.checks import is_owner
from utils.config import db_path, STATUS_FILE, COGS_DIR
from utils.prefix import get_prefix

config = json.loads(open(STATUS_FILE, "r").read()) 

def RandomColor(): 
    randcolor = discord.Color(random.randint(0x000000, 0xFFFFFF))
    return randcolor

class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        

    @commands.command(name='reset_lb', description="Allows the owner to manually reset the message leaderboard", aliases=['resetlb','reset', 'lb-reset', 'reset-lb'])
    @commands.check(is_owner)
    async def reset_lb(self, ctx, guild_id: int): 
        if guild_id == None:
            await ctx.send(f"Please enter the guild id you wish to reset.")
        else: 
            guild = self.bot.get_guild(guild_id)
            if guild:   
                async with aiosqlite.connect(db_path("level")) as ab:    
                    async with ab.cursor() as cursor:
                        await cursor.execute("SELECT message_count FROM messages WHERE guild = ?", (guild.id,))
                        data = await cursor.fetchall()
                        count = 0
                        if data: 
                            for item in data: 
                                count += 1
                            await cursor.execute("DELETE FROM messages WHERE guild = ?", (guild.id,))
                            logging.info("✅ Successfully deleted {} users in {} - [{}] from 'level.db'.".format(count, guild.name, guild.id))
                            await ctx.send(embed=discord.Embed(description="✅ Successfully deleted {} users in {} - [{}] from 'level.db'.".format(count, guild.name, guild.id), colour=0x43b581))
                        await ab.commit()
                        await ab.cursor()
            else: 
                await ctx.send(embed=discord.Embed(description=f"❌ Could Not Find Server!", colour=0xf04947), delete_after=5)
                
    @commands.command(name='reset_user', description="Allows the owner to manually reset a user the message leaderboard", aliases=['resetuser','resetu', 'user-reset', 'reset-user'])
    @commands.check(is_owner)
    async def reset_user(self, ctx, *, member: discord.Member = None): 
        if member == None:
            await ctx.send(f"Please enter the user id you wish to reset.")
        elif len(ctx.message.mentions) > 0: 
            member = ctx.message.mentions[0].id
        elif len(ctx.message.content) > 0:
            async with aiosqlite.connect(db_path("prefix")) as db:
                async with db.cursor() as cursor:
                    await cursor.execute("SELECT prefix FROM prefixes WHERE guild = ?", (ctx.guild.id,))
                    data = await cursor.fetchone()
                    if data: 
                        prefix = data
                        thing = ctx.message.content.rsplit(str(prefix))[0].rsplit(" ")
                        person = ctx.guild.get_member(int(thing[1]))
                        if person != None: 
                            member = person.id
                member=member
        else: 
            await ctx.send(embed=discord.Embed(description=f"❌ Could Not Find User!", colour=0xf04947), delete_after=5)
            
        async with aiosqlite.connect(db_path("level")) as ab:    
            async with ab.cursor() as cursor:
                await cursor.execute("SELECT message_count FROM messages WHERE user = ? AND guild = ?", (member, ctx.guild.id,))
                data = await cursor.fetchone()
                if data: 
                    user = ctx.guild.get_member(member)
                    await cursor.execute("DELETE FROM messages WHERE user = ? AND guild = ?", (member, ctx.guild.id,))
                    logging.info("✅ Successfully deleted {} - [{}] with {} messages in {} - [{}] from 'level.db'.".format(user.name, member, data[0], ctx.guild.name, ctx.guild.id))
                    await ctx.send(embed=discord.Embed(description="✅ Successfully deleted {} - [{}] with {} messages in {} - [{}] from 'level.db'.".format(user.name, member, data[0], ctx.guild.name, ctx.guild.id), colour=0x43b581))
                await ab.commit()
                await ab.cursor()
        

    
    @commands.command(name="sleave", description="Leaves the server the cmd is ran in.")
    @commands.check(is_owner)
    async def sleave(self, ctx, guild_id: int):
        guild = self.bot.get_guild(guild_id)
        if guild:
            await guild.leave()
            await ctx.send(embed=discord.Embed(description=f"✅ Left **{guild.name}** - {guild.member_count} Members! ({guild_id})", colour=0x43b581))
        else:
            await ctx.send(embed=discord.Embed(description=f"❌ Could Not Find Server!", colour=0xf04947), delete_after=5)

    @commands.command(name="reloadall",description="Reloads all cogs.")
    @commands.check(is_owner)
    async def reloadall(self, ctx):
        for filename in os.listdir(COGS_DIR):
            try:    
                if filename.endswith('.py') and not filename.startswith("__"):
                    self.bot.unload_extension(f'cogs.{filename[:-3]}')
                    self.bot.load_extension(f'cogs.{filename[:-3]}')
            except Exception as e:
                print(e)
        await ctx.send(embed=discord.Embed(description=f"✅ Reloaded Extensions!", colour=0x43b581))

    @commands.command(name="reload",description="Reloads a specific cog.")
    @commands.check(is_owner)
    async def reload(self, ctx, extension):
        self.bot.unload_extension(f'cogs.{extension}')
        self.bot.load_extension(f'cogs.{extension}')
        await ctx.send(embed=discord.Embed(description=f"✅ Reloaded **{extension}!**", colour=0x43b581))

    @commands.command(name="servers", description="Lists the bots Top 5 servers.")
    @commands.check(is_owner)
    async def servers(self, ctx):
        servers = self.bot.guilds
        servers.sort(key=lambda x: x.member_count, reverse=True) 
        embed = discord.Embed(description="", color=ctx.author.color)
        embed.set_author(name=f"{self.bot.user.name}'s Top 5 Servers!", icon_url=self.bot.user.avatar_url)

        for x in servers[:5]:
            embed.description += "{} - {} Members!\n".format(x.name, x.member_count)

        await ctx.send(embed=embed)
    
    @commands.command(name="toggle", description="Enables or disables a command.")    
    @commands.check(is_owner)
    async def toggle(self, ctx, *, command): 
        command = self.bot.get_command(command)
        if command is None: await ctx.send(embed=helpers.error("Command doesn't exist")) 
        
        elif ctx.command == command: await ctx.send(embed=helpers.error("You cannot disable this command."))

        else:
            command.enabled = not command.enabled
            ternary = "enabled" if command.enabled else "disabled"
            await ctx.send(embed=helpers.success(f"I have  **{ternary}** {command.qualified_name} for you."))
    
    @commands.command(name="logout", description="Disconnects the bot from discord.")
    @commands.check(is_owner)
    async def logout(self, ctx): 
        await ctx.send(content=f"{ctx.author.mention}",embed=helpers.success("Logging out... :wave:"))
        await self.bot.close()
    
    @commands.command(name="cds", description="his changes the bots default status when on_connect() is called.", aliases=['change-default-status', 'default'])
    @commands.check(is_owner)
    async def cds(self, ctx, *, status = None):       # type: ignore
        prefix = await get_prefix(self, ctx)
        if status:
            config['default'] = status
            open(STATUS_FILE, 'w+').write(json.dumps(config, indent=4, sort_keys=True))
            
            await ctx.send(embed=helpers.success(f"Successfully changed the default status to **{status}**"))
        else: 
            await ctx.send(embed=helpers.error(f"You need to state a new default status!"))
        
    
        
        
def setup(bot):
    bot.add_cog(Owner(bot))
