# Jerrin Shirks

# native imports

# custom imports
from files.jerrinth import JerrinthBot
from files.wrappers import *
from files.support import *


class UserInfoCog(commands.Cog):
    def __init__(self, bot):
        self.bot: JerrinthBot = bot

    @commands.command(name="eyecount", aliases=["ec"])
    @ctx_wrapper(var_types={0: "ping"}, redirect=True)
    async def showEyeCountCommand(self, ctx, user=None):
        ctx.updateUser(user)

        user = self.bot.get_user(ctx.userInt)
        if user is None:
            if ctx.user == "856411268633329684":
                return await ctx.send("*I can't roll for eyes silly! ... Should I?*")
            else:
                return await ctx.send("This user has not interacted with me yet!")

        prefix = self.bot.getPrefix(ctx)
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
                           boldCol=[],
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
            [data_user['findseed']['total_uses'], "Total Uses"],
            [eye_sum, "Total Eyes"]
        ]

        table2 = makeTable(data=table2,
                           boldCol=[],
                           code=[0],
                           sep={
                               0: " - ",
                           },
                           direction="left")

        embed.add_field(name="Eye Count", inline=True, value=table1)
        embed.add_field(name="Other Stats", inline=True, value=table2)
        await ctx.send(embed)

    @commands.command(name="profile", aliases=["userinfo"])
    @ctx_wrapper(redirect=True)
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
        prefix = self.bot.getPrefix(ctx)

        user = self.bot.getUser(ctx)

        if user is None:
            return await ctx.send("This user has not interacted with me yet!")

        # eye section
        if "findseed" in user:
            eyes = user["findseed"]["eye_count"].copy()
            while eyes[-1] == 0:
                eyes.pop()

            eye_sum = sum([eye * n for n, eye in enumerate(eyes)])
            best_eye = len(eyes) - 1
            embed.add_field(name="Eyes",
                            inline=False,
                            value=makeTable(
                                data=[
                                    ["Total", eye_sum, f"x{self.bot.getEmoji('mc_ender_eye')}"],
                                    ["Highest Rolled", best_eye, f"x{self.bot.getEmoji('mc_ender_eye')}"]
                                ],
                                boldCol=1,
                                sep={0: ": ",
                                     1: ""}))

        # command section
        keys = [
            ("ai", f"{prefix}ai"),
            ("imgur", f"{prefix}findimg"),
            ("findseed", f"{prefix}findseed"),
            ("playrandom", f"{prefix}playrandom"),
            ("@someone", f"@someone"),
            ("whisper", f"{prefix}whisper"),
            ("play", f"{prefix}play")
        ]

        data = []
        for key, title in keys:
            if key in user:
                data.append([key, title, user[key]["total_uses"]])

        length = getLongest([user[i[0]]["total_uses"] for i in data])

        message = [f"``{str(value).rjust(length)}`` - **{title}**" for key, title, value in data]

        embed.add_field(name="Command Uses",
                        inline=False,
                        value="\n".join(message))

        await ctx.send(embed)


async def setup(bot):
    await bot.add_cog(UserInfoCog(bot))
