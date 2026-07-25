# Jerrin Shirks

# native imports
import discord.ext.commands

# custom imports
from files.jerrinth import JerrinthBot
from files.wrappers import *
from files.support import *
from copy import deepcopy


class CogUtils(commands.Cog):
    def __init__(self, bot):
        self.bot: JerrinthBot = bot
        print(f"loading cog {self.__module__}")

    @wrapper_command(
        name='load',
        hidden=True,
        description='Load a cog by module name.\n',
        slash=False,
        slash_description='Load a cog by module name.',
        slash_args=[
            {
                "name": "module",
                "description": "Cog module name (e.g., main.cog_help).",
                "type": "string",
                "required": True
            }
        ],
        user_req=2,
        redirect=False,
        slash_user_ids=[
            611427346099994641
        ],
        slash_default_permissions={"administrator": True},
    )
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

    @wrapper_command(
        name='unload',
        hidden=True,
        description='Unload a cog by module name.\n',
        slash=False,
        slash_description='Unload a cog by module name.',
        slash_args=[
            {
                "name": "module",
                "description": "Cog module name or __init__ for all.",
                "type": "string",
                "required": True
            }
        ],
        user_req=2,
        redirect=False,
        slash_user_ids=[
            611427346099994641
        ],
        slash_default_permissions={"administrator": True},
    )
    async def unloadCommand(self, ctx, module):
        """Unloads a module."""

        if module == "__init__":
            unloaded = []
            errors = []

            # Iterate over all loaded cogs
            cogs_to_unload = [(cog_name, cog.__module__)
                              for cog_name, cog in self.bot.cogs.items()
                              if cog.__module__.startswith("cogs.")]

            for cog_name, module in cogs_to_unload:
                try:
                    await self.bot.unload_extension(module)  # Unload the cog
                    unloaded.append(cog_name)
                except Exception as e:
                    errors.append(f"{cog_name}: {type(e).__name__}: {e}")

            # Provide feedback to the user
            if unloaded:
                await ctx.send(f"Successfully unloaded: {', '.join(unloaded)}")
            if errors:
                await ctx.send(f"Errors occurred while unloading:\n" + "\n".join(errors))
            if not unloaded and not errors:
                await ctx.send("No cogs from the `cogs` folder were found to unload.")
            return

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

    @wrapper_command(
        name='reload',
        hidden=True,
        description='Reload a cog by module name.\n',
        slash=False,
        slash_description='Reload a cog by module name.',
        slash_args=[
            {
                "name": "module",
                "description": "Cog module name (e.g., main.cog_help).",
                "type": "string",
                "required": True
            }
        ],
        user_req=2,
        redirect=False,
        slash_user_ids=[
            611427346099994641
        ],
        slash_default_permissions={"administrator": True},
    )
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