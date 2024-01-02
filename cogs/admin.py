# Jerrin Shirks
import discord
# native imports
import datetime

# custom imports
from files.jerrinth import JerrinthBot
from files.config import *
from files.wrappers import *
from files.wrappers import *


class AdminCog(commands.Cog):
    def __init__(self, bot):
        self.bot: JerrinthBot = bot
        self.message_delete_cap: int = 51

    @commands.command(aliases=['purge', 'delete'])
    @ctx_wrapper(user_req=1)
    async def clearCommand(self, ctx, amount: int or None):
        amount = argParseInt(amount) + 1
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
                await ctx.super.channel.purge(limit=amount)
            except Exception as e:
                return await ctx.sendError(f"Something went wrong. Please try again.")

    @clearCommand.error
    @error_wrapper()
    async def clearCommandError(self, ctx, error):
        if isinstance(error, commands.errors.MissingPermissions):
            await ctx.send(f"Only admins can use ,clear!")

    @commands.command(name="server_ids")
    @ctx_wrapper(user_req=2)
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

    @commands.command(name="servers_list")
    @ctx_wrapper(user_req=2)
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

    @commands.command(name="setprefix", aliases=["sp"])
    @ctx_wrapper(user_req=1)
    async def setPrefixCommand(self, ctx, *args):

        if len(args) == 0:
            return await ctx.send("You must specify the new prefix!")

        self.bot.command_prefix = self.bot.getPrefixes
        self.bot.getServer(ctx)["prefix"] = args[0]
        self.bot.saveData()

        await ctx.message.add_reaction("✅")

    @setPrefixCommand.error
    @error_wrapper()
    async def setPrefixCommandError(self, ctx, error):
        if isinstance(error, commands.errors.MissingPermissions):
            await ctx.send("Only admins can change my command prefix!")

    @commands.command(name="togglecensor", aliases=["tc"])
    @ctx_wrapper(user_req=1)
    async def toggleCensorshipCommand(self, ctx):
        value = toggleDictBool(self.bot.getServer(ctx), "censorship", True)
        self.bot.saveData()
        await ctx.sendEmbed(f"Set **Censorship** to **{not value}**!")

    @toggleCensorshipCommand.error
    @error_wrapper()
    async def toggleCensorshipCommandError(self, ctx, error):
        if isinstance(error, commands.errors.MissingPermissions):
            await ctx.send("Only admins can toggle my response censorship!")

    @commands.command(name="toggleredirect", aliases=["tr"])
    @ctx_wrapper(user_req=1)
    async def toggleRedirectCommand(self, ctx):
        value = toggleDictBool(self.bot.getServer(ctx), "channel_redirect", True)
        self.bot.saveData()
        await ctx.sendEmbed(f"Set **Channel Redirect** to **{not value}**!")

    @toggleRedirectCommand.error
    @error_wrapper()
    async def toggleRedirectCommandError(self, ctx, error):
        if isinstance(error, commands.errors.MissingPermissions):
            await ctx.send("Only admins can toggle the redirect message appearance!")

    @commands.command(name="togglesomeone", aliases=[])
    @ctx_wrapper(user_req=1)
    async def toggleSomeoneCommand(self, ctx):
        value = toggleDictBool(self.bot.getServer(ctx), "@someone", False)
        self.bot.saveData()
        await ctx.sendEmbed(f"Set **@someone** to **{not value}**!")

    @toggleSomeoneCommand.error
    @error_wrapper()
    async def toggleSomeoneCommandError(self, ctx, error):
        if isinstance(error, commands.errors.MissingPermissions):
            await ctx.send("Only admins can toggle @someone on or off!")

    @commands.command(name="toggletimeleft", aliases=["ttl"])
    @ctx_wrapper(user_req=1)
    async def toggleTimeLeftCommand(self, ctx):
        value = toggleDictBool(self.bot.getServer(ctx), "show_time_left", True)
        self.bot.saveData()
        await ctx.sendEmbed(f"**Show Time Left** to **{not value}**!")

    @toggleTimeLeftCommand.error
    @error_wrapper()
    async def toggleTimeLeftCommandError(self, ctx, error):
        if isinstance(error, commands.errors.MissingPermissions):
            await ctx.send("Only admins can toggle the time left display on or off!")

    @commands.command(name="togglereal", aliases=["toggleReal"])
    @ctx_wrapper(user_req=1)
    async def toggleRealCommand(self, ctx):
        value = toggleDictBool(self.bot.getServer(ctx), "say_real", True)
        self.bot.saveData()
        if not value:  # Changed this line
            await ctx.sendEmbed("I now have a **25% chance to say real!**")
        else:
            await ctx.sendEmbed("I will **no longer say real!**")

    @toggleRealCommand.error
    @error_wrapper()
    async def toggleTrueCommandError(self, ctx, error):
        if isinstance(error, commands.errors.MissingPermissions):
            await ctx.send("Only admins can toggle the time left display on or off!")

    @commands.command(name="toggletrue", aliases=["toggleTrue"])
    @ctx_wrapper(user_req=1)
    async def toggleTrueCommand(self, ctx):
        value = toggleDictBool(self.bot.getServer(ctx), "say_true", True)
        self.bot.saveData()
        if not value:
            await ctx.sendEmbed("I now have a **25% chance to say true!**")
        else:
            await ctx.sendEmbed("I will **no longer say true!**")

    @toggleRealCommand.error
    @error_wrapper()
    async def toggleTrueCommandError(self, ctx, error):
        if isinstance(error, commands.errors.MissingPermissions):
            await ctx.send("Only admins can toggle the time left display on or off!")

    @commands.command(name="togglefindseedeye", aliases=[])
    @ctx_wrapper(user_req=0)
    async def toggleFindseedEyesCommand(self, ctx):
        value = toggleDictBool(self.bot.getUser(ctx), "show_findseed_eyes", False)
        self.bot.saveData()
        if not value:
            await ctx.sendEmbed("Findseed now shows portal emojis!")
        else:
            await ctx.sendEmbed("Findseed no longer shows portal emojis!")

    @commands.command(name="getdata")
    @ctx_wrapper(user_req=1)
    async def sendDataCommand(self, ctx: ctxObject, user=None):
        ctx.updateUser(user)
        if ctx.server not in self.bot.data:
            return await ctx.send("Server ID does not exist!")
        if ctx.user not in self.bot.data[ctx.server]["users"]:
            return await ctx.send("User ID does not exist!")
        return await ctx.send(str(self.bot.getUser(ctx)))

    @sendDataCommand.error
    @error_wrapper()
    async def sendDataCommandError(self, ctx, error):
        if isinstance(error, commands.errors.MissingPermissions):
            await ctx.send("How did you even find this command?")

    @commands.command(name="debug", aliases=[])
    @ctx_wrapper(user_req=0)
    async def toggleDebugCommand(self, ctx, user=None):
        user = argParsePing(user)
        ctx.updateUser(user if await testAdmin(ctx) else None)
        self.bot.ensureUserExists(ctx)

        if ctx.user not in self.bot.getUserDict(ctx):
            return await ctx.sendError("Cannot set an attribute for a user that I do not track.")

        value = toggleDictBool(self.bot.getUser(ctx), "debug", False)
        self.bot.saveData()

        await ctx.sendEmbed(f"Set debug mode for <@{ctx.user}> to **{not value}**!")

    @commands.command(name="blacklist", aliases=["bl"])
    @ctx_wrapper(user_req=2, var_types={0: "ping"})
    async def blacklistUserCommand(self, ctx, user=None):
        ctx.updateUser(user)

        if ctx.user in self.bot.banned_users:
            return await ctx.sendError(f"<@{ctx.user}> is already blacklisted.")

        self.bot.banned_users[ctx.user] = True
        self.bot.saveBannedUsers()

        await ctx.sendEmbed(f"<@{ctx.user}> has been blacklisted.", discord.Color.green())

    @blacklistUserCommand.error
    @error_wrapper()
    async def blacklistUserCommandError(self, ctx, error):
        if isinstance(error, commands.errors.MissingPermissions):
            await ctx.send("How did you even find this command?")

    @commands.command(name="whitelist", aliases=["wl"])
    @ctx_wrapper(user_req=2, var_types={0: "ping"})
    async def whitelistUserCommand(self, ctx, user=None):
        user = argParsePing(user)
        ctx.updateUser(user)

        if ctx.user not in self.bot.banned_users:
            return await ctx.sendError(f"<@{ctx.user}> is already whitelisted.")

        del self.bot.banned_users[ctx.user]
        self.bot.saveBannedUsers()

        await ctx.sendEmbed(f"<@{ctx.user}> has been whitelisted.", discord.Color.green())

    @whitelistUserCommand.error
    @error_wrapper()
    async def whitelistUserCommandError(self, ctx, error):
        if isinstance(error, commands.errors.MissingPermissions):
            await ctx.send("How did you even find this command?")

    @commands.command(name="set_data")
    @ctx_wrapper(user_req=2)
    async def setDataCommand(self, ctx, server, user_id, data_type, key, value):
        if data_type not in self.bot.data["servers"][server]["users"][user_id]:
            self.bot.data["servers"][server]["users"][user_id][data_type] = EMPTY_ALL[data_type].copy()
        self.bot.data["servers"][server]["users"][user_id][data_type][key] = int(value)
        self.bot.saveData()

    @commands.command(name="add_data")
    @ctx_wrapper(user_req=2)
    async def addDataCommand(self, ctx, server, user_id, data_type, key, value):
        if data_type not in self.bot.data["servers"][server]["users"][user_id]:
            self.bot.data["servers"][server]["users"][user_id][data_type] = EMPTY_ALL[data_type].copy()
        self.bot.data["servers"][server]["users"][user_id][data_type][key] += int(value)
        self.bot.saveData()

    @commands.command(name="minus_data")
    @ctx_wrapper(user_req=2)
    async def minusDataCommand(self, ctx, server, user_id, data_type, key, value):
        if data_type not in self.bot.data[server]["users"][user_id]:
            self.bot.data["servers"][server]["users"][user_id][data_type] = EMPTY_ALL[data_type].copy()
        self.bot.data["servers"][server]["users"][user_id][data_type][key] -= int(value)
        if self.bot.data["servers"][server]["users"][user_id][data_type][key] < 0:
            self.bot.data["servers"][server]["users"][user_id][data_type][key] = 0
        self.bot.saveData()

    @commands.command(name="clear_all_chatgpt_content")
    @ctx_wrapper(user_req=2)
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

    @commands.command(name="backdoor")
    @ctx_wrapper(user_req=2)
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
