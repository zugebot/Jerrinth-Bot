# Jerrin Shirks

# native imports
import time
import math

# custom imports
from files.jerrinth import JerrinthBot
from files.wrappers import *
from files.config import *


class FindseedCog(commands.Cog):
    def __init__(self, bot):
        self.bot: JerrinthBot = bot
        self.eye_count = 12

    def prob_of_n_tens(self, n):
        numerator = math.comb(self.eye_count, n) * (9 ** (self.eye_count - n))
        denominator = 10 ** self.eye_count
        return numerator / denominator

    @wrapper_command(name='findseed', cooldown=FINDSEED_COOLDOWN)
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
        self.bot.getUser(ctx)["findseed"]["use_total"] += 1
        self.bot.getUser(ctx)["findseed"]["use_last"] = time.time()

        await ctx.send(message + f"<@{ctx.author.id}> → your seed is a **{eye_count}** eye.")

    @findseedCommand.error
    @wrapper_error(use_cooldown=True)
    async def findseedCommandError(self, ctx, error):
        pass


async def setup(bot):
    await bot.add_cog(FindseedCog(bot))
