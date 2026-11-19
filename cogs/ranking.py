import discord, aiosqlite, logging, json, re, asyncio, time, math

from discord.ext import commands
from utils import helpers
from utils.checks import is_admin
from utils.config import OWNER_IDS, db_path, STATUS_FILE
from utils.prefix import get_prefix

config = json.loads(open(STATUS_FILE, "r").read()) 
    
time_regex = re.compile(r"(?:(\d{1,5})(h|s|m|d))+?")
time_dict = {'h': 3600, 's': 1, 'm':60, 'd': 86400}

class TimeConverter(commands.Converter):
    async def convert(self,ctx, argument):
        args = argument.lower()
        matches = re.findall(time_regex,args)
        time = 0
        for key, value in matches:
            try:
                time += time_dict[value] * float(key)
            except KeyError:
                raise commands.BadArgument(f"{value} is an invalid time key! h|m|s|d are valid arguments.")
            except ValueError:
                raise commands.BadArgument(f"{key} is not a number!")
        return time

class Ranking(commands.Cog):
    def __init__(self, bot):
        self.bot = bot 
        self.bot.whitelist = list(OWNER_IDS)
        self.bot.command = commands.command()
    
    @commands.Cog.listener()
    async def on_ready(self):
        
        helpers.clear()
        helpers.ui(self.bot, None)
        logging.info("Bot Has Successfully Loaded, Info will be displayed below:")
        logging.info("Name: {}".format(self.bot.user.name))
        logging.info("ID: {}".format(self.bot.user.id))
        logging.info("Server Count: {}".format(len(self.bot.guilds)))
        true_member_count = len([m for m in self.bot.users if not m.bot])
        true_count = sum(1 for _ in self.bot.get_all_members())  
        logging.info("Total Users Watching: {}".format(true_count))
        true_bot_count = len([m for m in self.bot.users if m.bot])
        logging.info("Total Bots Watching: {}".format(true_bot_count))
        logging.info("Default Prefix: >")
        logging.info("https://discord.com/api/oauth2/authorize?client_id={}&permissions=8&scope=bot".format(self.bot.user.id))
        await self.bot.change_presence(activity=discord.Streaming(name=config['default'],url="https://twitch.tv/fendi"))

        setattr(self.bot, "db", await aiosqlite.connect(db_path("level")))   
        await asyncio.sleep(3) 
        async with self.bot.db.cursor() as cursor:
            await cursor.execute("CREATE TABLE IF NOT EXISTS messages (guild INTEGER, user INTEGER, message_count INTEGER)")
        await self.bot.db.cursor()

        async with aiosqlite.connect(db_path("channels")) as cb:
            async with cb.cursor() as cursor:
                await cursor.execute("CREATE TABLE IF NOT EXISTS whitelist (guild INTEGER, channel INTEGER, UNIQUE(channel))")
                #await cursor.execute("DROP TABLE IF EXISTS whitelist")
            await cb.commit()
            await cb.cursor()

    @commands.Cog.listener(name='on_command')
    async def print(self, ctx):
        server = ctx.guild
        channel = ctx.channel
        user = ctx.author
        command = ctx.command
        logging.info(f'[{server.name} - {server.id}] > [{channel.name} - {channel.id}] > [{user} - {user.id}] > {command}')
        
    @commands.Cog.listener()
    async def on_message(self, message): 
        if message.author == self.bot: 
            return
        if message.author.bot:
            return
        async with aiosqlite.connect(db_path("channels")) as ab:
            async with ab.cursor() as cursor: 
                await cursor.execute('SELECT channel FROM whitelist WHERE guild = ? AND channel = ?',(message.guild.id,message.channel.id,))
                list = await cursor.fetchone()
                if not list:
                    return
                if list:
                    author = message.author
                    guild = message.guild
                    async with self.bot.db.cursor() as cursor:
                        await cursor.execute("SELECT message_count FROM messages WHERE user = ? AND guild = ? ", (author.id, guild.id))
                        message_count = await cursor.fetchone()
                        
                        if not message_count:
                            await cursor.execute("INSERT INTO messages (guild, user, message_count) VALUES (?, ?, ?) ", (guild.id, author.id, 0,))
                    
                        try: 
                            message_count = message_count[0]
                        except TypeError:
                            message_count = 0
                        
                        message_count += 1
                        await cursor.execute("UPDATE messages SET message_count = ? WHERE user = ? AND guild = ? ", (message_count, author.id, guild.id))
                    await self.bot.db.commit()
                    await self.bot.db.cursor()
    
    @commands.Cog.listener()
    async def on_guild_join(self, guild): 
        async with self.bot.db.cursor() as cursor:
            await cursor.execute("SELECT message_count FROM messages WHERE guild = ?", (guild.id,))
            data = await cursor.fetchall()
            count = 0
            if data: 
                for item in data: 
                    count += 1
                await cursor.execute("DELETE FROM messages WHERE guild = ?", (guild.id,))
                logging.info("Successfully deleted {} users in {} - [{}] with {} members from level.db due to them removing us from their server.".format(count, guild.name, guild.id, guild.member_count))
        await self.bot.db.commit()

    @commands.Cog.listener()
    async def on_guild_remove(self, guild): 
        #await asyncio.sleep(10)
        async with self.bot.db.cursor() as cursor:
            await cursor.execute("SELECT message_count FROM messages WHERE guild = ?", (guild.id,))
            data = await cursor.fetchall()
            count = 0
            if data: 
                for item in data: 
                    count += 1
                await cursor.execute("DELETE FROM messages WHERE guild = ?", (guild.id,))
                logging.info("Successfully deleted {} users in {} - [{}] with {} members from level.db due to them removing us from their server.".format(count, guild.name, guild.id, guild.member_count))
        await self.bot.db.commit()
        
        async with aiosqlite.connect(db_path("channels")) as cb:
                async with cb.cursor() as cursor:
                    await cursor.execute("SELECT channel FROM whitelist WHERE guild = ?", (guild.id,))
                data = await cursor.fetchall()
                if data: 
                    count = 0
                    for item in data: 
                        count +=1
                    await cursor.execute("DELETE FROM whitelist WHERE guild = ?", (guild.id,))
                    logging.info("Successfully deleted {} whitelisted channels for {} - [{}] from channels.db due to them removing us from their server.".format(count, guild.name, guild.id))
                await cb.commit()
                await cb.cursor()
        
    @commands.Cog.listener()
    async def on_member_remove(self, member): 
        #await asyncio.sleep(10)
        async with self.bot.db.cursor() as cursor:
            await cursor.execute("SELECT message_count FROM messages WHERE user = ? AND guild = ?", (member.id, member.guild.id,))
            data = await cursor.fetchone()
            if data: 
                await cursor.execute("DELETE FROM messages WHERE user = ? AND guild = ?", (member.id, member.guild.id,))
                logging.info("Successfully deleted {} - [{}] Who had [{}] messages from 'level.db' due to them leaving the following guild: {}".format(member.name + "#" + member.discriminator, member.id, data[0],member.guild.name))
        await self.bot.db.commit()
    
    @commands.command(aliases=["lvl", "msgs"], name = "rank", description = "Shows the message count and rank of the user.")
    @commands.cooldown(1,10,commands.BucketType.user)
    async def rank(self, ctx, *, member: discord.Member = None):  # type: ignore
        if await is_admin(ctx):
            self.rank.reset_cooldown(ctx)
        
        if member is None:
            member = ctx.author
        else: member = ctx.message.mentions[0]
        if member.bot:  # type: ignore
            text = "We Bots do not have a rank because WE are BETTER than you."
            await ctx.send(content=f"<@{str(ctx.author.id)}>",embed = helpers.getembed(text)) 
        guild = ctx.guild
        async with self.bot.db.cursor() as cursor:
            
            await cursor.execute("""
SELECT RowNr
FROM (
    SELECT 
         guild, ROW_NUMBER() OVER (ORDER BY message_count DESC) AS RowNr,
         message_count, user
    FROM messages WHERE guild = ?
) sub
WHERE sub.user = ?""", (guild.id, member.id,))
            rank = await cursor.fetchone()
            await self.bot.db.commit()
                
            
            await cursor.execute("SELECT message_count FROM messages WHERE user = ? AND guild = ? ORDER BY message_count DESC LIMIT 1", (member.id, ctx.guild.id))  # type: ignore
            message_count = await cursor.fetchone()
            
            if not message_count:
                await cursor.execute("INSERT INTO messages (guild, user, message_count) VALUES (?, ?, ?) ", (ctx.guild.id, member.id, 0,))  # type: ignore
                
            await cursor.execute("SELECT message_count FROM messages WHERE guild = ?", (guild.id,))
            data = await cursor.fetchall()
            count = 0
            if data: 
                for item in data: 
                    count += 1
            try: 
                message_count = message_count[0]
            except TypeError:
                message_count = 0
        
            text = "**{}** currently has **{}** messages this week.\nRank **#{}** on {} leaderboard.".format(str(member.name),message_count, rank[0], ctx.guild.name)  # type: ignore
            em = discord.Embed(description=text)
            em.set_author(name=str(ctx.author.name) + " | LB",icon_url=str(ctx.author.avatar_url),url="https://discord.gg/fendi")  # type: ignore
            em.set_thumbnail(url=str(ctx.guild.icon_url))
            em.set_footer(text=f"#{rank[0]} of {count} users.")  # type: ignore
            await ctx.send(content=f"<@{str(ctx.author.id)}>",embed = em)
        await self.bot.db.cursor()


        
    @commands.command(name="leaderboard", description="Displays the guilds Top 10 most active users with the most messages.",aliases=['lb']) 
    @commands.cooldown(1,30,commands.BucketType.user)
    async def leaderboard(self, ctx):
        if await is_admin(ctx):
            self.leaderboard.reset_cooldown(ctx)
        async with self.bot.db.cursor() as cursor:
            await cursor.execute("SELECT message_count, user FROM messages WHERE guild = ? ORDER BY message_count DESC LIMIT 10", (ctx.guild.id,))
            data = await cursor.fetchall()
            if data: 
                count = 0
                desc = ""
                for table in data: 
                    count+=1
                    user = ctx.guild.get_member(table[1])
                    desc += f"**{count}.** <@{user.id}>: **{table[0]} messages.**\n"
                em = discord.Embed(title=f"{ctx.guild.name}'s Weekly Activity Leaderboard", description=desc)
                em.set_author(name=str(ctx.author.name) + " | LB",icon_url=str(ctx.author.avatar_url),url="https://discord.gg/fendi")  # type: ignore
                em.set_thumbnail(url="https://media.discordapp.net/attachments/876092097420226560/1019749215821377536/unknn.png")
                return await ctx.send(embed=em)
            return await ctx.send("Leaderboard doesn't exist as there are no stored users.")
    
    @commands.command(name="whitelist", description="Allows a bot owner to whitelist channels for the bot to monitor messages in for the activity leaderboard.", aliases=['wlist','wl'])
    @commands.check(is_admin)
    async def whitelist(self, ctx, channel: discord.TextChannel = None):
        if channel is None:
            await ctx.send(embed=helpers.getembed(f"Please mention a channel to be whitelisted to monitor messages.\nExample: {await get_prefix(self,ctx)}whitelist {ctx.channel.mention}\nExample: {await get_prefix(self,ctx)}whitelist {ctx.channel.id}"))
        if channel:
            async with aiosqlite.connect(db_path("channels")) as cb:
                async with cb.cursor() as cur:
                    await cur.execute('SELECT channel FROM whitelist WHERE guild = ? AND channel = ?',(ctx.guild.id, channel.id))
                    list = await cur.fetchone()
                    if list:
                        em = discord.Embed(description=f"<#{channel.id}> - [{channel.id}] is already whitelisted.")
                        return await ctx.send(content=f"{ctx.author.mention}", embed=em)
                    if not list:  
                        await cur.execute("INSERT OR REPLACE INTO whitelist (channel, guild) VALUES (?,?)",(channel.id, ctx.guild.id,))     
                        await cb.commit()   
                        await cb.cursor()        
                        await cur.execute('SELECT channel FROM whitelist WHERE guild = ?',(ctx.guild.id,))
                        list = await cur.fetchall()
                        if list:
                            desc = ""
                            count= 0
                            for table in list:
                                count +=1
                                #chan = ctx.guild.get_channel(table[0])
                                desc += f"**{count}**. <#{table[0]}>\n"
                            em = discord.Embed(title=f"{ctx.guild.name}'s Whitelisted channels", description=desc)
                            em.set_author(name=str(ctx.author.name) + " | Whitelist",icon_url=str(ctx.author.avatar_url),url="https://discord.gg/fendi") 
                            em.set_thumbnail(url="https://media.discordapp.net/attachments/876092097420226560/1019749215821377536/unknn.png")
                            #text = f"Successfully added <@{member}> to the owner's list."
                            return await ctx.send(content=f"{ctx.author.mention} Added {channel.mention} - [{channel.id}] to the server's Whitelisted channels.",embed=em)
                await cb.commit()
                await cb.cursor()
    
    @commands.command(name="blacklist", description="Allows a bot owner to blacklist whitelisted channels to stop the bot from monitoring messages in that channel anymore.",aliases=['unwhitelist','delwhitelist','bl'])
    @commands.check(is_admin)
    async def blacklist(self, ctx, channel: discord.TextChannel = None): 
        if channel is None:
            await ctx.send(embed=helpers.getembed(f"Please mention a channel to be blacklisted..\nExample: {await get_prefix(self,ctx)}blacklist {ctx.channel.mention}\nExample: {await get_prefix(self,ctx)}blacklist {ctx.channel.id}"))
        if channel:
            async with aiosqlite.connect(db_path("channels")) as cb:
                async with cb.cursor() as cur:
                    await cur.execute('SELECT channel FROM whitelist WHERE guild = ? AND channel = ?',(ctx.guild.id, channel.id))
                    list = await cur.fetchone()
                    if list is None:
                        em = discord.Embed(description=f"<#{channel.id}> - [{channel.id}] is already blacklisted")
                        return await ctx.send(content=f"{ctx.author.mention}", embed=em)
                    if list:
                        await cur.execute("DELETE FROM whitelist WHERE channel = ? AND guild = ?", (channel.id, ctx.guild.id))
                        await cb.commit()
                        await cb.cursor()
                        await cur.execute('SELECT channel FROM whitelist WHERE guild = ?',(ctx.guild.id,))
                        list = await cur.fetchall()
                        if list:
                            desc = ""
                            count= 0
                            for table in list:
                                count +=1
                                desc += f"**{count}**. <#{table[0]}>\n"
                            em = discord.Embed(title=f"{ctx.guild.name}'s Whitelisted channels", description=desc)
                            em.set_author(name=str(ctx.author.name) + " | Whitelist",icon_url=str(ctx.author.avatar_url),url="https://discord.gg/fendi") 
                            em.set_thumbnail(url="https://media.discordapp.net/attachments/876092097420226560/1019749215821377536/unknn.png")
                            return await ctx.send(content=f"{ctx.author.mention} Removed {channel.mention} - [{channel.id}] from the server's Whitelisted channels.\nCurrent whitelisted channels.",embed=em)
                        else:
                            return await ctx.send(content=f"{ctx.author.mention} Removed {channel.mention} - [{channel.id}] from the server's Whitelisted channels.",embed=helpers.getembed(f"There are no whitelisted channels in {ctx.guild.name}"))
        
    @commands.command(name="whitelisted", description="Displays the channels that the bot is allowed to monitor messages in for the server activity leaderboard.",aliases=['channels','wlisted'])
    @commands.check(is_admin)
    #@commands.check(is_owner)
    async def whitelisted(self, ctx):
        async with aiosqlite.connect(db_path("channels")) as ab:
            async with ab.cursor() as cursor:
                await cursor.execute('SELECT channel FROM whitelist WHERE guild = ?',(ctx.guild.id,))
                list = await cursor.fetchall()
                if list:
                    desc = ""
                    count= 0
                    for table in list:
                        count +=1
                        desc += f"**{count}**. <#{table[0]}>\n"
                    em = discord.Embed(title=f"{ctx.guild.name}'s Whitelisted channels", description=desc)
                    em.set_author(name=str(ctx.author.name) + " | Whitelist",icon_url=str(ctx.author.avatar_url),url="https://discord.gg/fendi") 
                    em.set_thumbnail(url="https://media.discordapp.net/attachments/876092097420226560/1019749215821377536/unknn.png")
                    return await ctx.send(embed=em)
                else: return await ctx.send(embed=helpers.getembed("There are currently no Whitelisted Channels in **{}**.".format(ctx.guild.name)))
    
    
def setup(bot):
    bot.add_cog(Ranking(bot)) 