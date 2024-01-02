# Jerrin Shirks

# native imports
import time
import math

# custom imports
from files.jerrinth import JerrinthBot
from files.wrappers import *
from files.config import *
from old_code.moderation import *


class FunCog(commands.Cog):
    def __init__(self, bot):
        self.bot: JerrinthBot = bot

        self.eye_count = 12

    def prob_of_n_tens(self, n):
        numerator = math.comb(self.eye_count, n) * (9 ** (self.eye_count - n))
        denominator = 10 ** self.eye_count
        return numerator / denominator

    """
    @commands.command(name='say', description='gg')
    @ctx_wrapper(redirect=True)
    async def sayCommand(self, ctx):
        text = ctx.super.message.content
        text = removePings(text[5:], allowed=ctx.user)
        if not text:
            return await ctx.send("You can't just make me say nothing silly!")

        restricted = await testModeration(ctx, text)
        if restricted:
            return

        texts = splitStringIntoSegments(text)
        for text in texts:
            await ctx.send(text)
    """

    @commands.command(name='8ball', description='Let the 8 Ball Predict!\n')
    @ctx_wrapper(redirect=True)
    async def _8ballCommand(self, ctx, *args):
        """allows the user to get randomized responses from their questions from the magical 8ball."""
        if args:
            response = "🎱 " + random.choice(RESPONSES_8BALL)
        else:
            response = "🎱 " + random.choice(BAD_RESPONSES_8BALL)
        return await ctx.send(response)

    """
    @commands.command(name='etest')
    @ctx_wrapper(redirect=True)
    async def eyeTestCommand(self, ctx):
        eyes = self.bot.getUser(ctx)["findseed"]["eye_count"].copy()
        z_score = sum([(eye_c - self.eye_mean) / self.eye_variance for eye_c in eyes])
        return await ctx.sendEmbed(f"Your Z-Score: {z_score}")
    """

    @commands.command(name='findseed', description='Roll an end-portal eye count.\n')
    @discord.ext.commands.cooldown(*FINDSEED_COOLDOWN)
    @ctx_wrapper(redirect=True)
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
    @error_wrapper(use_cooldown=True)
    async def findseedCommandError(self, ctx, error):
        pass

    @commands.command(name='someone', aliases=["SOMEONE"], description='Ping a random person!\n')
    @discord.ext.commands.cooldown(*SOMEONE_COOLDOWN)
    @ctx_wrapper(redirect=True)
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
    @error_wrapper()
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
