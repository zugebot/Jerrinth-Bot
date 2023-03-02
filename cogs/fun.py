# Jerrin Shirks

# native imports
from discord.ext import commands
import random
import time

# custom imports
from jerrinth import JerrinthBot
from wrappers import *
from support import *
from config import *


class FunCog(commands.Cog):
    def __init__(self, bot):
        self.bot: JerrinthBot = bot
        self.eye_count = 12

    @commands.command(name='say', description='gg')
    @ctx_wrapper
    async def sayCommand(self, ctx):
        await ctx.send(ctx.super.message.content)

    @commands.command(name='8ball', description='Let the 8 Ball Predict!\n')
    @ctx_wrapper
    @channel_redirect
    async def _8ballCommand(self, ctx, *args):
        """allows the user to get randomized responses from their questions from the magical 8ball."""
        if args:
            response = "🎱 " + random.choice(RESPONSES_8BALL)
        else:
            response = "🎱 " + random.choice(BAD_RESPONSES_8BALL)
        return await ctx.send(response)


    @commands.command(name='findseed', description='Roll an end-portal eye count.\n')
    @discord.ext.commands.cooldown(*FINDSEED_COOLDOWN)
    @ctx_wrapper
    @channel_redirect
    async def findseedCommand(self, ctx):

        self.bot.ensureUserExists(ctx)
        if self.bot.getUser(ctx).get("findseed", None) is None:
            self.bot.getUser(ctx)["findseed"] = EMPTY_FUN.copy()
        self.bot.saveData()


        eyes = [random.random() for _ in range(self.eye_count)]
        e_empty = self.bot.getEmoji("mc_portal_empty")
        e_eye = self.bot.getEmoji("mc_portal_full")

        eyes_bool = [i > 0.9 for i in eyes]

        message = ""
        if self.bot.getUser(ctx).get("show_findseed_eyes", False):
            message = "".join([[e_empty, e_eye][eyes_bool[x]] for x in range(self.eye_count)]) + "\n"

        eye_count = sum(eyes_bool)

        self.bot.getUser(ctx)["findseed"]["eye_count"][eye_count] += 1
        self.bot.getUser(ctx)["findseed"]["total_uses"] += 1
        self.bot.getUser(ctx)["findseed"]["last_use"] = time.time()

        await ctx.send(message + f"<@{ctx.author.id}> → your seed is a **{eye_count}** eye.")

    @findseedCommand.error
    @ctx_wrapper
    async def findseedCommandError(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            if self.bot.getServer(ctx).get("show_time_left", True):
                await ctx.send(f"Try again in **{error.retry_after:.3f}**s.")
            else:
                await ctx.super.message.add_reaction(convertDecimalToClock(error.retry_after / FINDSEED_COOLDOWN[1]))


    @commands.command(name='someone', aliases=["SOMEONE"], description='Ping a random person!\n')
    @discord.ext.commands.cooldown(*SOMEONE_COOLDOWN)
    @ctx_wrapper
    @channel_redirect
    async def pingSomeoneCommand(self, ctx):

        self.bot.ensureUserExists(ctx)
        if self.bot.getUser(ctx).get("@someone", None) is None:
            self.bot.getUser(ctx)["@someone"] = EMPTY_SOMEONE.copy()

        if self.bot.getServer(ctx).get("@someone", False):
            self.bot.getUser(ctx)["@someone"]["total_uses"] += 1
            self.bot.getUser(ctx)["@someone"]["last_use"] = time.time()
            self.bot.saveData()

            user = random.choice(ctx.super.guild.members)
            await ctx.send(f"<@{user.id}>", allowed_mentions=True)
        else:
            await ctx.message.add_reaction("❌")

    @pingSomeoneCommand.error
    @ctx_wrapper
    async def pingSomeoneCommandError(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            if self.bot.getServer(ctx).get("@someone", False):
                if self.bot.getServer(ctx).get("show_time_left", True):
                    await ctx.send(f"Try again in **{error.retry_after:.3f}**s.")
                else:
                    await ctx.super.message.add_reaction(convertDecimalToClock(error.retry_after / SOMEONE_COOLDOWN[1]))
            else:
                await ctx.message.add_reaction("❌")
                self.pingSomeoneCommand.reset_cooldown(ctx.super)


async def setup(bot):
    await bot.add_cog(FunCog(bot))
