# Jerrin Shirks

# native imports

# custom imports
from files.jerrinth import JerrinthBot
from files.wrappers import *
from files.config import *
from files.support import *


class DefaultCog(commands.Cog):
    def __init__(self, bot):
        self.bot: JerrinthBot = bot

    @wrapper_command(name="test_", user_req=0, var_types={0: "num", 1: "ping"}, redirect=False)
    async def testCommand(self, ctx, var, user):
        await ctx.send(f"var: {var}, user: {user}")

    @testCommand.error
    @wrapper_error()
    async def testCommandError(self, ctx, error):
        pass


async def setup(bot):
    await bot.add_cog(DefaultCog(bot))
