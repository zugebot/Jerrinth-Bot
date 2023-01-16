# Jerrin Shirks

# native imports
from discord.ext import commands

# custom imports
from wrappers import *
from support import *



class ChannelsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.command(name="channelengine", aliases=["ce"])
    @commands.has_permissions(administrator=True)
    @ctx_wrapper
    async def setChannelEngineCommand(self, ctx, engineArg: str = ""):

        if engineArg == "":
            embed = errorEmbed(f"Please specify a number between **1** and **{len(self.bot.ai.engines)}** !")
            return await ctx.send(embed)

        if engineArg == "del":
            self.bot.ensureChannelExists(ctx)
            self.bot.getChannel(ctx).pop("forced_engine", None)
            self.bot.saveData()

            embed = newEmbed(f"<#{ctx.channel}> no longer uses an engine override!")
            return await ctx.send(embed, reference=True)

        engineNum = argParseInt(engineArg, offset=-1)
        engines = self.bot.ai.engines
        length = len(engines)
        if isinstance(engineNum, int):
            if 0 <= engineNum < length:
                self.bot.getChannel(ctx)["forced_engine"] = engineNum
                self.bot.saveData()
                embed = newEmbed(f"This channel now always uses **{engines[engineNum]}** !")
            else:
                embed = errorEmbed(f"Please specify a number between **1** and **{length}** !")
            await ctx.send(embed, reference=True)

        else:
            embed = errorEmbed(f"**'{engineArg}'** is not a valid engine number!")
            await ctx.send(embed, reference=True)
    @setChannelEngineCommand.error
    @ctx_wrapper
    async def setChannelEngineCommandError(self, ctx, error):
        if isinstance(error, commands.errors.MissingPermissions):
            await ctx.send("Only admins can set a channel engine!")


    @commands.command(name="addchannel", aliases=["ac"])
    @commands.has_permissions(administrator=True)
    @ctx_wrapper
    async def addChannelCommand(self, ctx, channel=None):
        channel = argParsePing(channel, excluded=["all"])
        ctx.updateChannel(channel)

        if channel == "all":
            guild = self.bot.get_guild(ctx.serverInt)

            for channel_iter in guild.text_channels:
                ctx.updateChannel(channel_iter.id)
                self.bot.ensureChannelExists(ctx)

            self.bot.saveData()
            embed = newEmbed(f"The bot is now limitless!\n*You can use me in all channels.*")
            return await ctx.send(embed, reference=True)

        status = self.bot.ensureChannelExists(ctx)
        if status:
            desc = f"I now watch over <#{ctx.channel}>!"
        else:
            desc = f"I already watch over <#{ctx.channel}>."
        await ctx.send(desc)
    @addChannelCommand.error
    @ctx_wrapper
    async def addChannelCommandError(self, ctx, error):
        if isinstance(error, commands.errors.MissingPermissions):
            await ctx.send("Only admins can add channels to my scope!")


    @commands.command(name="delchannel", aliases=["dc"])
    @commands.has_permissions(administrator=True)
    @ctx_wrapper
    async def deleteChannelCommand(self, ctx, channel=None):
        channel = argParsePing(channel, excluded=["all"])
        ctx.updateChannel(channel)

        if channel == "all":
            self.bot.data[ctx.server]["channels"] = {}
            self.bot.saveData()
            embed = newEmbed(f"All channels have been disabled from my usage.")
            return await ctx.send(embed, reference=True)

        status = self.bot.deleteChannel(ctx)
        if status:
            desc = f"I have removed <#{ctx.channel}>!"
        else:
            desc = f"I am already ignoring <#{ctx.channel}>!"
        await ctx.send(desc)

    @deleteChannelCommand.error
    @ctx_wrapper
    async def deleteChannelCommandError(self, ctx, error):
        if isinstance(error, commands.errors.MissingPermissions):
            await ctx.send("Only admins can remove channels to my scope!")


    @commands.command(name="channels", aliases=["c"])
    @ctx_wrapper
    async def channelsCommand(self, ctx, redirect=False):
        self.bot.ensureServerExists(ctx)

        prefix = self.bot.data[ctx.server]["prefix"]
        channels = self.bot.getChannelDict(ctx)
        embed = newEmbed(title="Channel List")

        # if it is being called from another function
        if redirect:
            embed.description = "You cannot use that command in this channel.\nPlease navigate to one of the below channels."
        else:
            embed.description = "These are places you can use my commands!"
        if channels:
            items = ", ".join([f"<#{channel}>" for channel in channels])
            embed.add_field(name="Channels", inline=False, value=items)
        else:
            value = f"Have an admin add a channel using **{prefix}addchannel**"
            embed.add_field(name="Channels Usable (Empty!)", inline=False, value=value)

        await ctx.send(embed, reference=True)


async def setup(bot):
    await bot.add_cog(ChannelsCog(bot))
