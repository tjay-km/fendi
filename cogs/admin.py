import discord, aiosqlite, logging

from discord.ext import commands
from utils import helpers
from utils.checks import is_admin
from utils.config import db_path
from utils.prefix import get_prefix

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
         

    @commands.Cog.listener()
    async def on_ready(self):
        #await asyncio.sleep(3) 
        async with aiosqlite.connect(db_path("prefix")) as db:
            async with db.cursor() as cursor:
                await cursor.execute("CREATE TABLE IF NOT EXISTS prefixes (guild INTEGER, prefix TEXT, UNIQUE(guild))")
            await db.commit()
            await db.cursor()
            
        async with aiosqlite.connect(db_path("admin")) as ab:    
            async with ab.cursor() as cur: 
                await cur.execute("CREATE TABLE IF NOT EXISTS owners (guild INTEGER, user INTEGER)")

            await ab.commit()
            await ab.cursor()
    
    @commands.Cog.listener()
    async def on_guild_join(self, guild): 
        async with aiosqlite.connect(db_path("prefix")) as db:
            async with db.cursor() as cursor:
                await cursor.execute("REPLACE INTO prefixes (guild, prefix) VALUES (?, ?)", (guild.id,">",))
            await db.commit()
            await db.cursor()
        
    @commands.Cog.listener()
    async def on_guild_remove(self, guild): 
        async with aiosqlite.connect(db_path("prefix")) as db:
            async with db.cursor() as cursor:
                await cursor.execute("SELECT prefix FROM prefixes WHERE guild = ?", (guild.id,))
                data = await cursor.fetchone()
                if data: 
                    await cursor.execute("DELETE FROM prefixes WHERE guild = ?", (guild.id,))
            await db.commit()
            await db.cursor()
            
        async with aiosqlite.connect(db_path("admin")) as ab:
            async with ab.cursor() as cursor:
                await cursor.execute("SELECT user FROM owners WHERE guild = ?", (guild.id,))
                data = await cursor.fetchone()
                if data: 
                    await cursor.execute("DELETE FROM owners WHERE guild = ?", (guild.id,))
            await ab.commit()
            await ab.cursor()
    
    @commands.command(name="setprefix",description="Allows an owner to change the servers prefix.", aliases=['set-prefix'])
    @commands.check(is_admin)
    @commands.has_permissions(manage_guild=True)
    async def setprefix(self, ctx, prefix=None): 
        async with aiosqlite.connect(db_path("prefix")) as db:
            async with db.cursor() as cursor:
                if prefix is None: 
                    await cursor.execute("SELECT prefix FROM prefixes WHERE guild = ?", (ctx.guild.id,))
                    data = await cursor.fetchone()
                    if data: 
                        return await ctx.send(content=ctx.author.mention, embed=helpers.getembed(f"You haven't entered a new prefix to change to.\nCurrent prefix is: **{prefix}**"))
                    else:
                        return await ctx.send(content=ctx.author.mention, embed=helpers.getembed(f"You haven't entered a new prefix to change to.\nCurrent prefix is: **>**"))
                await cursor.execute("SELECT prefix FROM prefixes WHERE guild = ?", (ctx.guild.id,))
                data = await cursor.fetchone()
                if data: 
                    await cursor.execute("UPDATE prefixes SET prefix = ? WHERE guild = ?", (prefix, ctx.guild.id,))
                    await ctx.send(content=ctx.author.mention,embed=helpers.getembed(f"Updated prefix's for {ctx.guild.name}.\nNew Prefix: {prefix}"))
                else:
                    await cursor.execute("INSERT INTO prefixes (prefix, guild) VALUES (?, ?)", (">", ctx.guild.id,))
                    await cursor.execute("SELECT prefix FROM prefixes WHERE guild = ?", (ctx.guild.id,))
                    data = await cursor.fetchone()
                    if data: 
                        await cursor.execute("UPDATE prefixes SET prefix = ? WHERE guild = ?", (prefix, ctx.guild.id,))
                        text = f"Updated prefix's for {ctx.guild.name}.\nNew Prefix: {prefix}"
                        await ctx.send(content=ctx.author.mention,embed=helpers.getembed(text))
                    else: return
            await db.commit()  # type: ignore
    
    @commands.command(name='prefix', description='Displays the guilds prefix for the bot.')
    @commands.cooldown(1,60, commands.BucketType.channel)
    async def prefix(self, ctx):
        if await is_admin(ctx):
            self.prefix.reset_cooldown(ctx)
        em = discord.Embed(title=f"Prefix Settings", description = await get_prefix(self,ctx))
        em.set_author(name=str(ctx.guild.name) + "'s Prefix",icon_url=str(ctx.author.avatar_url),url="https://discord.gg/fendi") 
        em.set_thumbnail(url=f"{str(ctx.guild.icon_url)}")
        await ctx.send(embed=em)

    @commands.command(name='add_owner', description = "Allows an owner to add someone to the owner list.",aliases=['add-owner','owner',"add"])
    #@commands.has_permissions(manage_server=True)
    @commands.check(is_admin)
    async def add_owner(self, ctx, *, member: discord.Member = None):  # type: ignore
        if member is None:
            async with aiosqlite.connect(db_path("admin")) as ab:
                async with ab.cursor() as cursor:
                    await cursor.execute('SELECT user FROM owners WHERE guild = ? AND user = ?',(ctx.guild.id, ctx.author.id))
                    list = await cursor.fetchone()
                    if list:   
                        async with aiosqlite.connect(db_path("prefix")) as db:
                            async with db.cursor() as cursor:
                                await cursor.execute("SELECT prefix FROM prefixes WHERE guild = ?", (ctx.guild.id,))
                                data = await cursor.fetchone()
                                if data: 
                                    prefix = data                       
                                    desc = f"You need to specify who you want to be owner.\nExamples: **{prefix[0]}add_owner** {ctx.author.id}\n**{prefix[0]}add_owner** <@{ctx.author.id}>"
                                    return await ctx.send(content=ctx.author.mention,embed=helpers.getembed(desc))
                                return await ctx.send(content=ctx.author.mention, embed=helpers.getembed(f"You currently don't have a prefix set.\nPlease use the current prefix: **>**"))
            
        elif member.bot:   # type: ignore
            text = "You can't add a bot as an owner."
            return await ctx.send(content=f"<@{str(ctx.author.id)}>",embed = helpers.getembed(text)) 
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
                        print(thing)
                        person = ctx.guild.get_member(int(thing[1]))
                        print(person)
                        if person != None: 
                            member = person.id
                            print(member)
                member = member
                
        async with aiosqlite.connect(db_path("admin")) as ab:
            async with ab.cursor() as cur:
                await cur.execute('SELECT user FROM owners WHERE guild = ? AND user = ?',(ctx.guild.id, member))
                list = await cur.fetchone()
                if list:
                    em = discord.Embed(description=f"<@{member}> - [{member}] is already in the owner list")
                    return await ctx.send(content=f"{ctx.author.mention}", embed=em)
                if not list:  
                    await cur.execute("INSERT OR REPLACE INTO owners (user, guild) VALUES (?,?)",(member, ctx.guild.id,))     
                    await ab.commit()   
                    await ab.cursor()        
                    await cur.execute('SELECT user FROM owners WHERE guild = ? AND user = ?',(ctx.guild.id, ctx.author.id))
                    b = await cur.fetchone()
                    if not b: 
                        await cur.execute("INSERT OR REPLACE INTO owners (user, guild) VALUES (?,?)",(ctx.author.id, ctx.guild.id,))
                        
                    await ab.commit()
                    await ab.cursor()
                    await cur.execute('SELECT user FROM owners WHERE guild = ?',(ctx.guild.id,))
                    list = await cur.fetchall()
                    if list:
                        desc = ""
                        count= 0
                        for table in list:
                            count +=1
                            user = ctx.guild.get_member(table[0])
                            desc += f"**{count}**. <@{user.id}>\n"
                        em = discord.Embed(title=f"{ctx.guild.name}'s Owner List", description=desc)
                        em.set_author(name=str(ctx.author.name) + " | Owners",icon_url=str(ctx.author.avatar_url),url="https://discord.gg/fendi") 
                        em.set_thumbnail(url="https://media.discordapp.net/attachments/876092097420226560/1019749215821377536/unknn.png")
                        return await ctx.send(content=f"{ctx.author.mention} Added {member} to the owners list.",embed=em)
            await ab.commit()
            await ab.cursor()
    
    @commands.command(name="remove_owner", description="Allows an owner to remove another owner",aliases=['remove-owner',"remove"])
    @commands.check(is_admin)
    async def remove_owner(self,ctx, *, member: discord.Member = None):
        if member is None:
            return await ctx.send(embed=helpers.getembed("Please mention a user to remove from the Owner Database."))
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
                member = member
        
        async with aiosqlite.connect(db_path("admin")) as ab:
            async with ab.cursor() as cur:
                await cur.execute('SELECT user FROM owners WHERE guild = ? AND user = ?',(ctx.guild.id, member))
                list = await cur.fetchone()
                if list:
                    user = ctx.guild.get_member(member)
                    await cur.execute("DELETE FROM owners WHERE user = ? AND guild = ?", (member, ctx.guild.id,))
                    logging.info("Successfully deleted {} - [{}] as an owner.".format(user.name + "#" + user.discriminator, member))
                    await ctx.send(embed=helpers.getembed("Successfully deleted {} - [{}] as an owner.".format(user.name + "#" + user.discriminator, member)))
            await ab.commit()
            await ab.cursor()

    @commands.command(name='owners',description="Displays the list of bot owners within the guild.",aliases=['owners-list'])
    @commands.check(is_admin)
    async def owners(self, ctx):
        async with aiosqlite.connect(db_path("admin")) as ab:
            async with ab.cursor() as cursor:
                await cursor.execute('SELECT user FROM owners WHERE guild = ?',(ctx.guild.id,))
                list = await cursor.fetchall()
                if list:
                    desc = ""
                    count= 0
                    for table in list:
                        count +=1
                        user = ctx.guild.get_member(table[0])
                        desc += f"**{count}**. <@{user.id}>\n"
                    em = discord.Embed(title=f"{ctx.guild.name}'s Owner List", description=desc)
                    em.set_author(name=str(ctx.author.name) + " | Owner",icon_url=str(ctx.author.avatar_url),url="https://discord.gg/fendi") 
                    em.set_thumbnail(url="https://media.discordapp.net/attachments/876092097420226560/1019749215821377536/unknn.png")
                    return await ctx.send(embed=em)
                else: return await ctx.send(embed=helpers.getembed("There are currently no owners in **{}**.".format(ctx.guild.name)))

def setup(bot):
    bot.add_cog(Admin(bot)) 