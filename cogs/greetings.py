
from discord.ext import commands

class Greetings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    # @commands.Cog.listener()
    # async def on_member_join(self, member):
    #     channel = member.guild.system_channel
    #     if channel is not None:
    #         text = '<@{}> Welcome to **{}** <3\nhead out to <#CHANNEL_ID> & <#CHANNEL_ID>\nMake sure to invite your friends.\nHit **level 15** or **boost** to get pic perms :3 \nRead the rules & be active <33'.format(member.id, member.guild.name)
    #         await channel.send(content=f'{member.mention}',embed=helpers.getembed(text))

    # @commands.command()
    # async def hello(self, ctx, *, member: discord.Member = None):  # type: ignore
    #     """Says hello"""
    #     member = member or ctx.author
    #     if self._last_member is None or self._last_member.id != member.id:  # type: ignore
    #         await ctx.send(f'Hello {member.name}~')  # type: ignore
    #     else:
    #         await ctx.send(f'Hello {member.name}... This feels familiar.')  # type: ignore
    #     self._last_member = member

def setup(bot):
    bot.add_cog(Greetings(bot))