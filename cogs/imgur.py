# Jerrin Shirks

# native imports
from discord.ext import commands
import pprint
import time

# custom imports
from jerrinth import JerrinthBot
from wrappers import *
from support import *
from config import *


class ImgurCog(commands.Cog):
    def __init__(self, bot):
        self.bot: JerrinthBot = bot


    def ensureUserImgurExists(self, ctx):
        self.bot.ensureUserExists(ctx)
        if self.bot.getUser(ctx).get("imgur", None) is None:
            self.bot.getUser(ctx)["imgur"] = EMPTY_IMGUR.copy()


    @commands.command(name="findimg", aliases=["FINDIMG"])
    @discord.ext.commands.cooldown(*FINDIMG_COOLDOWN)
    @ctx_wrapper
    @channel_redirect
    async def findImageCommand(self, ctx):

        self.ensureUserImgurExists(ctx)

        data = self.bot.imgur.getRandomImage(ctx)
        await self.bot.imgur.loadRandomImages()
        if data is None:
            return await ctx.send(errorEmbed(description="Something went wrong! Please try again."))

        self.bot.getUser(ctx)["imgur"]["total_uses"] += 1
        self.bot.getUser(ctx)["imgur"]["last_use"] = time.time()
        self.bot.saveData()

        pprint.pprint(data)
        # input("waiting")


        # await ctx.send(data["url"])
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
    @ctx_wrapper
    async def findImageCommandError(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            if self.bot.getServer(ctx).get("show_time_left", True):
                await ctx.send(f"Try again in **{error.retry_after:.3f}**s.")
            else:
                await ctx.super.message.add_reaction(convertDecimalToClock(error.retry_after / FINDIMG_COOLDOWN[1]))
        else:
            await ctx.message.add_reaction("❌")





    @commands.command(name="imgur", aliases=[])
    # @discord.ext.commands.cooldown(1, 4, commands.BucketType.guild)
    @ctx_wrapper
    @channel_redirect
    async def imgurCommand(self, ctx, *args):

        self.ensureUserImgurExists(ctx)

        await self.bot.imgur.loadGallery(*args)

        data = self.bot.imgur.getGalleryImage(ctx, *args)

        pprint.pprint(data)

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
