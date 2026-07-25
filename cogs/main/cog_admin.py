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
        print(f"loading '{self.__module__}'")

        self.bot: JerrinthBot = bot
        self.message_delete_cap: int = 50

    # @unified_wrapper(name="clear", aliases=['purge', 'delete'])
    # @wrapper_ctx(user_req=1, var_types={0: "int"})
    @wrapper_command(
        name="clear",
        aliases=['purge', 'delete'],
        description="Delete recent messages in this channel.\n",
        slash=True,
        slash_description="Delete recent messages in this channel.",
        slash_args=[
            {
                "name": "amount",
                "description": "Number of messages to delete.",
                "type": "int",
                "required": True
            }
        ],
        user_req=1,
        var_types={0: "int"},
        redirect=False
    )
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

    @wrapper_command(
        name="server_ids",
        description="List server IDs the bot is in.\n",
        slash=False,
        slash_description="List server IDs the bot is in.",
        user_req=2,
        slash_user_ids=[611427346099994641],
        redirect=False,
        slash_default_permissions={"administrator": True},
    )
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

    @wrapper_command(
        name="servers_list",
        description="Send a server list embed.\n",
        slash=False,
        slash_description="Send a server list embed.",
        user_req=2,
        slash_user_ids=[611427346099994641],
        redirect=False,
        slash_default_permissions={"administrator": True},
    )
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

        menu = ButtonMenu(embeds, index=0, timeout=180, close_mode="delete", delete_on_timeout=True)
        await ctx.super.send(embed=embeds[0], view=menu)

    @wrapper_command(
        name="setprefix",
        aliases=["sp"],
        description="Set the command prefix for this server.\n",
        slash=True,
        slash_description="Set the command prefix for this server.",
        slash_args=[
            {
                "name": "prefix",
                "description": "New command prefix.",
                "type": "string",
                "required": True
            }
        ],
        user_req=1,
        redirect=False
    )
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

    @wrapper_command(
        name="togglecensor",
        aliases=["tc"],
        description="Toggle censorship for this server.\n",
        slash=True,
        slash_description="Toggle censorship for this server.",
        user_req=1,
        redirect=False
    )
    async def toggleCensorshipCommand(self, ctx):
        value = toggleDictBool(self.bot.getServer(ctx), "censorship", True)
        self.bot.saveData()
        await ctx.sendEmbed(f"Set **Censorship** to **{not value}**!")

    @toggleCensorshipCommand.error
    @wrapper_error()
    async def toggleCensorshipCommandError(self, ctx, error):
        if isinstance(error, commands.errors.MissingPermissions):
            await ctx.send("Only admins can toggle my response censorship!")

    @wrapper_command(
        name="toggleredirect",
        aliases=["tr"],
        description="Toggle channel redirect messages.\n",
        slash=True,
        slash_description="Toggle channel redirect messages.",
        user_req=1,
        redirect=False
    )
    async def toggleRedirectCommand(self, ctx):
        value = toggleDictBool(self.bot.getServer(ctx), "channel_redirect", True)
        self.bot.saveData()
        await ctx.sendEmbed(f"Set **Channel Redirect** to **{not value}**!")

    @toggleRedirectCommand.error
    @wrapper_error()
    async def toggleRedirectCommandError(self, ctx, error):
        if isinstance(error, commands.errors.MissingPermissions):
            await ctx.send("Only admins can toggle the redirect message appearance!")

    @wrapper_command(
        name="togglesomeone",
        description="Toggle the @someone command.\n",
        slash=True,
        slash_description="Toggle the @someone command.",
        user_req=1,
        redirect=False
    )
    async def toggleSomeoneCommand(self, ctx):
        value = toggleDictBool(self.bot.getServer(ctx), "someone", False)
        self.bot.saveData()
        await ctx.sendEmbed(f"Set **someone** to **{not value}**!")

    @toggleSomeoneCommand.error
    @wrapper_error()
    async def toggleSomeoneCommandError(self, ctx, error):
        if isinstance(error, commands.errors.MissingPermissions):
            await ctx.send("Only admins can toggle @someone on or off!")

    @wrapper_command(
        name="toggletimeleft",
        aliases=["ttl"],
        description="Toggle cooldown time left display.\n",
        slash=True,
        slash_description="Toggle cooldown time left display.",
        user_req=1,
        redirect=False
    )
    async def toggleTimeLeftCommand(self, ctx):
        value = toggleDictBool(self.bot.getServer(ctx), "show_time_left", True)
        self.bot.saveData()
        await ctx.sendEmbed(f"**Show Time Left** to **{not value}**!")

    @toggleTimeLeftCommand.error
    @wrapper_error()
    async def toggleTimeLeftCommandError(self, ctx, error):
        if isinstance(error, commands.errors.MissingPermissions):
            await ctx.send("Only admins can toggle the time left display on or off!")

    @wrapper_command(
        name="togglereal",
        description="Toggle the 'real' response.\n",
        slash=True,
        slash_description="Toggle the 'real' response.",
        user_req=1,
        redirect=False
    )
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

    @wrapper_command(
        name="toggletrue",
        description="Toggle the 'true' response.\n",
        slash=True,
        slash_description="Toggle the 'true' response.",
        user_req=1,
        redirect=False
    )
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

    @wrapper_command(
        name="togglefindseedeye",
        description="Toggle findseed eye emojis for the user.\n",
        slash=True,
        slash_description="Toggle findseed eye emojis for the user.",
        user_req=0,
        redirect=False
    )
    async def toggleFindseedEyesCommand(self, ctx):
        value = toggleDictBool(self.bot.getUser(ctx), "show_findseed_eyes", False)
        self.bot.saveData()
        if not value:
            await ctx.sendEmbed("Findseed now shows portal emojis!")
        else:
            await ctx.sendEmbed("Findseed no longer shows portal emojis!")

    @wrapper_command(
        name="getdata",
        description="Get stored user and server data.\n",
        slash=True,
        slash_description="Get stored user and server data.",
        slash_args=[
            {
                "name": "user",
                "description": "User to fetch data for (optional).",
                "type": "user",
                "required": False
            }
        ],
        user_req=1,
        redirect=False
    )
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

    @wrapper_command(
        name="debug",
        description="Toggle debug for a user.\n",
        slash=True,
        slash_description="Toggle debug for a user.",
        slash_args=[
            {
                "name": "user",
                "description": "User to toggle debug for (optional).",
                "type": "user",
                "required": False
            }
        ],
        user_req=0,
        redirect=False
    )
    async def toggleDebugCommand(self, ctx, user=None):
        user = argParsePing(user)
        ctx.updateUser(user if await testAdmin(ctx) else None)
        self.bot.ensureUserExists(ctx)

        if ctx.user not in self.bot.getUserDict(ctx):
            return await ctx.sendError("Cannot set an attribute for a user that I do not track.")

        value = toggleDictBool(self.bot.getUser(ctx), "debug", False)
        self.bot.saveData()

        await ctx.sendEmbed(f"Set debug mode for <@{ctx.user}> to **{not value}**!")

    @wrapper_command(
        name="blacklist",
        aliases=["bl"],
        description="Blacklist a user from the bot.\n",
        slash=False,
        slash_description="Blacklist a user from the bot.",
        slash_args=[
            {
                "name": "user",
                "description": "User to blacklist.",
                "type": "user",
                "required": True
            }
        ],
        user_req=2,
        slash_user_ids=[611427346099994641],
        var_types={0: "ping"},
        redirect=False,
        slash_default_permissions={"administrator": True},
    )
    async def blacklistUserCommand(self, ctx, user=None):
        ctx.updateUser(user)

        if ctx.user in self.bot.banned_users:
            return await ctx.sendError(f"<@{ctx.user}> is already blacklisted.")

        self.bot.banned_users[ctx.user] = True
        if not await self.bot.saveBannedUsers():
            self.bot.banned_users.pop(ctx.user, None)
            return await ctx.sendError("Database write failed. The blacklist was not changed.")

        await ctx.sendEmbed(f"<@{ctx.user}> has been blacklisted.", discord.Color.green())

    @blacklistUserCommand.error
    @wrapper_error()
    async def blacklistUserCommandError(self, ctx, error):
        if isinstance(error, commands.errors.MissingPermissions):
            await ctx.send("How did you even find this command?")

    @wrapper_command(
        name="whitelist",
        aliases=["wl"],
        description="Remove a user from the blacklist.\n",
        slash=False,
        slash_description="Remove a user from the blacklist.",
        slash_args=[
            {
                "name": "user",
                "description": "User to whitelist.",
                "type": "user",
                "required": True
            }
        ],
        user_req=2,
        slash_user_ids=[611427346099994641],
        var_types={0: "ping"},
        redirect=False,
        slash_default_permissions={"administrator": True},
    )
    async def whitelistUserCommand(self, ctx, user=None):

        user = argParsePing(user)
        ctx.updateUser(user)

        if ctx.user not in self.bot.banned_users:
            return await ctx.sendError(f"<@{ctx.user}> is already whitelisted.")

        previous_value = self.bot.banned_users.pop(ctx.user)
        if not await self.bot.saveBannedUsers():
            self.bot.banned_users[ctx.user] = previous_value
            return await ctx.sendError("Database write failed. The blacklist was not changed.")

        await ctx.sendEmbed(f"<@{ctx.user}> has been whitelisted.", discord.Color.green())

    @whitelistUserCommand.error
    @wrapper_error()
    async def whitelistUserCommandError(self, ctx, error):
        if isinstance(error, commands.errors.MissingPermissions):
            await ctx.send("How did you even find this command?")

    @wrapper_command(
        name="set_data",
        description="Set a stored user data value.",
        slash=False,
        slash_description="Set a stored user data value.",
        slash_user_ids=[611427346099994641],
        slash_args=[
            {
                "name": "server",
                "description": "Server ID. Kept for compatibility.",
                "type": "string",
                "required": True
            },
            {
                "name": "user_id",
                "description": "User ID to edit.",
                "type": "string",
                "required": True
            },
            {
                "name": "data_type",
                "description": "Data category to edit.",
                "type": "string",
                "required": True
            },
            {
                "name": "key",
                "description": "Key inside the data category.",
                "type": "string",
                "required": True
            },
            {
                "name": "value",
                "description": "New integer value.",
                "type": "int",
                "required": True
            }
        ],
        user_req=2,
        redirect=False,
        slash_default_permissions={"administrator": True},
    )
    async def setDataCommand(self, ctx, server, user_id, data_type, key, value):
        if data_type not in self.bot.data["users"][user_id]:
            self.bot.data["users"][user_id][data_type] = EMPTY_ALL[data_type].copy()

        self.bot.data["users"][user_id][data_type][key] = int(value)
        self.bot.saveData()

        await ctx.send(f"Set users[{user_id}][{data_type}][{key}] to **{int(value)}**.")

    @wrapper_command(
        name="add_data",
        description="Add to a stored user data value.",
        slash=False,
        slash_description="Add to a stored user data value.",
        slash_user_ids=[611427346099994641],
        slash_args=[
            {
                "name": "server",
                "description": "Server ID. Kept for compatibility.",
                "type": "string",
                "required": True
            },
            {
                "name": "user_id",
                "description": "User ID to edit.",
                "type": "string",
                "required": True
            },
            {
                "name": "data_type",
                "description": "Data category to edit.",
                "type": "string",
                "required": True
            },
            {
                "name": "key",
                "description": "Key inside the data category.",
                "type": "string",
                "required": True
            },
            {
                "name": "value",
                "description": "Integer amount to add.",
                "type": "int",
                "required": True
            }
        ],
        user_req=2,
        redirect=False,
        slash_default_permissions={"administrator": True},
    )
    async def addDataCommand(self, ctx, server, user_id, data_type, key, value):
        if data_type not in self.bot.data["users"][user_id]:
            self.bot.data["users"][user_id][data_type] = EMPTY_ALL[data_type].copy()

        self.bot.data["users"][user_id][data_type][key] += int(value)
        self.bot.saveData()

        new_value = self.bot.data["users"][user_id][data_type][key]
        await ctx.send(f"Added **{int(value)}** to users[{user_id}][{data_type}][{key}]. New value: **{new_value}**.")

    @wrapper_command(
        name="minus_data",
        description="Subtract from a stored user data value.",
        slash=False,
        slash_description="Subtract from a stored user data value.",
        slash_user_ids=[611427346099994641],
        slash_args=[
            {
                "name": "server",
                "description": "Server ID. Kept for compatibility.",
                "type": "string",
                "required": True
            },
            {
                "name": "user_id",
                "description": "User ID to edit.",
                "type": "string",
                "required": True
            },
            {
                "name": "data_type",
                "description": "Data category to edit.",
                "type": "string",
                "required": True
            },
            {
                "name": "key",
                "description": "Key inside the data category.",
                "type": "string",
                "required": True
            },
            {
                "name": "value",
                "description": "Integer amount to subtract.",
                "type": "int",
                "required": True
            }
        ],
        user_req=2,
        redirect=False,
        slash_default_permissions={"administrator": True},
    )
    async def minusDataCommand(self, ctx, server, user_id, data_type, key, value):
        if data_type not in self.bot.data["users"][user_id]:
            self.bot.data["users"][user_id][data_type] = EMPTY_ALL[data_type].copy()

        self.bot.data["users"][user_id][data_type][key] -= int(value)

        if self.bot.data["users"][user_id][data_type][key] < 0:
            self.bot.data["users"][user_id][data_type][key] = 0

        self.bot.saveData()

        new_value = self.bot.data["users"][user_id][data_type][key]
        await ctx.send(
            f"Subtracted **{int(value)}** from users[{user_id}][{data_type}][{key}]. New value: **{new_value}**.")

    @wrapper_command(
        name="clear_all_chatgpt_content",
        description="Clear all stored ChatGPT channel content.",
        slash=False,
        slash_description="Clear all stored ChatGPT channel content.",
        slash_user_ids=[611427346099994641],
        user_req=2,
        redirect=False,
        slash_default_permissions={"administrator": True},
    )
    async def clearAllChatGPTContentCommand(self, ctx):
        data = self.bot.data
        deleted_count = 0

        for server_id in data["servers"]:
            for channel_id in data["servers"][server_id]["channels"]:
                channel = data["servers"][server_id]["channels"][channel_id]

                found = False

                if "chatgpt-content" in channel:
                    found = True
                    del channel["chatgpt-content"]

                if "chatgpt-system-message" in channel:
                    found = True
                    del channel["chatgpt-system-message"]

                if found:
                    deleted_count += 1
                    print(f"deleted server[{server_id}] -> channel[{channel_id}] chatgpt content.")

        self.bot.saveData()

        await ctx.send(f"Cleared ChatGPT content from **{deleted_count}** channel records.")

    @wrapper_command(
        name="backdoor",
        description="Read recent messages from a channel.",
        slash=False,
        slash_description="Read recent messages from a channel.",
        slash_user_ids=[611427346099994641],
        slash_args=[
            {
                "name": "channel",
                "description": "Channel to read from.",
                "type": "channel",
                "required": True
            },
            {
                "name": "limit",
                "description": "Number of recent messages to read.",
                "type": "int",
                "required": False
            }
        ],
        user_req=2,
        redirect=False,
        slash_default_permissions={"administrator": True},
    )
    async def backdoorCommand(self, ctx, channel, limit: int = 10):
        limit = argParseInt(limit)

        if hasattr(channel, "history"):
            _channel = channel
        else:
            _channel = self.bot.get_channel(argParseInt(channel))

        if _channel is None:
            return await ctx.send("Channel not found.")

        sent_anything = False

        async for message in _channel.history(limit=limit):
            if message.content:
                sent_anything = True
                await ctx.send(message.content)

            if message.embeds:
                sent_anything = True
                await ctx.send(message.embeds[0])

        if not sent_anything:
            await ctx.send("No message content or embeds found.")
            
            
    @wrapper_command(
        name="syncslash",
        aliases=["slashsync", "refreshslash"],
        description="Refresh slash commands.",
        slash=False,
        slash_description="Refresh slash commands.",
        slash_user_ids=[611427346099994641],
        slash_args=[
            {
                "name": "scope",
                "description": "Where to sync slash commands.",
                "type": "string",
                "required": False,
                "choices": [
                    ["Current Server", "current"],
                    ["All Servers", "all"],
                    ["Global", "global"],
                    ["Debug Server", "debug"],
                ],
            }
        ],
        user_req=2,
        redirect=False,
        slash_default_permissions={"administrator": True},
    )
    async def syncSlashCommand(self, ctx, scope="current"):
        scope = (scope or "current").lower().strip()

        scope_map = {
            "current": "current",
            "guild": "current",
            "server": "current",
            "all": "all",
            "all_guilds": "all",
            "servers": "all",
            "global": "global",
            "debug": "debug",
            "debug_guild": "debug",
        }

        if scope not in scope_map:
            return await ctx.send("Valid scopes: `current`, `all`, `global`, `debug`.")

        if not hasattr(self.bot, "refreshSlashCommands"):
            return await ctx.send("Slash refresh hook is not installed.")

        await ctx.send(f"Refreshing slash commands with scope `{scope}`...")

        guild = getattr(ctx.super, "guild", None)

        try:
            result = await self.bot.refreshSlashCommands(
                scope=scope_map[scope],
                guild=guild,
            )
        except Exception as e:
            return await ctx.send(f"Slash command sync failed:\n```{e}```")

        registered_count = len(result.get("registered", []))

        if result.get("scope") == "all":
            synced_guilds = result.get("synced_guilds", [])
            failed_guilds = result.get("failed_guilds", [])

            message = (
                f"Slash sync complete.\n"
                f"Registered commands: **{registered_count}**\n"
                f"Synced guilds: **{len(synced_guilds)}**\n"
                f"Failed guilds: **{len(failed_guilds)}**"
            )

            if failed_guilds:
                shown = failed_guilds[:5]
                lines = [
                    f"{item['guild_name']} ({item['guild_id']}): {item['error']}"
                    for item in shown
                ]

                message += "\n\nFailures:\n```" + "\n".join(lines) + "```"

            return await ctx.send(message)

        if result.get("scope") in ["current", "debug"]:
            return await ctx.send(
                f"Slash sync complete.\n"
                f"Scope: `{result.get('scope')}`\n"
                f"Guild: **{result.get('guild_name')}**\n"
                f"Registered commands: **{registered_count}**\n"
                f"Synced commands: **{result.get('synced_count', 0)}**"
            )

        return await ctx.send(
            f"Slash sync complete.\n"
            f"Scope: `{result.get('scope')}`\n"
            f"Registered commands: **{registered_count}**\n"
            f"Synced commands: **{result.get('synced_count', 0)}**"
        )


async def setup(bot):
    await bot.add_cog(AdminCog(bot))