"""Information about the bot, the server and its members."""
import platform
import time

import discord
from discord.ext import commands

from utils import helpers
from utils.config import SUPPORT_INVITE

DATE_FORMAT = "%d %b %Y %H:%M"
MAX_ROLES_SHOWN = 30


def _invite_url(bot) -> str:
    return discord.utils.oauth_url(bot.user.id, permissions=discord.Permissions(8))


class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def _bot_embed(self, ctx, title: str, description: str = discord.Embed.Empty) -> discord.Embed:
        embed = discord.Embed(description=description, colour=ctx.author.colour)
        embed.set_author(name=title, icon_url=self.bot.user.avatar_url)
        return embed

    # --------------------------------------------------------------------- bot
    @commands.command(name="ping", description="Shows the bot's latency.")
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def ping(self, ctx):
        started = time.perf_counter()
        message = await ctx.send(embed=helpers.info_embed("⏳ Pinging..."))
        response_ms = (time.perf_counter() - started) * 1000

        embed = helpers.success_embed(
            f"Online!\nLatency: `{self.bot.latency * 1000:.0f}ms`\nResponse: `{response_ms:.0f}ms`"
        )
        embed.set_author(name=f"{self.bot.user.name} Ping", icon_url=self.bot.user.avatar_url)
        await message.edit(embed=embed)

    @commands.command(name="uptime", description="Shows how long the bot has been online.")
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def uptime(self, ctx):
        await ctx.send(embed=self._bot_embed(ctx, f"{self.bot.user.name}'s Uptime",
                                             f"**{helpers.uptime_since(self.bot.start_time)}**"))

    @commands.command(name="stats", description="Shows how many servers and users the bot serves.")
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def stats(self, ctx):
        users = sum(guild.member_count for guild in self.bot.guilds)
        await ctx.send(embed=self._bot_embed(
            ctx, f"{self.bot.user.name} Stats",
            f"Servers: **{len(self.bot.guilds)}**\nUsers: **{users}**",
        ))

    @commands.command(name="invite", aliases=["inv"], description="Sends the bot's invite link.")
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def invite(self, ctx):
        await ctx.send(embed=self._bot_embed(
            ctx, self.bot.user.name, f"[Invite {self.bot.user.name}]({_invite_url(self.bot)})"
        ))

    @commands.command(name="about", description="Shows information about the bot.")
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def about(self, ctx):
        users = sum(guild.member_count for guild in self.bot.guilds)
        embed = self._bot_embed(
            ctx, f"About {self.bot.user.name}",
            f"{self.bot.user.name} was created on {self.bot.user.created_at.strftime(DATE_FORMAT)}",
        )
        embed.add_field(name="Developer", value="@1v1", inline=True)
        embed.add_field(name="Library", value=f"Python {platform.python_version()} / discord.py {discord.__version__}",
                        inline=True)
        embed.add_field(name="Uptime", value=helpers.uptime_since(self.bot.start_time), inline=False)
        embed.add_field(name="Statistics", value=f"**{len(self.bot.guilds)}** servers / **{users}** users", inline=False)
        embed.add_field(name="Links", value=f"[Invite]({_invite_url(self.bot)}) | [Support server]({SUPPORT_INVITE})",
                        inline=False)
        await ctx.send(embed=embed)

    # ------------------------------------------------------------------ server
    @commands.command(name="serverinfo", description="Shows information about this server.")
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def serverinfo(self, ctx):
        guild = ctx.guild
        embed = discord.Embed(colour=ctx.author.colour,
                              description=f"Created on {guild.created_at.strftime(DATE_FORMAT)}")
        embed.set_author(name=guild.name, icon_url=helpers.icon(guild.icon_url))
        helpers.set_thumbnail(embed, guild.icon_url)

        fields = [
            ("Owner", f"<@{guild.owner_id}>"),
            ("Boosts", f"{guild.premium_subscription_count} (Level {guild.premium_tier})"),
            ("Members", guild.member_count),
            ("Roles", len(guild.roles) - 1),
            ("Text Channels", len(guild.text_channels)),
            ("Voice Channels", len(guild.voice_channels)),
            ("Verification", str(guild.verification_level).title()),
            ("Prefix", f"`{self.bot.db.prefix_for(guild.id)}`"),
            ("Server ID", guild.id),
        ]
        if guild.system_channel:
            fields.append(("System Channel", guild.system_channel.mention))
        for name, value in fields:
            embed.add_field(name=name, value=value, inline=True)
        await ctx.send(embed=embed)

    @commands.command(name="membercount", aliases=["mc"], description="Shows the server's member count.")
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def membercount(self, ctx):
        bots = sum(member.bot for member in ctx.guild.members)
        embed = discord.Embed(
            colour=ctx.author.colour,
            description=f"Members: **{ctx.guild.member_count}**\n"
                        f"Humans: **{ctx.guild.member_count - bots}**\nBots: **{bots}**",
        )
        embed.set_author(name=f"{ctx.guild.name} Member Count", icon_url=helpers.icon(ctx.guild.icon_url))
        await ctx.send(embed=embed)

    @commands.command(name="servericon", description="Shows the server's icon.")
    @commands.cooldown(1, 60, commands.BucketType.channel)
    async def servericon(self, ctx):
        if not ctx.guild.icon:
            return await ctx.send(embed=helpers.error_embed(f"{ctx.guild.name} has no icon."), delete_after=5)
        embed = self._bot_embed(ctx, self.bot.user.name, f"{ctx.guild.name}'s icon")
        embed.set_image(url=ctx.guild.icon_url_as(static_format="png", size=1024))
        await ctx.send(embed=embed)

    @commands.command(name="serverbanner", description="Shows the server's banner.")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def serverbanner(self, ctx):
        if not ctx.guild.banner:
            return await ctx.send(embed=helpers.error_embed(f"{ctx.guild.name} has no banner."), delete_after=5)
        embed = self._bot_embed(ctx, self.bot.user.name, f"{ctx.guild.name}'s banner")
        embed.set_image(url=ctx.guild.banner_url)
        await ctx.send(embed=embed)

    # ----------------------------------------------------------------- members
    @commands.command(name="userinfo", aliases=["whois"], description="Shows information about a member.")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def userinfo(self, ctx, *, member: discord.Member = None):
        member = member or ctx.author
        roles = [role.mention for role in reversed(member.roles[1:])]

        embed = discord.Embed(colour=member.colour)
        embed.set_author(name=str(member), icon_url=member.avatar_url)
        embed.set_thumbnail(url=member.avatar_url)
        embed.add_field(name="Joined Discord", value=member.created_at.strftime(DATE_FORMAT), inline=True)
        embed.add_field(name="Joined Server",
                        value=member.joined_at.strftime(DATE_FORMAT) if member.joined_at else "Unknown", inline=True)
        embed.add_field(name="Nickname", value=member.display_name, inline=True)
        embed.add_field(name="User ID", value=member.id, inline=True)
        embed.add_field(name="Avatar", value=f"[Link]({member.avatar_url})", inline=True)
        if len(roles) > MAX_ROLES_SHOWN:
            roles_text = f"Too many to show ({len(roles)})."
        else:
            roles_text = " ".join(roles) or "None"
        embed.add_field(name=f"Roles [{len(roles)}]", value=roles_text, inline=False)
        await ctx.send(embed=embed)

    @commands.command(name="roleinfo", description="Shows information about a role.")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def roleinfo(self, ctx, *, role: discord.Role):
        embed = discord.Embed(colour=role.colour)
        embed.set_author(name=role.name, icon_url=helpers.icon(ctx.guild.icon_url))
        helpers.set_thumbnail(embed, ctx.guild.icon_url)
        fields = [
            ("Mention", role.mention),
            ("Role ID", role.id),
            ("Colour", str(role.colour).upper()),
            ("Position", role.position),
            ("Members", len(role.members)),
            ("Hoisted", role.hoist),
            ("Mentionable", role.mentionable),
            ("Managed", role.managed),
            ("Created", role.created_at.strftime(DATE_FORMAT)),
        ]
        for name, value in fields:
            embed.add_field(name=name, value=value, inline=True)
        await ctx.send(embed=embed)

    @commands.command(name="avatar", aliases=["av"], description="Shows a member's avatar.")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def avatar(self, ctx, *, member: discord.Member = None):
        member = member or ctx.author
        embed = self._bot_embed(ctx, self.bot.user.name, f"{member.display_name}'s avatar")
        embed.set_image(url=member.avatar_url_as(static_format="png", size=1024))
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Info(bot))
