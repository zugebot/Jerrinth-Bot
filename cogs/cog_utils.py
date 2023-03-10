# Jerrin Shirks

# native imports
import discord.ext.commands
from discord.ext import commands

# custom imports
from jerrinth import JerrinthBot
from wrappers import *
from support import *



class CogUtils(commands.Cog):
    def __init__(self, bot):
        self.bot: JerrinthBot = bot


    @commands.command(hidden=True)
    @is_jerrin
    @ctx_wrapper
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
    async def loadCommandError(self, ctx, error):
        if isinstance(error, commands.errors.MissingPermissions):
            await ctx.send(errorEmbed(description="Only admins can use this."))



    @commands.command(hidden=True)
    @is_jerrin
    @ctx_wrapper
    async def unloadCommand(self, ctx: discord.ext.commands.Context, module):
        """Unloads a module."""
        try:
            await self.bot.unload_extension(f"cogs.{module}")
            await ctx.message.add_reaction("✅")
        except Exception as e:
            await ctx.message.add_reaction("❌")
            if self.bot.getUser(ctx).get("debug", False):
                await ctx.send('{}: {}'.format(type(e).__name__, e))
    @unloadCommand.error
    @ctx_wrapper
    async def unloadCommandError(self, ctx, error):
        if isinstance(error, commands.errors.MissingPermissions):
            await ctx.send(errorEmbed(description="Only admins can use this."))


    @commands.command(name='reload', hidden=True)
    @is_jerrin
    @ctx_wrapper
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
    @ctx_wrapper
    async def reloadCommandError(self, ctx, error):
        if isinstance(error, commands.errors.MissingPermissions):
            await ctx.send(errorEmbed(description="Only admins can use this."))


async def setup(bot):
    await bot.add_cog(CogUtils(bot))
