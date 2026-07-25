# Jerrin Shirks

# native imports

# custom imports
from files.jerrinth import JerrinthBot
from files.makeTable import makeTable
from files.wrappers import *
from files.support import *
from files.discord_objects import *


class UserInfoCog(commands.Cog):
    def __init__(self, bot):
        print(f"loading '{self.__module__}'")

        self.bot: JerrinthBot = bot

    def getMobDefs(self):
        return getattr(self.bot, "mob_defs", {})

    def getItemDefs(self):
        return getattr(self.bot, "mob_item_defs", {})

    def getUserItemCount(self, user, item_key):
        return user.get("items", {}).get(item_key, 0)

    def getUserItemsTable(self, user):
        table_items = []
        item_defs = self.getItemDefs()
        items = user.get("items", {})

        for item_key, item_def in item_defs.items():
            amount = self.getUserItemCount(user, item_key)

            if amount <= 0:
                continue

            table_items.append([
                item_def["emoji"],
                amount,
                item_def["plural"].title()
            ])

        for item_key, amount in items.items():
            if item_key in item_defs:
                continue
            if amount <= 0:
                continue

            table_items.append([
                "",
                amount,
                item_key.replace("_", " ").title()
            ])

        return table_items

    def getMobStatsTable(self, user):
        table_stats = []

        for mob_key, mob_def in self.getMobDefs().items():
            if mob_key not in user:
                continue

            use_total = user[mob_key].get("use_total", 0)

            if use_total <= 0:
                continue

            table_stats.append([
                mob_def["emoji"],
                use_total,
                mob_def.get("stat_name", f"{mob_def['plural'].title()} Killed")
            ])

        return table_stats

    def formatStatsField(self, table_stats):
        if not table_stats:
            return None

        return makeTable(
            data=table_stats,
            bold_col=[],
            code=[1],
            sep={
                0: "  ",
                1: "  ",
            },
            direction="right"
        )
    
    def getPortalStatsTable(self, user):
        table_stats = []

        _emoji_eye = self.bot.getEmoji('mc_ender_eye')

        if "findseed" in user:
            eyes = user["findseed"]["eye_count"].copy()
            while eyes and eyes[-1] == 0:
                eyes.pop()

            if eyes:
                table_stats.append([
                    _emoji_eye,
                    len(eyes) - 1,
                    "Highest Portal Eyes"
                ])
                table_stats.append([
                    _emoji_eye,
                    sum([eye * n for n, eye in enumerate(eyes)]),
                    "Total Eyes In Portal"
                ])

        return table_stats

    def getCommandUsageRows(self, user, prefix):
        keys = [
            ("ai", f"{prefix}ai"),
            ("imgur", f"{prefix}findimg"),
            ("findseed", f"{prefix}findseed"),
            ("findblock", f"{prefix}findblock"),
            ("playrandom", f"{prefix}playrandom"),
            ("@someone", f"@someone"),
            ("whisper", f"{prefix}whisper"),
            ("play", f"{prefix}play"),
        ]

        for mob_key, mob_def in self.getMobDefs().items():
            keys.append((mob_key, f"{prefix}{mob_def['command']}"))

        data = []

        for key, title in keys:
            if key not in user:
                continue

            use_total = user[key].get("use_total", 0)

            if use_total <= 0:
                continue

            data.append([key, title, use_total])

        return data

    @wrapper_command(
        name="eyecount",
        aliases=["ec"],
        var_types={0: "ping"},
        description="Show end portal eye counts for a user.\n",
        slash=True,
        slash_description="Show end portal eye counts for a user.",
        slash_args=[
            {
                "name": "user",
                "description": "User to look up.",
                "type": "string",
                "required": False
            }
        ]
    )
    async def showEyeCountCommand(self, ctx, user=None):
        ctx.updateUser(user)

        user = self.bot.get_user(ctx.userInt)
        if user is None:
            if ctx.user == "856411268633329684":
                return await ctx.send("*I can't roll for eyes silly! ... Should I?*")
            else:
                return await ctx.send("This user has not interacted with me yet!")

        prefix = self.bot.gp(ctx)
        data_user = self.bot.getUser(ctx)

        if data_user is None:
            return await ctx.send("This user has not interacted with me yet!")

        if "findseed" not in data_user:
            return await ctx.send(f"This user has not used {prefix}findseed before!")

        embed = newEmbed()
        embed.set_thumbnail(url=user.avatar)
        embed.set_author(name=user.name)
        embed.add_field(name="User", inline=False, value=f"<@{user.id}>")

        eyes = data_user["findseed"]["eye_count"].copy()
        while eyes and eyes[-1] == 0:
            eyes.pop()

        table1 = []
        for n, eye in enumerate(eyes):
            item1 = n
            item2 = f"{self.bot.getEmoji('mc_ender_eye')}"
            item3 = f"**{eye}**x"
            table1.append([item1, item2, item3])
        table1.reverse()

        table1 = makeTable(data=table1,
                           bold_col=[],
                           code=[0],
                           sep={
                               0: "",
                               1: "- ",
                           },
                           direction="left")

        eye_sum = sum([eye * n for n, eye in enumerate(eyes)])

        table2 = [
            [data_user['findseed']['use_total'], "Total Uses"],
            [eye_sum, "Total Eyes"]
        ]

        table2 = makeTable(data=table2,
                           bold_col=[],
                           code=[0],
                           sep={
                               0: " - ",
                           },
                           direction="left")

        embed.add_field(name="Eye Count", inline=True, value=table1)
        embed.add_field(name="Other Stats", inline=True, value=table2)
        await ctx.send(embed)

    async def showMobCount(self, ctx, mob_key, user=None):
        ctx.updateUser(user)

        user_obj = self.bot.get_user(ctx.userInt)
        if user_obj is None:
            return await ctx.send("This user has not interacted with me yet!")

        data_user = self.bot.getUser(ctx)

        if data_user is None:
            return await ctx.send("This user has not interacted with me yet!")

        mob_defs = self.getMobDefs()
        item_defs = self.getItemDefs()

        if mob_key not in mob_defs:
            return await ctx.send(f"Mob metadata missing for `{mob_key}`.")

        mob_def = mob_defs[mob_key]

        if mob_key not in data_user:
            return await ctx.send(f"This user has not used {self.bot.gp(ctx)}{mob_def['command']} before!")

        embed = newEmbed()
        embed.set_thumbnail(url=user_obj.avatar)
        embed.set_author(name=user_obj.name)
        embed.add_field(name="User", inline=False, value=f"<@{user_obj.id}>")

        drop_table = []

        for item_key in mob_def.get("drops", []):
            if item_key not in item_defs:
                continue

            amount = self.getUserItemCount(data_user, item_key)
            item_def = item_defs[item_key]

            drop_table.append([
                item_def["emoji"],
                amount
            ])

        if drop_table:
            embed.add_field(
                name="Drops",
                inline=True,
                value=makeTable(
                    data=drop_table,
                    bold_col=[1],
                    sep={0: " - "},
                    direction="left"
                )
            )

        stats_table = makeTable(data=[
            [data_user[mob_key].get("use_total", 0), f"{mob_def['plural'].title()} Killed"],
        ],
            bold_col=[],
            code=[0],
            sep={0: " - "},
            direction="left")

        embed.add_field(name="Other Stats", inline=True, value=stats_table)
        await ctx.send(embed)

    @wrapper_command(
        name="blazecount",
        aliases=["bc"],
        var_types={0: "ping"},
        description="Show blaze kill stats for a user.\n",
        slash=True,
        slash_description="Show blaze kill stats for a user.",
        slash_args=[
            {
                "name": "user",
                "description": "User to look up.",
                "type": "string",
                "required": False
            }
        ]
    )
    async def showBlazeCountCommand(self, ctx, user=None):
        await self.showMobCount(ctx, "blaze", user)

    @wrapper_command(
        name="wscount",
        aliases=["wsc"],
        var_types={0: "ping"},
        description="Show wither skeleton kill stats for a user.\n",
        slash=True,
        slash_description="Show wither skeleton kill stats for a user.",
        slash_args=[
            {
                "name": "user",
                "description": "User to look up.",
                "type": "string",
                "required": False
            }
        ]
    )
    async def showWitherSkeletonCountCommand(self, ctx, user=None):
        await self.showMobCount(ctx, "ws", user)

    @wrapper_command(
        name="usage",
        aliases=["uses", "commandcount", "uc"],
        var_types={0: "ping"},
        description="Show command usage stats for a user.\n",
        slash=True,
        slash_description="Show command usage stats for a user.",
        slash_args=[
            {
                "name": "user",
                "description": "User to look up.",
                "type": "string",
                "required": False
            }
        ]
    )
    async def usageCommand(self, ctx, user=None):
        ctx.updateUser(argParsePing(user))

        user_obj = self.bot.get_user(ctx.userInt)

        if user_obj is None:
            return await ctx.send("This user has not interacted with me yet!")

        data_user = self.bot.getUser(ctx)

        if data_user is None:
            return await ctx.send("This user has not interacted with me yet!")

        prefix = self.bot.gp(ctx)
        data = self.getCommandUsageRows(data_user, prefix)

        if not data:
            return await ctx.send("This user has no command usage tracked yet.")

        length = getLongest([value for key, title, value in data])
        message = [f"``{str(value).rjust(length)}`` - **{title}**" for key, title, value in data]

        embed = newEmbed()
        embed.set_thumbnail(url=user_obj.avatar)
        embed.set_author(name=user_obj.name)
        embed.add_field(name="User", inline=False, value=f"<@{user_obj.id}>")
        embed.add_field(name="Command Usage", inline=False, value="\n".join(message))

        await ctx.send(embed)

    @wrapper_command(
        name="profile",
        aliases=["userinfo", "pr"],
        description="Show a user's profile.\n",
        slash=True,
        slash_description="Show a user's profile.",
        slash_args=[
            {
                "name": "user",
                "description": "User to look up.",
                "type": "string",
                "required": False
            }
        ]
    )
    async def profileCommand(self, ctx, user=None):
        ctx.updateUser(argParsePing(user))

        user_obj = self.bot.get_user(ctx.userInt)

        if user_obj is not None:
            if ctx.user == "856411268633329684":
                return await ctx.send("*I don't have a profile silly! ... Should I?*")
        else:
            return await ctx.send("This user has not interacted with me yet!")

        embed = newEmbed()
        embed.set_thumbnail(url=user_obj.avatar)
        embed.set_author(name=user_obj.name)
        embed.add_field(name="User", inline=False, value=f"<@{user_obj.id}>")
        prefix = self.bot.gp(ctx)

        user = self.bot.getUser(ctx)

        if user is None:
            return await ctx.send("This user has not interacted with me yet!")
        
        table_items = []

        if "findblock" in user:
            if self.bot.getUser(ctx)["findblock"]["end_portal_count"] != 0:
                _emoji_portal = self.bot.getEmoji("end_portal")
                portal_count = self.bot.getUser(ctx)["findblock"]["end_portal_count"]
                table_items.append(["End Portals", f"{portal_count}x {_emoji_portal}"])

        table_items.extend(self.getUserItemsTable(user))

        if table_items:
            embed.add_field(name="Items",
                            inline=False,
                            value=makeTable(
                                data=table_items,
                                bold_col=[],
                                code=[1],
                                sep={
                                    0: " ",
                                    1: " ",
                                },
                                direction="right"))

        portal_stats = self.getPortalStatsTable(user)
        portal_stats_text = self.formatStatsField(portal_stats)

        if portal_stats_text:
            embed.add_field(name="Portal Stats",
                            inline=False,
                            value=portal_stats_text)

        mob_stats = self.getMobStatsTable(user)
        mob_stats_text = self.formatStatsField(mob_stats)

        if mob_stats_text:
            embed.add_field(name="Mob Stats",
                            inline=False,
                            value=mob_stats_text)

        embed.set_footer(text=f"Use {prefix}usage to view command counts.")

        await ctx.send(embed)


async def setup(bot):
    await bot.add_cog(UserInfoCog(bot))