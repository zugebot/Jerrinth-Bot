# Jerrin Shirks

# native imports
from discord.ext import commands, tasks

# custom imports
from files.jerrinth import JerrinthBot


class AlexisSucksCog(commands.Cog):
    def __init__(self, bot):
        self.bot: JerrinthBot = bot
        # self.randomTyping.start()

    def cog_unload(self):
        self.randomTyping.cancel()

    @tasks.loop(seconds=3)
    async def randomTyping(self):
        channel_id = 751086615274979419
        channel = self.bot.get_channel(channel_id)

        kbps = channel.bitrate // 1000
        if kbps > 48:
            return

        await channel.edit(bitrate=512000)

        user_id = 611427346099994641 # 362793094342770688
        user = self.bot.get_user(user_id)

        await user.send("KYS retard I immediately set it back to 64Kbps.")


async def setup(bot):
    await bot.add_cog(AlexisSucksCog(bot))
