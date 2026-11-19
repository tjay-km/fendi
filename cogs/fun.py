import discord, random

from discord.ext import commands
from utils.checks import is_admin

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        #self.whitelist = list(OWNER_IDS)
        
        
    @commands.command(name="pp", description="Sends a random dick size for the user.")
    @commands.cooldown(1,5,commands.BucketType.user)
    async def pp(self, ctx, *, member: discord.Member = None):
        if await is_admin(ctx):
            self.pp.reset_cooldown(ctx)
        string = ""
        for x in range(random.randint(1, 15)):
            string += "="
        if member is None:
            member = ctx.author   
            embed = discord.Embed(
                title=f"Your pp", description=f"8{string}D")
            await ctx.channel.send(embed=embed)
        if len(ctx.message.mentions) > 0: 
            member = ctx.message.mentions[0]
            embed = discord.Embed(
                title=f"{member.name}'s pp", description=f"8{string}D", color="2f3136")
            await ctx.channel.send(embed=embed)

    @commands.command(name="iq", description="Sends a random iq for the user.")
    @commands.cooldown(1,5,commands.BucketType.user)
    async def iq(self, ctx, member: discord.Member = None):
        if await is_admin(ctx):
            self.iq.reset_cooldown(ctx)
        if member is None:
            member = ctx.author
            embed = discord.Embed(title=f"IQ Test:")
            embed.add_field(name=f"Your IQ is",value=random.randint(1,100),inline=False)
            await ctx.send(embed=embed)
        if len(ctx.message.mentions) > 0: 
            member = ctx.message.mentions[0]
            embed = discord.Embed(title=f"IQ Test:")
            embed.add_field(name=f"{member.name}'s IQ is",value=random.randint(1,100),inline=False)
            await ctx.send(embed=embed)

    @commands.command(name = "thotrate", description= "Checks how much of a thot the user is.", aliases=['thot'])
    @commands.cooldown(1,5,commands.BucketType.user)
    async def thotrate(self, ctx, member: discord.Member = None):
        if await is_admin(ctx):
            self.thotrate.reset_cooldown(ctx)
        # if member.id == OWNER_ID:
        #     embed = discord.Embed(color=0x36393F)
        #     embed.set_thumbnail(url = 'https://cdn.discordapp.com/emojis/719666107878735874.png')
        #     embed.add_field(name=f"You are",value=f"{random.randint(1,10)}% thot",inline=False)
        #     await ctx.send(embed=embed)
        if member is None:
            member = ctx.author
            #if member.id == OWNER_ID:
                
            embed = discord.Embed(color=0x36393F)
            embed.set_thumbnail(url = 'https://cdn.discordapp.com/emojis/719666107878735874.png')
            embed.add_field(name=f"You are",value=f"{random.randint(1,100)}% thot",inline=False)
            await ctx.send(embed=embed)
        if len(ctx.message.mentions) > 0: 
            member = ctx.message.mentions[0]
            embed = discord.Embed(color=0x36393F)
            embed.set_thumbnail(url = 'https://cdn.discordapp.com/emojis/719666107878735874.png')
            embed.add_field(name=f"{member.name} is",value=f"{random.randint(1,100)}% thot",inline=False)
            await ctx.send(embed=embed)

    @commands.command(name="gayrate",aliases=['gay','howgay'], description="Checks how gay the user is.")
    @commands.cooldown(1,5,commands.BucketType.user)
    async def gayrate(self, ctx, member: discord.Member = None):
        if await is_admin(ctx):
            self.gayrate.reset_cooldown(ctx)
        if member is None:
            member = ctx.author
            embed = discord.Embed(color=0x36393F)
            embed.add_field(name=f"You are",value=f"{random.randint(1,100)}% gay🌈",inline=False)
            embed.set_thumbnail(url = 'https://cdn.discordapp.com/emojis/719666107878735874.png')
            await ctx.send(embed=embed)
        if len(ctx.message.mentions) > 0: 
            member = ctx.message.mentions[0]
            embed = discord.Embed(color=0x36393F)
            embed.add_field(name=f"{member.name} is",value=f"{random.randint(1,100)}% gay🌈",inline=False)
            embed.set_thumbnail(url = 'https://cdn.discordapp.com/emojis/719666107878735874.png')
            await ctx.send(embed=embed)

    @commands.command(name="height", description="Sends a random height for the user.")
    @commands.cooldown(1,5,commands.BucketType.user)
    async def height(self, ctx, member: discord.Member = None):
        if await is_admin(ctx):
            self.height.reset_cooldown(ctx)
        if ctx.author.id == await is_admin(ctx): 
            ctx.command.reset_cooldown(ctx)
        if member is None:
            member = ctx.author
            embed = discord.Embed(color=0x36393F)
            embed.add_field(name=f"You are",value=f"{random.randint(1,7)}'{random.randint(1,12)} ft tall.",inline=False)
            await ctx.send(embed=embed)
        if len(ctx.message.mentions) > 0: 
            member = ctx.message.mentions[0]
            embed = discord.Embed(color=0x36393F)
            embed.add_field(name=f"{member.name} is",value=f"{random.randint(1,7)}'{random.randint(1,12)} ft tall.",inline=False)
            await ctx.send(embed=embed)

            
        
def setup(bot):
    bot.add_cog(Fun(bot))