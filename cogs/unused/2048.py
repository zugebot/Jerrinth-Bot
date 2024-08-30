# Jerrin Shirks

# native imports
from discord.ext import commands, tasks

# custom imports
from files.jerrinth import JerrinthBot
from files.buttonMenu import ButtonMenu
from files.support import CtxObject
from files.wrappers import *
from files.discord_objects import *
from files.makeTable import makeTable


class Server2048RunsCog(commands.Cog):
    def __init__(self, bot):
        self.bot: JerrinthBot = bot
        self.EMOJIS = ["🤡", ":clown:"]
        self.SERVER_IDS = [490493858401222656, 1099062116549415012]
        self.EMPTY_2048 = {"warns": 0}
        self.LOG_CHANNEL = {
            1099062116549415012: 1190090160147279952,
            490493858401222656: 1190089938813849670
        }

        self.admins = {
            1099062116549415012: "**'dr.filean'** / **'iloveannifrfr'**",
            490493858401222656: "**'thecabillonaire'** / **'hobbelweg'** / **'iloveannifrfr'**"
        }

        for server in self.SERVER_IDS:
            self.bot.hooks_on_raw_reaction_add[server] = self.on_raw_reaction_add
            self.bot.hooks_on_message[server] = self.on_message

    @wrapper_command(name='warnings', cooldown=(1, 15, commands.BucketType.guild))
    async def warningsCommand(self, ctx: CtxObject):
        if ctx.serverInt not in self.SERVER_IDS:
            return

        size = 10
        dict_key = "2048"

        items = [i for i in self.bot.getUserDict(ctx).items() if dict_key in i[1]]
        if len(items) == 0:
            return await ctx.sendError("There have been no warnings in this server...")
        users = sorted(items, key=lambda x: x[1][dict_key]["warns"], reverse=True)

        table = []

        for n, user in enumerate(users):
            key, value = user
            # print(value[dict_key]["warns"])
            if value[dict_key]["warns"] == 0:
                break
            if value[dict_key]['warns'] >= 5:
                table.append([f"banned", f"<@{key}>"])
            else:
                table.append([f"{value[dict_key]['warns']} of 5", f"<@{key}>"])

        sects = [table[i:i + size] for i in range(0, len(table), size)]
        embeds = []
        for n, sect in enumerate(sects):
            text = makeTable(sect, code=[0], sep={0: " - "})
            embed = newEmbed(text)
            embeds.append(embed)

        if len(embeds) > 1:
            for n, embed in enumerate(embeds):
                embed.set_author(name=f"Warned Users [{n + 1}/{len(embeds)}]")
            menu = ButtonMenu(embeds, index=0, timeout=180)
            try:
                await menu.send(ctx)
            except discord.errors.Forbidden:
                await ctx.send("Something went wrong with the interaction.")

        else:
            embeds[0].set_author(name="Warned Users")
            await ctx.send(embeds[0])

    @wrapper_command(name='warn', user_req=1)
    async def _2048warnCommand(self, ctx: CtxObject, user=None):

        original_user = ctx.userInt

        if ctx.serverInt not in self.SERVER_IDS:
            return

        if user is None:
            await ctx.message.add_reaction("❌")
            return

        ctx.updateUser(argParsePing(user))

        user = self.bot.get_user(ctx.userInt)

        if user is None:
            await ctx.message.add_reaction("❌")
            return

        await self.addWarning(ctx, "", True)
        await ctx.message.add_reaction("✅")

    @_2048warnCommand.error
    @wrapper_error()
    async def _2048warnCommandError(self, ctx, error):
        if isinstance(error, commands.errors.MissingPermissions):
            await ctx.message.add_reaction("❌")

    @wrapper_command(name='setwarn', aliases=['setwarning'], user_req=1)
    async def _2048setWarnCommand(self, ctx: CtxObject, user=None, number: int | None = None):
        if ctx.serverInt not in self.SERVER_IDS:
            return

        original_user = ctx.userInt

        ctx.updateUser(argParsePing(user))
        user = self.bot.get_user(ctx.userInt)

        if user is None or number is None:
            await ctx.message.add_reaction("❌")
            return

        if number < 0:
            number = 0

        if number > 4:
            return await ctx.sendError("Cannot set warning level to max, for that would be an immediate ban. Ban them"
                                       " yourselves!")

        self.ensureUser2048Exists(ctx)
        before = self.bot.getUser(ctx)["2048"]["warns"]

        if number == 0:
            self.bot.getUser(ctx)["2048"]["warns"] = 0
            self.bot.saveData()
            await ctx.message.add_reaction("✅")

        else:
            await ctx.message.add_reaction("✅")
            if number > before:
                self.bot.getUser(ctx)["2048"]["warns"] = number - 1
                await self.addWarning(ctx, "", True)

        # send log message
        channel = self.bot.get_channel(self.LOG_CHANNEL[ctx.serverInt])
        content = f"<@{original_user}> set <@{ctx.userInt}>'s warnings to {number} of 5."
        if number == 4:
            content += "\nThis resulted in them being kicked."
        embed = newEmbed(content)
        await channel.send(embed=embed)

    @_2048setWarnCommand.error
    @wrapper_error()
    async def _2048setWarnCommandError(self, ctx, error):
        if isinstance(error, commands.errors.MissingPermissions):
            await ctx.message.add_reaction("❌")

    def ensureUser2048Exists(self, ctx: CtxObject):
        if self.bot.getUser(ctx) is None:
            self.bot.data["users"][ctx.user] = EMPTY_USER.copy()

        if isinstance(ctx.message, RawReactionActionEvent):
            self.bot.getUser(ctx)["name"] = self.bot.get_user(ctx.userInt).name
        elif ctx.userInt == ctx.message.author.id:
            self.bot.getUser(ctx)["name"] = ctx.message.author.name

        self.bot.saveData()

        if self.bot.getUser(ctx).get("2048", None) is None:
            self.bot.getUser(ctx)["2048"] = self.EMPTY_2048.copy()

    async def sendDMWarning(self, ctx: CtxObject, warning: str):
        user = self.bot.get_user(ctx.userInt)
        embed = newEmbed(description=warning)
        server = self.bot.get_guild(ctx.serverInt)
        embed.set_author(name=server.name, icon_url=server.icon.url)
        await user.send(embed=embed)

    async def getMember(self, guild_id, user_id):
        guild = self.bot.get_guild(guild_id)
        if guild is None:
            return None
        return guild.get_member(user_id)

    async def addWarning(self, ctx: CtxObject, emoji=None, admin_did_it=False, reaction=False, context=""):
        """
        self.ensureUser2048Exists(ctx)
        if self.bot.getUser(ctx)["2048"]["warns"] < 0:
            self.bot.getUser(ctx)["2048"]["warns"] = 0
        self.bot.getUser(ctx)["2048"]["warns"] += 1
        self.bot.saveData()
        warnings = self.bot.getUser(ctx)["2048"]["warns"]


        if warnings in [1, 2, 3]:
            message = "An admin has issued you a **warning**." if admin_did_it else "You have received a **warning** " \
                                                                                    "for using " \
                                                                                    "the {} emoji.".format(emoji)
            message += f"\n\nCurrent warning count: **{warnings}**."
            message += f"\n\nConsequences if continued:"
            message += f"\n- **Kicked** from the server at **{4}** warnings."
            message += f"\n- **Banned** from the server at **{5}** warnings."
            await self.sendDMWarning(ctx, message)

        elif warnings == 4:
            message = "An admin has issued you a **warning**,\nresulting in you being **kicked**." if admin_did_it \
                else "You have been **kicked** for using the {} emoji.".format(emoji)
            message += f"\n\nCurrent warning count: **{warnings}**."
            message += "\n\nConsequences if continued:"
            message += f"\n- **Banned** from the server at **{5}** warnings."
            await self.sendDMWarning(ctx, message)
            member = await self.getMember(ctx.serverInt, ctx.userInt)
            try:
                await member.kick(reason="Consistently breaking the rules")
            except Exception as e:
                if isinstance(e, discord.errors.Forbidden):
                    await self.bot.get_channel(ctx.channelInt).send(
                        embed=errorEmbed("I do not have valid permissions to kick..."))
                    return

        elif warnings >= 5:
            message = "You have been **banned** by an admin." if admin_did_it else "You have been **banned** for " \
                                                                                   "using the {} emoji.".format(emoji)
            message += f"\n\nCurrent warning count: **{warnings}**."
            message += f"\n\nFor appeals, contact {self.admins[ctx.serverInt]} on Discord."
            await self.sendDMWarning(ctx, message)

            member = await self.getMember(ctx.serverInt, ctx.userInt)
            try:
                await member.ban(reason="Consistently breaking the rules")
            except Exception as e:
                if isinstance(e, discord.errors.Forbidden):
                    await self.bot.get_channel(ctx.channelInt).send(
                        embed=errorEmbed("I do not have valid permissions to ban..."))
                    return
        """
        warnings = 0

        # send log message
        channel = self.bot.get_channel(self.LOG_CHANNEL[ctx.serverInt])
        content = f"<@{ctx.userInt}> received warning #{warnings}."
        if warnings == 4:
            content += "\nThis resulted in them being kicked."
        if warnings == 5:
            content += "\nThis resulted in them being banned."

        if reaction:
            content += f"\n\nreacted with {emoji}."
        if context != "":
            content += f"\n\n**Message:**\n{context}"

        embed = newEmbed(content)
        await channel.send(embed=embed)

    async def on_message(self, ctx: CtxObject) -> None:
        text = ctx.message.content.lower().replace(" ", "")

        for emoji in self.EMOJIS:
            if emoji in text:
                await self.addWarning(ctx, emoji, context=ctx.message.content)
                await ctx.message.delete()

    async def on_raw_reaction_add(self, payload):
        if str(payload.emoji) in self.EMOJIS:
            channel = self.bot.get_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
            user = self.bot.get_user(payload.user_id)
            try:
                await message.remove_reaction(str(payload.emoji), user)
            except:
                ""
            ctx: CtxObject = CtxObject(payload)
            await self.addWarning(ctx, str(payload.emoji), reaction=True)


async def setup(bot):
    await bot.add_cog(Server2048RunsCog(bot))
