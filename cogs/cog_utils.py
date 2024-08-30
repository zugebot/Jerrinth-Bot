# Jerrin Shirks

# native imports
import discord.ext.commands

# custom imports
from files.jerrinth import JerrinthBot
from files.wrappers import *
from files.support import *


class CogUtils(commands.Cog):
    def __init__(self, bot):
        self.bot: JerrinthBot = bot

    @wrapper_command(name='load', hidden=True, user_req=2, redirect=False)
    async def loadCommand(self, ctx, module):
        """Loads a module."""
        try:
            await self.bot.load_extension(f"cogs.{module}")
            await ctx.message.add_reaction("✅")
        except Exception as e:
            await ctx.message.add_reaction("❌")
            if self.bot.getUser(ctx).get("debug", False):
                await ctx.send('{}: {}'.format(type(e).__name__, e))

    @loadCommand.error
    @wrapper_error()
    async def loadCommandError(self, ctx, error):
        if isinstance(error, commands.errors.MissingPermissions):
            await ctx.sendError("Only admins can use this.")

    @wrapper_command(name='unload', hidden=True, user_req=2, redirect=False)
    async def unloadCommand(self, ctx, module):
        """Unloads a module."""
        try:
            await self.bot.unload_extension(f"cogs.{module}")
            await ctx.message.add_reaction("✅")
        except Exception as e:
            await ctx.message.add_reaction("❌")
            if self.bot.getUser(ctx).get("debug", False):
                await ctx.send('{}: {}'.format(type(e).__name__, e))

    @unloadCommand.error
    @wrapper_error()
    async def unloadCommandError(self, ctx, error):
        if isinstance(error, commands.errors.MissingPermissions):
            await ctx.sendError("Only admins can use this.")

    @wrapper_command(name='reload', hidden=True, user_req=2, redirect=False)
    async def reloadCommand(self, ctx, module):
        """Reloads a module."""
        try:
            await self.bot.reload_extension(f"cogs.{module}")
            await ctx.message.add_reaction("✅")
        except Exception as e:
            await ctx.message.add_reaction("❌")
            if self.bot.getUser(ctx).get("debug", False):
                await ctx.send('{}: {}'.format(type(e).__name__, e))

    @reloadCommand.error
    @wrapper_error()
    async def reloadCommandError(self, ctx, error):
        if isinstance(error, commands.errors.MissingPermissions):
            await ctx.sendError("Only admins can use this.")


async def setup(bot):
    await bot.add_cog(CogUtils(bot))
