import discord, datetime, random, io, aiohttp, platform

from utils import helpers
from discord.ext import commands
from aiohttp import ClientSession
from time import time
from utils.checks import is_admin
from utils.prefix import get_prefix

start_time = datetime.datetime.utcnow()

class Miscellaneous(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = ClientSession()
        self.snipeCache = {}
        self.editSnipeCache = {}
        self.afterSnipeCache = {}
        self.badwords = ("discord.gg", ".gg", ".gg/", "discord.gg/", "/invite/")
    
    @commands.command(name="ping", description="Displays the bot's ping.")
    @commands.cooldown(1,60,commands.BucketType.user)
    async def ping(self, ctx):
        if await is_admin(ctx):
            self.ping.reset_cooldown(ctx)
        start = time()
        msg = await ctx.send(embed=discord.Embed(description='⏳ Loading...', color=0x7385da))
        end = time()
        embed=discord.Embed(
            description=f"✅ Currently Online!\nLatency: `{round(self.bot.latency * 1000)}ms`\nResponse: `{(end-start)*1000:,.0f}ms`", 
            colour=0x43b581
        )
        embed.set_author(name=f"{self.bot.user.name} Ping!", icon_url=self.bot.user.avatar_url)
        await msg.edit(embed=embed)

    @commands.command(name="uptime", description="Displays the bot's uptime.")
    @commands.cooldown(1,60,commands.BucketType.user)
    async def uptime(self, ctx):
        if await is_admin(ctx):
            self.uptime.reset_cooldown(ctx)

        uptime = datetime.datetime.utcnow() - start_time
        uptime = str(uptime).split('.')[0]
        embed=discord.Embed(description="Current: "+'**'+uptime+'**', color=ctx.author.color)
        embed.set_author(name=f"{self.bot.user.name}'s Uptime!", icon_url=self.bot.user.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(name="serverinfo", description="Displays information about the server.")
    @commands.cooldown(1,60,commands.BucketType.user)
    async def serverinfo(self, ctx):
        if await is_admin(ctx):
            self.serverinfo.reset_cooldown(ctx)

        prefix = await get_prefix(self,ctx)
        
        embed = discord.Embed(color=ctx.author.color,description=f"{ctx.guild.name} was created on {ctx.guild.created_at.strftime('%d %b %Y %H:%M')}",)
        embed.add_field(name='Owner', value=f"<@{ctx.guild.owner_id}>", inline=True)
        #embed.add_field(name='Region', value=f"{ctx.guild.region}", inline=True)
        embed.add_field(name='Boosts', value=f"{ctx.guild.premium_subscription_count} Boosters (Level {ctx.guild.premium_tier})", inline=True)
        embed.add_field(name='Users', value=f"{ctx.guild.member_count}", inline=True)
        embed.add_field(name='Roles', value="{}".format(len(ctx.guild.roles)-1), inline=True)
        embed.add_field(name='Server ID', value=f"{ctx.guild.id}", inline=True)
        embed.add_field(name='Total Channels', value="{}".format(len(ctx.guild.text_channels+ctx.guild.voice_channels)), inline=True)
        embed.add_field(name='Text Channels', value="{}".format(len(ctx.guild.text_channels)), inline=True)
        embed.add_field(name='Voice Channels', value="{}".format(len(ctx.guild.voice_channels)), inline=True)
        if ctx.guild.system_channel:
            embed.add_field(name='Systems Channel', value=f'<#{ctx.guild.system_channel.id}>', inline=True)
        embed.add_field(name='Verification Level', value=f'{ctx.guild.verification_level}', inline=True)
        embed.add_field(name='Server Prefix', value=f'{prefix}', inline=True)
        embed.set_author(name=f"{ctx.guild.name}", icon_url=ctx.guild.icon_url)
        embed.set_thumbnail(url=ctx.guild.icon_url)
        await ctx.send(embed=embed)

    @commands.command(name="userinfo", description="Displays information about the user's profile in the server.", aliases=['whois'])
    @commands.cooldown(1,10,commands.BucketType.user)
    async def userinfo(self, ctx, *, user: discord.Member = None):
        if await is_admin(ctx):
            self.userinfo.reset_cooldown(ctx)

        if user is None:
            user = ctx.author
        date_format = "%d %b %Y %I:%M"
        embed = discord.Embed(colour=ctx.author.color)
        embed.add_field(name="Joined Discord", value=user.created_at.strftime(date_format), inline=True)
        embed.add_field(name="Joined Server", value=user.joined_at.strftime(date_format), inline=True)
        embed.add_field(name="Avatar Link", value=f"[Avatar]({user.avatar_url})", inline=True)
        embed.add_field(name="User ID", value=str(user.id), inline=True)
        embed.add_field(name="Nickname", value=user.display_name, inline=True)
        embed.add_field(name="Total Roles", value="{}".format(len(user.roles)-1), inline=True)
        embed.set_author(name=str(user), icon_url=user.avatar_url)
        embed.set_thumbnail(url=user.avatar_url)
        if len(user.roles) > 30:
            embed.add_field(name="Roles [{}]".format(len(user.roles)-1), value="User Has More Than 30 Roles!", inline=False)
        else:
            role_string = ' '.join([r.mention for r in user.roles][1:])
            embed.add_field(name="Roles [{}]".format(len(user.roles)-1), value=role_string, inline=False)
        return await ctx.send(embed=embed)

    @commands.command(name="roleinfo", description="Displays information about the role.")
    @commands.cooldown(1,10,commands.BucketType.user)
    async def roleinfo(self, ctx, *, role: discord.Role):
        if await is_admin(ctx):
            self.roleinfo.reset_cooldown(ctx)

        try:    
            guild = ctx.guild
            role_created = role.created_at.strftime("%d %b %Y %H:%M")
            created_on = "{}".format(role_created)
            users = len([x for x in guild.members if role in x.roles])
            if str(role.colour) == "#000000":
                colour = "#000000"
                color = ("#%06x" % random.randint(0, 0xFFFFFF))
                color = int(colour[1:], 16)
            else:
                colour = str(role.colour).upper()
                color = role.colour
            embed = discord.Embed(
                colour=color
            )
            embed.add_field(name="Role Mention", value=f"<@&{role.id}>", inline=True)
            embed.add_field(name="Role ID", value=f"{role.id}", inline=True)
            embed.add_field(name="Color", value=f"{colour}", inline=True)
            embed.add_field(name="Position", value=f"{role.position}", inline=True)
            embed.add_field(name="Users", value=f"{users}", inline=True)
            embed.add_field(name="Hoisted", value=f"{role.hoist}", inline=True)
            embed.add_field(name="Mentionable", value=f"{role.mentionable}", inline=True)
            embed.add_field(name="Creation Date", value=f"{created_on}", inline=True)
            embed.add_field(name="Bot Role", value=f"{role.managed}", inline=True)
            embed.set_thumbnail(url=f"{ctx.guild.icon_url}")
            embed.set_author(name=f"{role.name}", icon_url=ctx.guild.icon_url)
            await ctx.send(embed=embed)
        except Exception:
            await ctx.send(embed=helpers.getembed(f""))

    @commands.command(name="avatar", description="Displays the user's avatar.",aliases=['av'])
    @commands.cooldown(1,5,commands.BucketType.user)
    async def avatar(self, ctx, *, user: discord.Member=None):
        if await is_admin(ctx):
            self.avatar.reset_cooldown(ctx)

        format = "gif"
        user = user or ctx.author
        if user.is_avatar_animated() != True:
	        format = "png"
        avatar = user.avatar_url_as(format = format if format != "gif" else None)
        embed = discord.Embed(colour=ctx.author.color, description=f"{user.display_name}'s Current Avatar!")
        embed.set_author(name=f"{self.bot.user.name}", icon_url=self.bot.user.avatar_url)
        embed.set_image(url=avatar)
        await ctx.send(embed=embed)

    @commands.command(name="stats", description="Displays guild and member stats  about the bot.")
    @commands.cooldown(1,60,commands.BucketType.user)
    async def stats(self, ctx):
        if await is_admin(ctx):
            self.stats.reset_cooldown(ctx)

        y = 0
        for x in self.bot.guilds:
            y += x.member_count
        embed=discord.Embed(
            colour=ctx.author.color,
            description=f"Total Guilds: **{len(self.bot.guilds)}** Guilds!\nTotal Users: **{y}** Users!"
        )
        embed.set_author(name=f"{self.bot.user.name} Stats!", icon_url=self.bot.user.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(name="membercount", description="Displays the server's member count",aliases=['mc'])
    @commands.cooldown(1,60,commands.BucketType.user)
    async def membercount(self, ctx):
        if await is_admin(ctx):
            self.membercount.reset_cooldown(ctx)

        server = ctx.message.author.guild
        memberCount = 0
        memberOnline = 0
        for member in server.members:
            memberCount += 1
            if not member.status == discord.Status.offline:
                memberOnline += 1
            embed=discord.Embed(
            colour=ctx.author.color,
            description=f"Total Members: **{ctx.guild.member_count}** Members!",
            #description=f"<:online:781981577395175484> Online - **{memberOnline}** Members!\n<:idle:781981577462284359> Idle - **nil** Members!\n<:dnd:781981577110224898> DND - **nil** Members!\n<:invis:781981577449177118> Offline - **nil** Members!"
        )
        embed.set_author(name=f"{ctx.guild.name} Membercount!", icon_url=self.bot.user.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(name="invite", description="Sends the bot invite.", aliases=['inv'])
    @commands.cooldown(1,60,commands.BucketType.user)
    async def invite(self, ctx):
        if await is_admin(ctx):
            self.invite.reset_cooldown(ctx)

        embed=discord.Embed(
            colour=ctx.author.color,
            description=f"[{ctx.bot.user.name} Invite!](https://discord.com/api/oauth2/authorize?client_id={ctx.bot.user.id}&permissions=8&scope=bot)"
        )
        embed.set_author(name=f"{self.bot.user.name}", icon_url=self.bot.user.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(name="enlarge", description="Enlarges the specified emoji.",aliases=['resize'])
    @commands.cooldown(1,30,commands.BucketType.user)
    async def enlarge(self, ctx, emoji: discord.Emoji, size: int = None):
        if await is_admin(ctx):
            self.enlarge.reset_cooldown(ctx)

        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{emoji.url}" + f"?size=512"
            ) as resp:
                image = await resp.read()
        if emoji.animated:
            with io.BytesIO(image) as file:
                await ctx.send(file=discord.File(file, "emote.gif"))
        else:
            with io.BytesIO(image) as file:
                await ctx.send(file=discord.File(file, "emote.png"))

    @commands.command(name="about", description="Shows information about the bot")
    @commands.cooldown(1,60,commands.BucketType.user)
    async def about(self, ctx):
        if await is_admin(ctx):
            self.about.reset_cooldown(ctx)

        uptime = datetime.datetime.utcnow() - start_time
        uptime = str(uptime).split('.')[0]
        y = 0
        for x in self.bot.guilds:
            y += x.member_count
        embed=discord.Embed(
            colour=ctx.author.color,
            description=f"{self.bot.user.name} was created on 16 Sep 2022 18:15"
        )
        embed.add_field(name="Developer!", value="Pre [ego#4444]", inline=True)
        embed.add_field(name="Homies!", value="Sipher, Nina, Fez", inline=False)
        embed.add_field(name="Library!", value=f"{platform.python_version()}/{discord.__version__}", inline=True)
        embed.add_field(name="Uptime!", value=uptime, inline=True)
        embed.add_field(name="Statistics!", value=f"**{len(self.bot.guilds)}** Guilds/**{y}** Users!", inline=False)
        embed.add_field(name="Bot Invite!", value=f"[{ctx.bot.user.name} Invite!](https://discord.com/api/oauth2/authorize?client_id={ctx.bot.user.id}&permissions=8&scope=bot)", inline=True)
        embed.add_field(name="Server!", value="[Discord Invite!](https://discord.gg/fendi)", inline=True)
        embed.set_author(name=f"{self.bot.user.name}'s Information!", icon_url=self.bot.user.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(name='urban',description="Searches the term in the urban dictionary",aliases=['ud'])
    @commands.cooldown(1,10,commands.BucketType.user)
    async def urban(self, ctx,  *, search: str):
        if await is_admin(ctx):
            self.urban.reset_cooldown(ctx)

        search2 = search.replace(" ", "-")
        r = await self.session.get(f"http://api.urbandictionary.com/v0/define?term={search2}")
        if r.status != 200:
            return await ctx.send(embed=discord.Embed(description=f"❌ Urban Dictionary API Unavailable!", colour=0xf04947))

        json = await r.json()
        list1 = json['list']
        if not list1:
            return await ctx.send(embed=discord.Embed(description=f"❌ Word Not Found In Urban Dictionary!", colour=0xf04947))

        res = list1[0]
        embed=discord.Embed(
            title=res['word'],
            description=res['definition'],
            color=ctx.author.color
        )
        embed.add_field(name="Date Written!", value=res['written_on'])
        embed.add_field(name="Author!", value=res['author'])
        embed.set_footer(text=f"👍 {res['thumbs_up']} | 👎 {res['thumbs_down']}")
        embed.set_author(name=f"{self.bot.user.name}!", icon_url=self.bot.user.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(name='revav',description="Reverse's the avatar of the user.")
    @commands.cooldown(1,10,commands.BucketType.user)
    async def revav(self, ctx, user: discord.Member=None):
        if await is_admin(ctx):
            self.revav.reset_cooldown(ctx)

        user = user or ctx.author
        embed=discord.Embed(
            description=f"https://images.google.com/searchbyimage?image_url={user.avatar_url}",
            color=ctx.author.color
        )
        embed.set_author(name=f"{self.bot.user.name}!", icon_url=self.bot.user.avatar_url)
        await ctx.send(embed=embed)


    @commands.command(name="snipe", aliases=['s'],description="Snipes the last deleted message.")
    async def snipe(self, ctx):
        try:
            if self.snipeCache[ctx.channel.id]["content"] in self.badwords:
                return await ctx.send(embed=discord.Embed(description=f"❌ Banned Word In Sniped Message!", colour=0xf04947), delete_after=5)
            if self.snipeCache[ctx.channel.id]['user'] == ctx.bot: pass
            #embed=discord.Embed(title=f"Message edited by {self.snipeCache[ctx.channel.id]['user']}",color=ctx.author.color, description=self.snipeCache[ctx.channel.id]["content"], timestamp=datetime.datetime.utcnow())
            embed=discord.Embed(description=self.snipeCache[ctx.channel.id]["content"], timestamp=datetime.datetime.utcnow())
            if self.snipeCache[ctx.channel.id]["image"] == []: pass
            else: embed.set_image(url=self.snipeCache[ctx.channel.id]["image"][0])
            embed.set_author(name=self.snipeCache[ctx.channel.id]["user"], icon_url=self.snipeCache[ctx.channel.id]['avatar_url'])
            #embed.set_footer(text=f"Sniped By: {ctx.author}")
            await ctx.send(embed=embed) 
            #del self.snipeCache[ctx.channel.id]
        except:
            return await ctx.send(embed=discord.Embed(description=f"❌ Nothing To Snipe!", colour=0xf04947), delete_after=5)

    @commands.command(name="editsnipe",description="Snipes the last edited message.",aliases=["esnipe"])
    async def editsnipe(self, ctx):
        try:
            if self.editSnipeCache[ctx.channel.id]["bcontent"] in self.badwords:
                return await ctx.send(embed=discord.Embed(description=f"❌ Banned Word In Sniped Message!", colour=0xf04947), delete_after=5)
            #embed=discord.Embed(title=f"Message edited by {self.editSnipeCache[ctx.channel.id]['user']} in **{self.afterSnipeCache[ctx.channel.id]['achannel']}**",color=ctx.author.color, description="**Old message**\n" + self.editSnipeCache[ctx.channel.id]["bcontent"] + "\n**New message**\n" + self.afterSnipeCache[ctx.channel.id]['acontent'], timestamp=datetime.datetime.utcnow())
            embed=discord.Embed(color=ctx.author.color, description="**Old message**\n" + self.editSnipeCache[ctx.channel.id]["bcontent"] + "\n**New message**\n" + self.afterSnipeCache[ctx.channel.id]['acontent'], timestamp=datetime.datetime.utcnow())
            embed.set_author(name=self.editSnipeCache[ctx.channel.id]["user"], icon_url=self.afterSnipeCache[ctx.channel.id]['avatar_url'])
            #embed.set_footer(text=f"Sniped By: {ctx.author}")
            await ctx.send(embed=embed)
            #del self.editSnipeCache[ctx.channel.id]
            #del self.afterSnipeCache[ctx.channel.id]
        except:
            return await ctx.send(embed=discord.Embed(description=f"❌ Nothing To Snipe!", colour=0xf04947), delete_after=5)


    @commands.Cog.listener()
    async def on_message_delete(self, message):

        self.snipeCache.update(
            {message.channel.id: {
            "user": message.author,
            "content": message.content,
            "avatar_url": message.author.avatar_url,
            "channel": message.channel.name,
            "image": message.attachments
        }})

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        self.editSnipeCache.update(
            {before.channel.id: {
                "user": before.author,
                "bcontent": before.content,
                "avatar_url": before.author.avatar_url
                
        }})
        self.afterSnipeCache.update({after.channel.id:{
                "user": after.author,
                "acontent": after.content,
                "avatar_url": after.author.avatar_url,
                "achannel": after.channel.name}})

def setup(bot):
    bot.add_cog(Miscellaneous(bot))
