# Jerrin Shirks

# native imports
from discord.ext import commands, tasks
import asyncio
import random

# custom imports
from jerrinth import JerrinthBot



class RandomTypingCog(commands.Cog):
    def __init__(self, bot):
        self.bot: JerrinthBot = bot
        # self.randomTyping.start()

    def cog_unload(self):
        self.randomTyping.cancel()

    """
    @tasks.loop(hours=1)
    async def randomTyping(self):
        # pause execution for 0-60 minutes.
        await asyncio.sleep(random.randint(0, 3600))

        # pick random channel here
        guild = random.choice(self.bot.guilds)
        channel = random.choice(guild.text_channels)

        async with channel.typing():
            # type for 5-10 minutes.
            await asyncio.sleep(random.randint(300, 600))
    """

async def setup(bot):
    await bot.add_cog(RandomTypingCog(bot))
