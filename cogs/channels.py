# Jerrin Shirks

# native imports

# custom imports
from files.wrappers import *
from files.support import *
from files.jerrinth import JerrinthBot


class ChannelsCog(commands.Cog):
    def __init__(self, bot):
        self.bot: JerrinthBot = bot

    @commands.command(name="channelengine", aliases=["ce"])
    @has_administrator()
    @ctx_wrapper
    async def setChannelEngineCommand(self, ctx, engineArg: str = ""):

        if engineArg == "":
            return await ctx.sendError(f"Please specify a number between **1** and **{len(self.bot.ai.engines)}** !")

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
            await ctx.sendError(f"**'{engineArg}'** is not a valid engine number!", reference=True)

    @setChannelEngineCommand.error
    @ctx_wrapper
    async def setChannelEngineCommandError(self, ctx, error):
        if isinstance(error, commands.errors.MissingPermissions):
            await ctx.send("Only admins can set a channel engine!")

    @commands.command(name="addchannel", aliases=["ac"])
    @has_administrator()
    @ctx_wrapper
    async def addChannelCommand(self, ctx, channel=None):
        channel = argParsePing(channel, excluded=["all"])
        ctx.updateChannel(channel)

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
    @has_administrator()
    @ctx_wrapper
    async def deleteChannelCommand(self, ctx, channel=None):
        channel = argParsePing(channel, excluded=["all"])
        ctx.updateChannel(channel)

        if channel == "all":
            self.bot.getServer(ctx)["usable_everywhere"] = False
            self.bot.data["servers"][ctx.server]["channels"] = {}
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
        server = self.bot.getServer(ctx)
        prefix = self.bot.getPrefix(ctx)
        channels = self.bot.getChannelDict(ctx)
        embed = newEmbed(title="Channel List")

        if server.get("usable_everywhere", False):
            return await ctx.send(newEmbed(f"**No need to list channels, for I am usable in all!**\n"
                                           f"If you want to turn this off, use {prefix}omni"))

        field_title = "Channels" if channels else "Channels Usable (Empty!)"

        # if it is being called from another function
        if redirect:
            embed.description = "You cannot use that command in this channel.\n" \
                                "Please navigate to one of the below channels."
        else:
            embed.description = "These are places you can use my commands!"

        text = ""
        if channels:
            text = ", ".join([f"<#{channel}>" for channel in channels])
        text = f"{text}Have an admin add a channel using **{prefix}addchannel**\n"
        text = f"{text}Admins can also add all channels using **{prefix}omni**"
        embed.add_field(name=field_title, inline=False, value=text)

        await ctx.send(embed, reference=True)

    @commands.command(name="omni", aliases=["OMNI", "Omni"])
    @ctx_wrapper
    async def addAllChannels(self, ctx):
        server = self.bot.getServer(ctx)
        prefix = self.bot.getPrefix(ctx)
        toggleDictBool(server, "usable_everywhere", False)
        if server.get("usable_everywhere"):
            description = "***You can now use me in all text channels!***"
        else:
            description = f"**I can now only use channels that were added using the {prefix}addchannel.**"

        await ctx.sendEmbed(description)


async def setup(bot):
    await bot.add_cog(ChannelsCog(bot))
