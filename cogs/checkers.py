import discord, requests

from discord.ext import commands
from utils.checks import is_admin

class Checkers(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
  
  def checkURL(self, url):
    try:
      r = requests.get(url)
      if r.status_code == 200:
        return True
    except:
      return False 
  
  @commands.command(name="serverbanner", description="Displays the server's banner.")
  @commands.cooldown(1,10,commands.BucketType.user)
  async def serverbanner(self, ctx):
    if await is_admin(ctx):
      self.serverbanner.reset_cooldown(ctx)
    if self.checkURL(ctx.guild.banner_url) == True:
      embed = discord.Embed(colour=ctx.author.color, description=f"{ctx.guild.name}'s Current Banner!")
      embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
      embed.set_image(url=ctx.guild.banner_url)
      await ctx.send(embed=embed)
    else:
        await ctx.send(embed=discord.Embed(description=f"❌ {ctx.guild.name} Currently Has No Banner!", colour=0xf04947), delete_after=5)

  @commands.command(name="servericon", description="Displays the server's icon.")
  @commands.cooldown(1,60,commands.BucketType.channel)
  async def servericon(self, ctx):
    if await is_admin(ctx):
      self.servericon.reset_cooldown(ctx)
    if self.checkURL(ctx.guild.icon_url) == True:
        embed = discord.Embed(colour=ctx.author.color, description=f"{ctx.guild.name}'s Current Server Icon!")
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
        embed.set_image(url=ctx.guild.icon_url)
        await ctx.send(embed=embed)
    else:
        await ctx.send(embed=discord.Embed(description=f"❌ {ctx.guild.name} Currently Has No Icon!", colour=0xf04947), delete_after=5)

def setup(bot):
    bot.add_cog(Checkers(bot))
