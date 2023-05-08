# Jerrin Shirks

# native imports

# custom imports
from files.jerrinth import JerrinthBot
from files.wrappers import *
from files.config import *



class DMsCog(commands.Cog):
    def __init__(self, bot):
        self.bot: JerrinthBot = bot







async def setup(bot):
    await bot.add_cog(DMsCog(bot))

