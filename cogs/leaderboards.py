# Jerrin Shirks

# native imports
from discord.ext import commands

# custom imports
from jerrinth import JerrinthBot
from wrappers import *
from support import *
from config import *



class LeaderBoardsCog(commands.Cog):
    def __init__(self, bot):
        self.bot: JerrinthBot = bot
        self.leaderboard_amount = 15
        self.empty_message = "Apparently no one has used the **{}{}** command..."


    def getAmount(self, amount=None):
        if amount is None:
            return self.leaderboard_amount
        else:
            return int(amount)


    async def leaderboardObject(self, ctx, dict_key="", title="🏆 BLANK Total Uses Leaderboard", amount=None):
        items = [i for i in self.bot.getUserDict(ctx).items() if dict_key in i[1]]
        if len(items) == 0:
            return await ctx.send(errorEmbed(self.empty_message.format(self.bot.getPrefix(ctx), dict_key)))
        users = sorted(items, key=lambda x: x[1][dict_key]["total_uses"], reverse=True)

        table = []
        amount = self.getAmount(amount)
        for n, user in enumerate(users):
            key, value = user
            if n >= amount or value[dict_key]["total_uses"] == 0:
                break
            table.append([value[dict_key]["total_uses"], f"<@{key}>"])

        leaderboard = makeTable(table,
                                show_index=True,
                                code=[0]
                                )
        await ctx.send(newEmbed(leaderboard, title=title))

    @commands.command(name="leaderboards", aliases=["ts", "lb"])
    @ctx_wrapper
    @channel_redirect
    async def showLeaderboardsCommand(self, ctx):
        prefix = self.bot.getPrefix(ctx)

        embed = trophyEmbed()
        embed.title = "Leaderboards"
        embed.description = f"\n**``{prefix}tsa``** - **{prefix}ai** command uses." \
                            f"\n**``{prefix}tsi``** - **{prefix}findimg** command uses." \
                            f"\n**``{prefix}tsf``** - **{prefix}findseed** command uses." \
                            f"\n**``{prefix}tss``** - **@someone** command uses."
        await ctx.send(embed)




    @commands.command(name="topservai", aliases=["tsa", "TSA", "Tsa"])
    @discord.ext.commands.cooldown(*LEADERBOARD_COOLDOWN)
    @ctx_wrapper
    @channel_redirect
    async def topServerAICommand(self, ctx, amount=None):
        await self.leaderboardObject(ctx, "ai", "🏆 AI Total Uses Leaderboard", amount)


    @commands.command(name="topservi", aliases=["tsi", "TSI", "Tsi"])
    @discord.ext.commands.cooldown(*LEADERBOARD_COOLDOWN)
    @ctx_wrapper
    @channel_redirect
    async def topServerFindImgCommand(self, ctx, amount=None):
        await self.leaderboardObject(ctx, "imgur", f"🏆 Findimg Total Uses Leaderboard", amount)


    @commands.command(name="topservf", aliases=["tsf", "TSF", "Tsf"])
    @discord.ext.commands.cooldown(*LEADERBOARD_COOLDOWN)
    @ctx_wrapper
    @channel_redirect
    async def topServerFindSeedCommand(self, ctx, amount=None):
        await self.leaderboardObject(ctx, "findseed", f"🏆 Findseed Total Uses Leaderboard", amount)


    @commands.command(name="topservs", aliases=["tss", "TSS", "Tss"])
    @discord.ext.commands.cooldown(*LEADERBOARD_COOLDOWN)
    @ctx_wrapper
    @channel_redirect
    async def topAtSomeoneCommand(self, ctx, amount=None):
        await self.leaderboardObject(ctx, "@someone", f"🏆 @Someone Total Uses Leaderboard", amount)


    @commands.command(name="data", aliases=[])
    @ctx_wrapper
    @channel_redirect
    async def getDataCommand(self, ctx):
        prefix = self.bot.data[ctx.server]["prefix"]

        server_count = len(self.bot.guilds)
        server_user_total_count = self.bot.get_guild(ctx.serverInt).member_count
        user_count_server = len(self.bot.getUserDict(ctx))

        part1 = [
            [server_count, "Servers I am in!"],
            [user_count_server, "Users That have used me here!"],
            [server_user_total_count, "Users in this Server!"]
        ]
        table1 = makeTable(data=part1,
                           boldCol=1,
                           code=0,
                           sep={0: " - "})
        embed = trophyEmbed(title="🏆 These are my Stats!")
        embed.add_field(name="General",
                        inline=False,
                        value=table1)

        part2 = [
            ["Here", "Ever"],
            [0, 0, f"{prefix}ai"],
            [0, 0, f"{prefix}findimg"],
            [0, 0, f"{prefix}findseed"],
            [0, 0, f"@someone"],
        ]
        for server in self.bot.data:
            for user in self.bot.data[server]["users"]:
                userObj = self.bot.data[server]["users"][user]

                for tagNum, tag in enumerate(["ai", "imgur", "findseed", "@someone"], start=1):
                    if tag in userObj:
                        part2[tagNum][1] += userObj[tag]["total_uses"]
                        if server == ctx.server:
                            part2[tagNum][0] += userObj[tag]["total_uses"]
        table2 = makeTable(data=part2,
                           boldRow=[0],
                           boldCol=[2],
                           code=[0, 1],
                           sep={0: " | ",
                                1: " - "}
                           )
        embed.add_field(name="Command Usage Count",
                        inline=False,
                        value=table2)

        await ctx.send(embed)


async def setup(bot):
    await bot.add_cog(LeaderBoardsCog(bot))
