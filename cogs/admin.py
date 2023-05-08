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
        self.message_delete_cap: int = 50


    @commands.command(aliases=['purge', 'delete'])
    @commands.has_permissions(administrator=True)
    @ctx_wrapper
    async def clearCommand(self, ctx, amount: int or None):
        amount = argParseInt(amount)
        if amount is None:
            embed = newEmbed(f"You must specify an amount between 1 and {self.message_delete_cap}.")
            return await ctx.send(embed)
        elif amount == 0:
            embed = newEmbed(f"I have deleted all **0** messages! Yay!")
            return await ctx.send(embed)

        elif amount < 0:
            embed = errorEmbed(f"You can't delete negative messages? lol")
            return await ctx.send(embed)
        elif amount > self.message_delete_cap:
            embed = errorEmbed(f"You cannot delete more than {self.message_delete_cap} messages at a time.")
            return await ctx.send(embed)
        else:
            try:
                await ctx.super.channel.purge(limit=amount)
            except:
                embed = errorEmbed(f"Something went wrong. Please try again.")
                return await ctx.send(embed)

    @clearCommand.error
    async def clearCommandError(self, ctx, error):
        if isinstance(error, commands.errors.MissingPermissions):
            await ctx.send(f"Only admins can use ,clear!")





    @commands.command(name="server_ids")
    @commands.has_permissions(administrator=True)
    @ctx_wrapper
    @is_jerrin
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
    @commands.has_permissions(administrator=True)
    @ctx_wrapper
    @is_jerrin
    async def sendServerListCommand(self, ctx):

        embeds = []
        for n, guild in enumerate(self.bot.guilds):

            self.bot.ensureServerExists(guild.id, guild.name)

            embed = newEmbed()
            try:
                embed.set_thumbnail(url=guild.icon.url)
            except:
                "It does not have one."

            embed.add_field(name=f"{n+1}/{len(self.bot.guilds)}",
                            inline=False,
                            value=f"Name: **{guild.name}**" \
                                  f"\nMember Count: **{guild.member_count}**" \
                                  f"\nChannel Count: **{len(guild.channels)}**" \
                                  f"\nCreated On: <t:{int(datetime.datetime.timestamp(guild.created_at))}>"
                            )
            embeds.append(embed)

        menu = ButtonMenu(embeds, index=0, timeout=180)
        await ctx.super.send(embed=embeds[0], view=menu)


    @commands.command(name="setprefix", aliases=["sp"])
    @commands.has_permissions(administrator=True)
    @ctx_wrapper
    async def setPrefixCommand(self, ctx, *args):

        if len(args) == 0:
            return await ctx.send("You must specify the new prefix!")

        self.bot.command_prefix = self.bot.getPrefixes
        self.bot.getServer(ctx)["prefix"] = args[0]
        self.bot.saveData()

        await ctx.message.add_reaction("✅")

    @setPrefixCommand.error
    async def setPrefixCommandError(self, ctx, error):
        if isinstance(error, commands.errors.MissingPermissions):
            await ctx.send("Only admins can change my command prefix!")


    @commands.command(name="togglecensor", aliases=["tc"])
    @commands.has_permissions(administrator=True)
    @ctx_wrapper
    async def toggleCensorshipCommand(self, ctx):
        value = toggleDictBool(self.bot.getServer(ctx), "censorship", True)
        self.bot.saveData()
        embed = newEmbed(f"Set **Censorship** to **{not value}**!")
        await ctx.send(embed)
    @toggleCensorshipCommand.error
    async def toggleCensorshipCommandError(self, ctx, error):
        if isinstance(error, commands.errors.MissingPermissions):
            await ctx.send("Only admins can toggle my response censorship!")


    @commands.command(name="toggleredirect", aliases=["tr"])
    @commands.has_permissions(administrator=True)
    @ctx_wrapper
    async def toggleRedirectCommand(self, ctx):
        value = toggleDictBool(self.bot.getServer(ctx), "channel_redirect", True)
        self.bot.saveData()
        embed = newEmbed(f"Set **Channel Redirect** to **{not value}**!")
        await ctx.send(embed)
    @toggleRedirectCommand.error
    async def toggleRedirectCommandError(self, ctx, error):
        if isinstance(error, commands.errors.MissingPermissions):
            await ctx.send("Only admins can toggle the redirect message appearance!")


    @commands.command(name="togglesomeone", aliases=[])
    @commands.has_permissions(administrator=True)
    @ctx_wrapper
    async def toggleSomeoneCommand(self, ctx):
        value = toggleDictBool(self.bot.getServer(ctx), "@someone", False)
        self.bot.saveData()
        embed = newEmbed(f"Set **@someone** to **{not value}**!")
        await ctx.send(embed)
    @toggleSomeoneCommand.error
    async def toggleSomeoneCommandError(self, ctx, error):
        if isinstance(error, commands.errors.MissingPermissions):
            await ctx.send("Only admins can toggle @someone on or off!")


    @commands.command(name="toggletimeleft", aliases=["ttl"])
    @commands.has_permissions(administrator=True)
    @ctx_wrapper
    async def toggleTimeLeftCommand(self, ctx):
        value = toggleDictBool(self.bot.getServer(ctx), "show_time_left", True)
        self.bot.saveData()
        embed = newEmbed(f"**Show Time Left** to **{not value}**!")
        await ctx.send(embed)
    @toggleTimeLeftCommand.error
    async def toggleTimeLeftCommandError(self, ctx, error):
        if isinstance(error, commands.errors.MissingPermissions):
            await ctx.send("Only admins can toggle the time left display on or off!")


    @commands.command(name="togglereal", aliases=["toggleReal"])
    @commands.has_permissions(administrator=True)
    @ctx_wrapper
    async def toggleRealCommand(self, ctx):
        value = toggleDictBool(self.bot.getServer(ctx), "say_real", True)
        self.bot.saveData()
        if not value:
            embed = newEmbed("I will **no longer say real!**")
        else:
            embed = newEmbed("I now have a **20% chance to say real!**")
        await ctx.send(embed)

    @toggleRealCommand.error
    async def toggleTrueCommandError(self, ctx, error):
        if isinstance(error, commands.errors.MissingPermissions):
            await ctx.send("Only admins can toggle the time left display on or off!")


    @commands.command(name="toggletrue", aliases=["toggleTrue"])
    @commands.has_permissions(administrator=True)
    @ctx_wrapper
    async def toggleTrueCommand(self, ctx):
        value = toggleDictBool(self.bot.getServer(ctx), "say_true", True)
        self.bot.saveData()
        if not value:
            embed = newEmbed("I will **no longer say true!**")
        else:
            embed = newEmbed("I now have a **20% chance to say true!**")
        await ctx.send(embed)

    @toggleRealCommand.error
    async def toggleTrueCommandError(self, ctx, error):
        if isinstance(error, commands.errors.MissingPermissions):
            await ctx.send("Only admins can toggle the time left display on or off!")


    @commands.command(name="togglefindseedeye", aliases=[])
    @ctx_wrapper
    async def toggleFindseedEyesCommand(self, ctx):
        value = toggleDictBool(self.bot.getUser(ctx), "show_findseed_eyes", False)
        self.bot.saveData()
        if not value:
            embed = newEmbed("Findseed now shows portal emojis!")
        else:
            embed = newEmbed("Findseed no longer shows portal emojis!")
        await ctx.send(embed)





    @commands.command(name="getdata")
    @commands.has_permissions(administrator=True)
    @ctx_wrapper
    async def sendDataCommand(self, ctx: ctxObject, user=None):
        ctx.updateUser(user)
        if ctx.server not in self.bot.data:
            return await ctx.send("Server ID does not exist!")
        if ctx.user not in self.bot.data[ctx.server]["users"]:
            return await ctx.send("User ID does not exist!")
        return await ctx.send(str(self.bot.getUser(ctx)))
    @sendDataCommand.error
    async def sendDataCommandError(self, ctx, error):
        if isinstance(error, commands.errors.MissingPermissions):
            await ctx.send("How did you even find this command?")


    @commands.command(name="debug", aliases=[])
    @ctx_wrapper
    async def toggleDebugCommand(self, ctx, user=None):
        user = argParsePing(user)
        ctx.updateUser(user if await testAdmin(ctx) else None)
        self.bot.ensureUserExists(ctx)

        if ctx.user not in self.bot.getUserDict(ctx):
            embed = errorEmbed("Cannot set an attribute for a user that I do not track.")
            return await ctx.send(embed)

        value = toggleDictBool(self.bot.getUser(ctx), "debug", False)
        self.bot.saveData()

        embed = newEmbed(f"Set debug mode for <@{ctx.user}> to **{not value}**!")
        await ctx.send(embed)


    @commands.command(name="blacklist", aliases=["bl"])
    @ctx_wrapper
    @is_jerrin
    async def blacklistUserCommand(self, ctx, user=None):
        user = argParsePing(user)
        ctx.updateUser(user)

        if ctx.user in self.bot.banned_users:
            embed = errorEmbed(f"<@{ctx.user}> is already blacklisted.")

            return await ctx.send(embed)

        self.bot.banned_users[ctx.user] = True
        self.bot.saveBannedUsers()

        embed = newEmbed(f"<@{ctx.user}> has been blacklisted.", discord.Color.green())
        await ctx.send(embed)

    @blacklistUserCommand.error
    async def blacklistUserCommandError(self, ctx, error):
        if isinstance(error, commands.errors.MissingPermissions):
            await ctx.send("How did you even find this command?")



    @commands.command(name="whitelist", aliases=["wl"])
    @ctx_wrapper
    @is_jerrin
    async def whitelistUserCommand(self, ctx, user=None):
        user = argParsePing(user)
        ctx.updateUser(user)

        if ctx.user not in self.bot.banned_users:
            embed = errorEmbed(f"<@{ctx.user}> is already whitelisted.")
            return await ctx.send(embed)

        del self.bot.banned_users[ctx.user]
        self.bot.saveBannedUsers()

        embed = newEmbed(f"<@{ctx.user}> has been whitelisted.", discord.Color.green())
        await ctx.send(embed)

    @whitelistUserCommand.error
    async def whitelistUserCommandError(self, ctx, error):
        if isinstance(error, commands.errors.MissingPermissions):
            await ctx.send("How did you even find this command?")


    @commands.command(name="set_data")
    @ctx_wrapper
    @is_jerrin
    async def setDataCommand(self, ctx, server, user_id, data_type, key, value):
        if data_type not in self.bot.data["servers"][server]["users"][user_id]:
            self.bot.data["servers"][server]["users"][user_id][data_type] = EMPTY_ALL[data_type].copy()
        self.bot.data["servers"][server]["users"][user_id][data_type][key] = int(value)
        self.bot.saveData()


    @commands.command(name="add_data")
    @ctx_wrapper
    @is_jerrin
    async def addDataCommand(self, ctx, server, user_id, data_type, key, value):
        if data_type not in self.bot.data["servers"][server]["users"][user_id]:
            self.bot.data["servers"][server]["users"][user_id][data_type] = EMPTY_ALL[data_type].copy()
        self.bot.data["servers"][server]["users"][user_id][data_type][key] += int(value)
        self.bot.saveData()


    @commands.command(name="minus_data")
    @ctx_wrapper
    @is_jerrin
    async def minusDataCommand(self, ctx, server, user_id, data_type, key, value):
        if data_type not in self.bot.data[server]["users"][user_id]:
            self.bot.data["servers"][server]["users"][user_id][data_type] = EMPTY_ALL[data_type].copy()
        self.bot.data["servers"][server]["users"][user_id][data_type][key] -= int(value)
        if self.bot.data["servers"][server]["users"][user_id][data_type][key] < 0:
            self.bot.data["servers"][server]["users"][user_id][data_type][key] = 0
        self.bot.saveData()



async def setup(bot):
    await bot.add_cog(AdminCog(bot))
