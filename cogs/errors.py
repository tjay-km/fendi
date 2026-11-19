import discord, math

from discord.ext import commands

def humanify(seconds):
    seconds = math.ceil(seconds)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours,24)

    items = []
    if days !=0:
        items.append(f"**{days} days**")
    if hours != 0:
        items.append(f"**{hours} hours**")
    if minutes != 0:
        items.append(f"**{minutes} minutes**")
    if seconds != 0:
        items.append(f"**{seconds} seconds!**")

    if len(items) == 0:
        return ""
    if len(items) == 1:
        return items[0]
    elif len(items) == 2:
        return f"{items[0]} and {items[1]}"
    elif len(items) == 3:
        items[-1] = "and " + items[-1]
        return ", ".join(items)
    elif len(items) == 4:
        items[-2] = "and " + items[-2]
        return ", ".join(items)

class Errors(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.errors.CommandNotFound):
            """ Command not found error """
            pass

        elif isinstance(error, commands.errors.MissingPermissions):
            """ Missing Perms error """
            await ctx.send(embed=discord.Embed(description=f"❌ **{ctx.author.display_name}** Is Missing Permission To Do That!", colour=0xf04947), delete_after=5)

        elif isinstance(error, commands.errors.MissingRequiredArgument):
            """ Missing Required Arguments error """
            await ctx.send(embed=discord.Embed(description=f"❌ **{error.param.name}** Is A Required Argument!", colour=0xf04947), delete_after=5)
            #await ctx.send(embed=discord.Embed(description=f"❌ A Required Argument Is Missing!", colour=0xf04947), delete_after=5)

        elif isinstance(error, commands.errors.BotMissingPermissions):
            """ Bot missing Permissions error """
            await ctx.send(embed=discord.Embed(description=f"❌ **{self.bot.user.name}** Is Missing Permission To That!", colour=0xf04947), delete_after=5)

        elif isinstance(error, commands.errors.CommandOnCooldown):
            """ Command Cooldown """
            await ctx.send(embed=discord.Embed(description=f"❌ Command On Cooldown! Try Again In {humanify(error.retry_after)}", colour=0xf04947), delete_after=5)

        elif isinstance(error, commands.errors.CheckFailure):
            """ Check Failure """
            await ctx.send(embed=discord.Embed(description=f"❌ **{ctx.author.display_name}** You do not have access to this command!",color=0xf04947), delete_after=5)
        
        elif isinstance(error, commands.errors.DisabledCommand):
            """ Disabled Command """
            await ctx.send(embed=discord.Embed(description=f"❌ **{ctx.author.display_name}** This command is disabled!",color=0xf04947), delete_after=5)

        elif isinstance(error, commands.errors.CommandInvokeError):
            """ Not Loaded Command """
            await ctx.send(embed=discord.Embed(description=f"❌ **{ctx.author.display_name}** {error}",color=0xf04947), delete_after=5)
            print(error)
        elif isinstance(error, commands.errors.RoleNotFound):
            """ Role Not Found """
            await ctx.send(embed=discord.Embed(description=f"❌ **{ctx.author.display_name}** Role Not found!",color=0xf04947), delete_after=5)

        elif isinstance(error, discord.errors.Forbidden):
            """ Discord Forbidden """
            pass

        elif isinstance(error, discord.errors.NotFound):
            """ Not Found """
            pass

        elif isinstance(error, discord.Forbidden):
            """ Not Found """
            pass           

        else:
            raise error

def setup(bot):
    bot.add_cog(Errors(bot))
