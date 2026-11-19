from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from utils.config import OWNER_IDS

#rate: how many times the command can be used before triggering the cooldown
rate = 1
#per: the amount of seconds the cooldown lasts
per = 10
#type: the scope of the cooldown, go to https://discordpy.readthedocs.io/en/latest/ext/commands/api.html#discord.ext.commands.cooldown to see what they are
t = BucketType.default

class Cooldowns(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        #whitelist: the list of IDs of people/roles/channels/things to ignore
        #to whitelist someone/something, add their ID to the whitelist
        self.whitelist = list(OWNER_IDS)
    
    #example command
    @commands.command(
        name = 'command',
        description = 'example description',
    )
    #cooldown
    @commands.cooldown(rate, per, t)
    async def example_command(self, ctx):
        #put your command things here
        pass

    @example_command.after_invoke
    async def reset_cooldown(self, ctx):
        for e in self.whitelist:
            #to whitelist a person:
            if e == ctx.author.id:
                self.example_command.reset_cooldown(ctx)

            #to whitelist a channel:
            if e == ctx.message.channel.id:
                self.example_command.reset_cooldown(ctx)

            #to whitelist a guild/server:
            if e == ctx.message.guild.id:
                self.example_command.reset_cooldown(ctx)

            #to whitelist a role:
            if e in [role.id for role in ctx.author.roles]:
                self.example_command.reset_cooldown(ctx)

#cog setup function
def setup(bot):
    bot.add_cog(Cooldowns(bot))