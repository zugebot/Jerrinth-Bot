# Jerrin Shirks

# native imports

# custom imports
from files.jerrinth import JerrinthBot
from files.wrappers import *
from files.config import *
from files.support import *
import time


class AtSomeoneCog(commands.Cog):
    def __init__(self, bot):
        self.bot: JerrinthBot = bot

    @wrapper_command(name='someone', cooldown=SOMEONE_COOLDOWN)
    async def pingSomeoneCommand(self, ctx):

        self.bot.ensureUserExists(ctx)
        if self.bot.getUser(ctx).get("someone", None) is None:
            self.bot.getUser(ctx)["someone"] = EMPTY_SOMEONE.copy()

        if self.bot.getServer(ctx).get("someone", False):
            self.bot.getUser(ctx)["someone"]["use_total"] += 1
            self.bot.getUser(ctx)["someone"]["use_last"] = time.time()
            self.bot.saveData()

            user = random.choice(ctx.super.guild.members)
            await ctx.send(f"<@{user.id}>", allowed_mentions=True)
        else:
            await ctx.message.add_reaction("❌")

    @pingSomeoneCommand.error
    @wrapper_error()
    async def pingSomeoneCommandError(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            if self.bot.getServer(ctx).get("someone", False):
                if self.bot.getServer(ctx).get("show_time_left", True):
                    await ctx.send(f"Try again in **{error.retry_after:.3f}**s.")
                else:
                    await ctx.super.message.add_reaction(convertDecimalToClock(error.retry_after / SOMEONE_COOLDOWN[1]))
            else:
                await ctx.message.add_reaction("❌")
                self.pingSomeoneCommand.reset_cooldown(ctx.super)


async def setup(bot):
    await bot.add_cog(AtSomeoneCog(bot))

