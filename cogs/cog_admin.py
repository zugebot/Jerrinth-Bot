# Jerrin Shirks
import discord
# native imports
import datetime

# custom imports
from files.jerrinth import JerrinthBot
from files.config import *
from files.buttonMenu import ButtonMenu
from files.discord_objects import testAdmin, newEmbed
from files.wrappers import *


class AdminCog(commands.Cog):
    def __init__(self, bot):
        self.bot: JerrinthBot = bot
        self.message_delete_cap: int = 50

    # @unified_wrapper(name="clear", aliases=['purge', 'delete'])
    # @wrapper_ctx(user_req=1, var_types={0: "int"})
    @wrapper_command(name="clear", aliases=['purge', 'delete'], user_req=1, var_types={0: "int"}, redirect=False)
    async def clearCommand(self, ctx, amount: int = None):
        if amount is None:
            return await ctx.sendEmbed(f"You must specify an amount between 1 and {self.message_delete_cap}.")
        elif amount == 0:
            return await ctx.sendEmbed(f"I have deleted all **0** messages! Yay!")

        elif amount < 0:
            return await ctx.sendError(f"You can't delete negative messages? lol")
        elif amount > self.message_delete_cap:
            return await ctx.sendError(f"You cannot delete more than {self.message_delete_cap} messages at a time.")
        else:
            try:
                await ctx.super.channel.purge(limit=amount + 1)
            except Exception as e:
                return await ctx.sendError(f"Something went wrong. Please try again.\n{e}")

    @clearCommand.error
    @wrapper_error()
    async def clearCommandError(self, ctx, error):
        if isinstance(error, commands.errors.MissingPermissions):
            await ctx.send(f"Only admins can use ,clear!")

    @wrapper_command(name="server_ids", user_req=2, redirect=False)
    async def listServerIdsCommand(self, ctx):
        ids = [guild.id for guild in self.bot.guilds]

        for server_id in ids:
            guild = self.bot.get_guild(server_id)
            if guild is None:
                continue

            if str(server_id) in self.bot.data["servers"]:
                self.bot.data["servers"][str(server_id)]["name"] = guild.name
                print(f"{server_id} found! {guild.name}")
            else:
                print(f"{server_id} not in data? {guild.name}")

        self.bot.saveData()

        message = "\n".join([str(i) for i in ids])
        await ctx.send(message)

    @wrapper_command(name="servers_list", user_req=2, redirect=False)
    async def sendServerListCommand(self, ctx):

        embeds = []
        for n, guild in enumerate(self.bot.guilds):

            self.bot.ensureServerExists(guild.id, guild.name)

            embed = newEmbed()
            try:
                embed.set_thumbnail(url=guild.icon.url)
            except:
                "It does not have one."

            embed.add_field(name=f"{n + 1}/{len(self.bot.guilds)}",
                            inline=False,
                            value=f"Name: **{guild.name}**"
                                  f"\nMember Count: **{guild.member_count}**"
                                  f"\nChannel Count: **{len(guild.channels)}**"
                                  f"\nCreated On: <t:{int(datetime.datetime.timestamp(guild.created_at))}>"
                            )
            embeds.append(embed)

        menu = ButtonMenu(embeds, index=0, timeout=180)
        await ctx.super.send(embed=embeds[0], view=menu)

    @wrapper_command(name="setprefix", aliases=["sp"], user_req=1, redirect=False)
    async def setPrefixCommand(self, ctx, *args):

        if len(args) == 0:
            return await ctx.send("You must specify the new prefix!")

        self.bot.command_prefix = self.bot.getPrefixes
        self.bot.getServer(ctx)["prefix"] = args[0]
        self.bot.saveData()

        await ctx.message.add_reaction("✅")

    @setPrefixCommand.error
    @wrapper_error()
    async def setPrefixCommandError(self, ctx, error):
        if isinstance(error, commands.errors.MissingPermissions):
            await ctx.send("Only admins can change my command prefix!")

    @wrapper_command(name="togglecensor", aliases=["tc"], user_req=1, redirect=False)
    async def toggleCensorshipCommand(self, ctx):
        value = toggleDictBool(self.bot.getServer(ctx), "censorship", True)
        self.bot.saveData()
        await ctx.sendEmbed(f"Set **Censorship** to **{not value}**!")

    @toggleCensorshipCommand.error
    @wrapper_error()
    async def toggleCensorshipCommandError(self, ctx, error):
        if isinstance(error, commands.errors.MissingPermissions):
            await ctx.send("Only admins can toggle my response censorship!")

    @wrapper_command(name="toggleredirect", aliases=["tr"], user_req=1, redirect=False)
    async def toggleRedirectCommand(self, ctx):
        value = toggleDictBool(self.bot.getServer(ctx), "channel_redirect", True)
        self.bot.saveData()
        await ctx.sendEmbed(f"Set **Channel Redirect** to **{not value}**!")

    @toggleRedirectCommand.error
    @wrapper_error()
    async def toggleRedirectCommandError(self, ctx, error):
        if isinstance(error, commands.errors.MissingPermissions):
            await ctx.send("Only admins can toggle the redirect message appearance!")

    @wrapper_command(name="togglesomeone", user_req=1, redirect=False)
    async def toggleSomeoneCommand(self, ctx):
        value = toggleDictBool(self.bot.getServer(ctx), "someone", False)
        self.bot.saveData()
        await ctx.sendEmbed(f"Set **someone** to **{not value}**!")

    @toggleSomeoneCommand.error
    @wrapper_error()
    async def toggleSomeoneCommandError(self, ctx, error):
        if isinstance(error, commands.errors.MissingPermissions):
            await ctx.send("Only admins can toggle @someone on or off!")

    @wrapper_command(name="toggletimeleft", aliases=["ttl"], user_req=1, redirect=False)
    async def toggleTimeLeftCommand(self, ctx):
        value = toggleDictBool(self.bot.getServer(ctx), "show_time_left", True)
        self.bot.saveData()
        await ctx.sendEmbed(f"**Show Time Left** to **{not value}**!")

    @toggleTimeLeftCommand.error
    @wrapper_error()
    async def toggleTimeLeftCommandError(self, ctx, error):
        if isinstance(error, commands.errors.MissingPermissions):
            await ctx.send("Only admins can toggle the time left display on or off!")

    @wrapper_command(name="togglereal", user_req=1, redirect=False)
    async def toggleRealCommand(self, ctx):
        value = toggleDictBool(self.bot.getServer(ctx), "say_real", True)
        self.bot.saveData()
        if not value:  # Changed this line
            await ctx.sendEmbed("I now have a **25% chance to say real!**")
        else:
            await ctx.sendEmbed("I will **no longer say real!**")

    @toggleRealCommand.error
    @wrapper_error()
    async def toggleTrueCommandError(self, ctx, error):
        if isinstance(error, commands.errors.MissingPermissions):
            await ctx.send("Only admins can toggle the time left display on or off!")

    @wrapper_command(name="toggletrue", user_req=1, redirect=False)
    async def toggleTrueCommand(self, ctx):
        value = toggleDictBool(self.bot.getServer(ctx), "say_true", True)
        self.bot.saveData()
        if not value:
            await ctx.sendEmbed("I now have a **25% chance to say true!**")
        else:
            await ctx.sendEmbed("I will **no longer say true!**")

    @toggleRealCommand.error
    @wrapper_error()
    async def toggleTrueCommandError(self, ctx, error):
        if isinstance(error, commands.errors.MissingPermissions):
            await ctx.send("Only admins can toggle the time left display on or off!")

    @wrapper_command(name="togglefindseedeye", user_req=0, redirect=False)
    async def toggleFindseedEyesCommand(self, ctx):
        value = toggleDictBool(self.bot.getUser(ctx), "show_findseed_eyes", False)
        self.bot.saveData()
        if not value:
            await ctx.sendEmbed("Findseed now shows portal emojis!")
        else:
            await ctx.sendEmbed("Findseed no longer shows portal emojis!")

    @wrapper_command(name="getdata", user_req=1, redirect=False)
    async def sendDataCommand(self, ctx: CtxObject, user=None):
        ctx.updateUser(user)
        if ctx.server not in self.bot.data:
            return await ctx.send("Server ID does not exist!")
        if ctx.user not in self.bot.data["users"]:
            return await ctx.send("User ID does not exist!")
        return await ctx.send(str(self.bot.getUser(ctx)))

    @sendDataCommand.error
    @wrapper_error()
    async def sendDataCommandError(self, ctx, error):
        if isinstance(error, commands.errors.MissingPermissions):
            await ctx.send("How did you even find this command?")

    @wrapper_command(name="debug", user_req=0, redirect=False)
    async def toggleDebugCommand(self, ctx, user=None):
        user = argParsePing(user)
        ctx.updateUser(user if await testAdmin(ctx) else None)
        self.bot.ensureUserExists(ctx)

        if ctx.user not in self.bot.getUserDict(ctx):
            return await ctx.sendError("Cannot set an attribute for a user that I do not track.")

        value = toggleDictBool(self.bot.getUser(ctx), "debug", False)
        self.bot.saveData()

        await ctx.sendEmbed(f"Set debug mode for <@{ctx.user}> to **{not value}**!")

    @wrapper_command(name="blacklist", aliases=["bl"], user_req=2, var_types={0: "ping"}, redirect=False)
    async def blacklistUserCommand(self, ctx, user=None):
        ctx.updateUser(user)

        if ctx.user in self.bot.banned_users:
            return await ctx.sendError(f"<@{ctx.user}> is already blacklisted.")

        self.bot.banned_users[ctx.user] = True
        self.bot.saveBannedUsers()

        await ctx.sendEmbed(f"<@{ctx.user}> has been blacklisted.", discord.Color.green())

    @blacklistUserCommand.error
    @wrapper_error()
    async def blacklistUserCommandError(self, ctx, error):
        if isinstance(error, commands.errors.MissingPermissions):
            await ctx.send("How did you even find this command?")

    @wrapper_command(name="whitelist", aliases=["wl"], user_req=2, var_types={0: "ping"}, redirect=False)
    async def whitelistUserCommand(self, ctx, user=None):

        user = argParsePing(user)
        ctx.updateUser(user)

        if ctx.user not in self.bot.banned_users:
            return await ctx.sendError(f"<@{ctx.user}> is already whitelisted.")

        del self.bot.banned_users[ctx.user]
        self.bot.saveBannedUsers()

        await ctx.sendEmbed(f"<@{ctx.user}> has been whitelisted.", discord.Color.green())

    @whitelistUserCommand.error
    @wrapper_error()
    async def whitelistUserCommandError(self, ctx, error):
        if isinstance(error, commands.errors.MissingPermissions):
            await ctx.send("How did you even find this command?")

    @wrapper_command(name="set_data", user_req=2, redirect=False)
    async def setDataCommand(self, ctx, server, user_id, data_type, key, value):
        if data_type not in self.bot.data["users"][user_id]:
            self.bot.data["users"][user_id][data_type] = EMPTY_ALL[data_type].copy()
        self.bot.data["users"][user_id][data_type][key] = int(value)
        self.bot.saveData()

    @wrapper_command(name="add_data", user_req=2, redirect=False)
    async def addDataCommand(self, ctx, server, user_id, data_type, key, value):
        if data_type not in self.bot.data["users"][user_id]:
            self.bot.data["users"][user_id][data_type] = EMPTY_ALL[data_type].copy()
        self.bot.data["users"][user_id][data_type][key] += int(value)
        self.bot.saveData()

    @wrapper_command(name="minus_data", user_req=2, redirect=False)
    async def minusDataCommand(self, ctx, server, user_id, data_type, key, value):
        if data_type not in self.bot.data["users"][user_id]:
            self.bot.data["users"][user_id][data_type] = EMPTY_ALL[data_type].copy()
        self.bot.data["users"][user_id][data_type][key] -= int(value)
        if self.bot.data["users"][user_id][data_type][key] < 0:
            self.bot.data["users"][user_id][data_type][key] = 0
        self.bot.saveData()

    @wrapper_command(name="clear_all_chatgpt_content", user_req=2, redirect=False)
    async def clearAllChatGPTContentCommand(self, ctx):
        data = self.bot.data
        for server_id in (SERVERS := data["servers"]):
            for channel_id in (CHANNELS := SERVERS[server_id]["channels"]):
                channel = CHANNELS[channel_id]

                found = False

                if "chatgpt-content" in channel:
                    found = True
                    del channel["chatgpt-content"]

                if "chatgpt-system-message" in channel:
                    found = True
                    del channel["chatgpt-system-message"]

                if found:
                    print(f"deleted server[{server_id}] -> channel[{channel_id}] chatgpt content.")
        self.bot.saveData()

    @wrapper_command(name="backdoor", user_req=2, redirect=False)
    async def backdoorCommand(self, ctx, _channel: int, limit: int = 10):
        _channel = argParseInt(_channel)
        limit = argParseInt(limit)
        _channel = self.bot.get_channel(_channel)
        async for message in _channel.history(limit=limit):
            if message.content:
                await ctx.send(message.content)
            if message.embeds:
                await ctx.send(message.embeds[0])


async def setup(bot):
    await bot.add_cog(AdminCog(bot))
