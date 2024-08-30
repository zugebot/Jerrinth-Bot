# Jerrin Shirks

# native imports
import pprint
import time
import ssl
import certifi

# custom imports
from files.jerrinth import JerrinthBot
from files.buttonMenu import ButtonMenu
from files.wrappers import *
from files.support import *
from files.config import *
from funcs.imgur import Imgur


class ImgurCog(commands.Cog):
    def __init__(self, bot):
        self.bot: JerrinthBot = bot

    def ensureUserImgurExists(self, ctx):
        self.bot.ensureUserExists(ctx)
        if self.bot.getUser(ctx).get("imgur", None) is None:
            self.bot.getUser(ctx)["imgur"] = EMPTY_IMGUR.copy()

    @wrapper_command(name="findimg", cooldown=FINDIMG_COOLDOWN)
    async def findImageCommand(self, ctx):

        self.ensureUserImgurExists(ctx)

        if not self.bot.imgur.valid_id:
            return await ctx.sendError("My imgur key is invalid, this command will not work until one is added.")

        data = self.bot.imgur.getRandomImage(ctx)
        await self.bot.imgur.loadRandomImages()
        if data is None:
            return await ctx.sendError("Something went wrong! Please try again.")

        self.bot.getUser(ctx)["imgur"]["use_total"] += 1
        self.bot.getUser(ctx)["imgur"]["use_last"] = time.time()
        self.bot.saveData()

        message = await self.bot.imgur.createMessage(data)
        if isinstance(message, str):
            await ctx.send(message)

        elif isinstance(message, discord.embeds.Embed):
            await ctx.send(message)

        elif isinstance(message, list):
            menu = ButtonMenu(message, index=0, timeout=180)
            try:
                await menu.send(ctx)
            except discord.errors.Forbidden:
                await ctx.send("Something went wrong with the interaction.")

    @findImageCommand.error
    @wrapper_error(use_cooldown=True)
    async def findImageCommandError(self, ctx, error):
        pass

    @wrapper_command(name="imgur")
    async def imgurCommand(self, ctx, *args):

        self.ensureUserImgurExists(ctx)

        await self.bot.imgur.loadGallery(*args)

        data = self.bot.imgur.getGalleryImage(ctx, *args)

        # pprint.pprint(data)

        message = await self.bot.imgur.createMessage(data)

        if isinstance(message, str):
            await ctx.send(message)
        elif isinstance(message, discord.embeds.Embed):
            await ctx.send(message)
        elif isinstance(message, list):
            menu = ButtonMenu(message, index=0, timeout=180)
            try:
                await menu.send(ctx)
            except discord.errors.Forbidden:
                await ctx.send("Something went wrong with the interaction.")


async def setup(bot):
    await bot.add_cog(ImgurCog(bot))
