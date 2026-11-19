"""Paginated help command."""
from typing import List

import discord
from discord.ext import commands
from discord.ext.buttons import Paginator

from utils import helpers

COMMANDS_PER_PAGE = 6


class HelpPaginator(Paginator):
    async def teardown(self):
        try:
            await self.page.clear_reactions()
        except discord.HTTPException:
            pass


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    async def _usable_commands(source, ctx) -> List[commands.Command]:
        usable = []
        for command in source.walk_commands():
            if command.hidden or command.parent:
                continue
            try:
                if await command.can_run(ctx):
                    usable.append(command)
            except commands.CommandError:
                continue
        return sorted(usable, key=lambda command: command.name)

    @staticmethod
    def _describe(ctx, command: commands.Command, detailed: bool) -> str:
        text = f"• **__{command.name}__**\n{command.description or command.short_doc or 'No description.'}"
        if detailed:
            text += f"\n```{ctx.prefix}{command.qualified_name} {command.signature}```"
            if command.aliases:
                text += f"Aliases: {', '.join(command.aliases)}"
        return text

    async def _send_pages(self, ctx, command_list: List[commands.Command], title: str, detailed: bool = False):
        if not command_list:
            return await ctx.send(embed=helpers.error_embed("There are no commands you can use here."))
        pages = [
            "\n".join(self._describe(ctx, command, detailed) for command in command_list[i:i + COMMANDS_PER_PAGE])
            for i in range(0, len(command_list), COMMANDS_PER_PAGE)
        ]
        await HelpPaginator(title=title, color=helpers.COLOUR_ERROR, entries=pages, length=1).start(ctx)

    @commands.command(name="help", aliases=["cmds"], description="Shows the commands, a category or one command.")
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def help(self, ctx, *, entity: str = None):
        if entity is None:
            return await self._send_pages(ctx, await self._usable_commands(self.bot, ctx), self.bot.description)

        cog = next((cog for name, cog in self.bot.cogs.items() if name.lower() == entity.lower()), None)
        if cog is not None:
            return await self._send_pages(ctx, await self._usable_commands(cog, ctx), f"{cog.qualified_name} commands")

        command = self.bot.get_command(entity)
        if command is not None:
            return await self._send_pages(ctx, [command], command.qualified_name, detailed=True)

        await ctx.send(embed=helpers.error_embed(f"No command or category called **{entity}**."))


def setup(bot):
    bot.add_cog(Help(bot))
