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

    @commands.command(hidden=True)
    @ctx_wrapper(user_req=2)
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
    @error_wrapper()
    async def loadCommandError(self, ctx, error):
        if isinstance(error, commands.errors.MissingPermissions):
            await ctx.sendError("Only admins can use this.")

    @commands.command(hidden=True)
    @ctx_wrapper(user_req=2)
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
    @error_wrapper()
    async def unloadCommandError(self, ctx, error):
        if isinstance(error, commands.errors.MissingPermissions):
            await ctx.sendError("Only admins can use this.")

    @commands.command(name='reload', hidden=True)
    @ctx_wrapper(user_req=2)
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
    @error_wrapper()
    async def reloadCommandError(self, ctx, error):
        if isinstance(error, commands.errors.MissingPermissions):
            await ctx.sendError("Only admins can use this.")


async def setup(bot):
    await bot.add_cog(CogUtils(bot))
