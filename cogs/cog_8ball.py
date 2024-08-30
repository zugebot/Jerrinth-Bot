# Jerrin Shirks

# native imports

# custom imports
from files.jerrinth import JerrinthBot
from files.wrappers import *
from files.config import *
from files.support import *


class EightBallCog(commands.Cog):
    RESPONSES_8BALL = ["It is certain.",
                       "It is decidedly so.",
                       "Without a doubt.",
                       "Yes definitely.",
                       "You may rely on it.",
                       "As I see it, yes.",
                       "Most likely.",
                       "Outlook good.",
                       "Yes.",
                       "Signs point to yes.",
                       "Reply hazy, try again.",
                       "Ask again later.",
                       "Better not tell you now.",
                       "Cannot predict now.",
                       "Concentrate and ask again.",
                       "Don't count on it.",
                       "My reply is no.",
                       "My sources say no.",
                       "Outlook not so good.",
                       "Very doubtful."]
    BAD_RESPONSES_8BALL = ["Do you participate in the contest of the most useless questions?",
                           "Please ask a real question please.",
                           "I do not understand."]

    def __init__(self, bot):
        self.bot: JerrinthBot = bot

    @wrapper_command(name='8ball', description='Let the 8 Ball Predict!\n')
    async def _8ballCommand(self, ctx, *args):
        """allows the user to get randomized responses from their questions from the magical 8ball."""
        if args:
            response = "🎱 " + random.choice(EightBallCog.RESPONSES_8BALL)
        else:
            response = "🎱 " + random.choice(EightBallCog.BAD_RESPONSES_8BALL)
        return await ctx.send(response)


async def setup(bot):
    await bot.add_cog(EightBallCog(bot))
