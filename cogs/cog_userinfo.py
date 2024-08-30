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
        self.bot: JerrinthBot = bot

    @wrapper_command(name="eyecount", aliases=["ec"], var_types={0: "ping"})
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
        while eyes[-1] == 0:
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

        eyes = data_user["findseed"]["eye_count"].copy()
        while eyes[-1] == 0:
            eyes.pop()
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

    @wrapper_command(name="profile", aliases=["userinfo"])
    async def profileCommand(self, ctx, user=None):
        ctx.updateUser(argParsePing(user))

        user = self.bot.get_user(ctx.userInt)

        if user is not None:
            if ctx.user == "856411268633329684":
                return await ctx.send("*I don't have a profile silly! ... Should I?*")
        else:
            return await ctx.send("This user has not interacted with me yet!")

        embed = newEmbed()
        embed.set_thumbnail(url=user.avatar)
        embed.set_author(name=user.name)
        embed.add_field(name="User", inline=False, value=f"<@{user.id}>")
        prefix = self.bot.gp(ctx)

        user = self.bot.getUser(ctx)

        if user is None:
            return await ctx.send("This user has not interacted with me yet!")

        table_uniques = []

        # findblock
        if "findblock" in user:
            if self.bot.getUser(ctx)["findblock"]["end_portal_count"] != 0:
                _emoji_portal = self.bot.getEmoji("end_portal")
                portal_count = self.bot.getUser(ctx)["findblock"]["end_portal_count"]
                table_uniques.append(["Total", f"{portal_count}x {_emoji_portal}"])

        # findseed section
        _emoji_eye = self.bot.getEmoji('mc_ender_eye')
        if "findseed" in user:
            eyes = user["findseed"]["eye_count"].copy()
            while eyes[-1] == 0:
                eyes.pop()
            table_uniques.append(["Total", f"{sum([eye * n for n, eye in enumerate(eyes)])}x {_emoji_eye}"])

        if table_uniques:
            embed.add_field(name="Uniques",
                            inline=False,
                            value=makeTable(
                                data=table_uniques,
                                bold_col=1,
                                sep={0: ": "}))

        table_stats = []

        if "findseed" in user:
            eyes = user["findseed"]["eye_count"].copy()
            while eyes[-1] == 0:
                eyes.pop()
            table_stats.append([f"Highest{_emoji_eye}", len(eyes) - 1])

        if table_stats:
            embed.add_field(name="Stats",
                            inline=False,
                            value=makeTable(
                                data=table_stats,
                                bold_col=1,
                                sep={0: ": "}))

        # command section
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

        data = []
        for key, title in keys:
            if key in user:
                data.append([key, title, user[key]["use_total"]])

        length = getLongest([user[i[0]]["use_total"] for i in data])

        message = [f"``{str(value).rjust(length)}`` - **{title}**" for key, title, value in data]

        embed.add_field(name="Uses",
                        inline=False,
                        value="\n".join(message))

        await ctx.send(embed)


async def setup(bot):
    await bot.add_cog(UserInfoCog(bot))
