# Jerrin Shirks

# native imports

# custom imports
from files.jerrinth import JerrinthBot
from files.wrappers import *
from files.support import *
from files.config import *


class LeaderBoardsCog(commands.Cog):
    def __init__(self, bot):
        self.bot: JerrinthBot = bot
        self.leaderboard_amount = 15
        self.empty_message = "Apparently no one has used the **{}{}** command..."

    @commands.command(name="leaderboards", aliases=["ts", "lb"])
    @ctx_wrapper
    @channel_redirect
    async def showLeaderboardsCommand(self, ctx):
        prefix = self.bot.getPrefix(ctx)

        embed = trophyEmbed()
        embed.title = "Leaderboards"
        embed.description = f'\n**``{prefix}tsa ``** - **{prefix}ai** command uses.' \
                            f'\n**``{prefix}tsi ``** - **{prefix}findimg** command uses.' \
                            f'\n**``{prefix}tsf ``** - **{prefix}findseed** command uses.' \
                            f'\n**``{prefix}tspr``** - **{prefix}playrandom** command uses.' \
                            f'\n**``{prefix}tsp ``** - **{prefix}play** command uses.' \
                            f'\n**``{prefix}tsw ``** - **{prefix}whisper** command uses.' \
                            f'\n**``{prefix}tss ``** - **@someone** command uses.'

        await ctx.send(embed)

    @commands.command(name="leaderboard")
    @ctx_wrapper
    @channel_redirect
    async def showLeaderboardsCommand(self, ctx, board, amount=None):
        amount = self.getAmount(amount)
        title = "🏆 [Global] {} Total Uses Leaderboard"
        key = board.lower().replace("@", "")
        keys = {
            "ai": ["ai", "AI"],
            "findimg": ["imgur", "Findimg"],
            "findseed": ["findseed", "Findseed"],
            "playrandom": ["playrandom", "Playrandom"],
            "whisper": ["whisper", "Whisper"],
            "play": ["play", "Play"],
            "someone": ["@someone", "@Someone"]
        }
        if key not in keys:
            return
        keys = keys[key]
        print(keys[0])
        await self.globalLeaderboardObject(ctx, keys[0], title.format(keys[1]), amount)

    def getAmount(self, amount=None):
        if amount is None:
            return self.leaderboard_amount
        else:
            return int(amount)

    async def serverLeaderboardObject(self, ctx, dict_key="", title="🏆 BLANK Total Uses Leaderboard", amount=None):
        items = [i for i in self.bot.getUserDict(ctx).items() if dict_key in i[1]]
        if len(items) == 0:
            return await ctx.sendError(self.empty_message.format(self.bot.getPrefix(ctx), dict_key))
        users = sorted(items, key=lambda x: x[1][dict_key]["total_uses"], reverse=True)

        table = []
        amount = self.getAmount(amount)
        for n, user in enumerate(users):
            key, value = user
            if n >= amount + 1 or value[dict_key]["total_uses"] == 0:
                break
            table.append([value[dict_key]["total_uses"], f"<@{key}>"])

        leaderboard = makeTable(table,
                                show_index=True,
                                code=[0]
                                )
        await ctx.send(newEmbed(leaderboard, title=title))

    @commands.command(name="topservai", aliases=["tsa", "TSA", "Tsa"])
    @discord.ext.commands.cooldown(*LEADERBOARD_COOLDOWN)
    @ctx_wrapper
    @channel_redirect
    async def topServerAICommand(self, ctx, amount=None):
        await self.serverLeaderboardObject(ctx, "ai", "🏆 [Server] AI Total Uses Leaderboard", amount)

    @commands.command(name="topservi", aliases=["tsi", "TSI", "Tsi"])
    @discord.ext.commands.cooldown(*LEADERBOARD_COOLDOWN)
    @ctx_wrapper
    @channel_redirect
    async def topServerFindImgCommand(self, ctx, amount=None):
        await self.serverLeaderboardObject(ctx, "imgur", f"🏆 [Server] Findimg Total Uses Leaderboard", amount)

    @commands.command(name="topservf", aliases=["tsf", "TSF", "Tsf"])
    @discord.ext.commands.cooldown(*LEADERBOARD_COOLDOWN)
    @ctx_wrapper
    @channel_redirect
    async def topServerFindSeedCommand(self, ctx, amount=None):
        await self.serverLeaderboardObject(ctx, "findseed", f"🏆 [Server] Findseed Total Uses Leaderboard", amount)

    @commands.command(name="topservs", aliases=["tss", "TSS", "Tss"])
    @discord.ext.commands.cooldown(*LEADERBOARD_COOLDOWN)
    @ctx_wrapper
    @channel_redirect
    async def topAtSomeoneCommand(self, ctx, amount=None):
        await self.serverLeaderboardObject(ctx, "@someone", f"🏆 [Server] @Someone Total Uses Leaderboard", amount)

    @commands.command(name="topservpr", aliases=["tspr", "TSPR", "Tspr"])
    @discord.ext.commands.cooldown(*LEADERBOARD_COOLDOWN)
    @ctx_wrapper
    @channel_redirect
    async def topServerPlayRandomCommand(self, ctx, amount=None):
        await self.serverLeaderboardObject(ctx, "playrandom", f"🏆 [Server] Playrandom Total Uses Leaderboard", amount)

    @commands.command(name="topservw", aliases=["tsw", "TSW", "Tsw"])
    @discord.ext.commands.cooldown(*LEADERBOARD_COOLDOWN)
    @ctx_wrapper
    @channel_redirect
    async def topServerPlayRandomCommand(self, ctx, amount=None):
        await self.serverLeaderboardObject(ctx, "whisper", f"🏆 [Server] Whisper Total Uses Leaderboard", amount)

    @commands.command(name="topservp", aliases=["tsp", "TSP", "Tsp"])
    @discord.ext.commands.cooldown(*LEADERBOARD_COOLDOWN)
    @ctx_wrapper
    @channel_redirect
    async def topServerPlayRandomCommand(self, ctx, amount=None):
        await self.serverLeaderboardObject(ctx, "play", f"🏆 [Server] Play Total Uses Leaderboard", amount)

    async def globalLeaderboardObject(self, ctx, dict_key="ai", title="", maximum_users=None):
        items = [i for i in self.bot.data["users"].items() if dict_key in i[1]]
        users = sorted(items,
                       key=lambda x: x[1][dict_key]["total_uses"],
                       reverse=True)
        print(users)
        table = []
        maximum_users = self.getAmount(maximum_users)
        for n, (key, value) in enumerate(users):
            if n >= maximum_users or value[dict_key]["total_uses"] == 0:
                break
            table.append([value[dict_key]["total_uses"], f"<@{key}>"])
        print(table)
        leaderboard = makeTable(table, show_index=True, code=[0])

        await ctx.send(newEmbed(leaderboard, title=title))

    @commands.command(game="globalservai", aliases=["gsa", "GSA", "Gsa"])
    @discord.ext.commands.cooldown(*LEADERBOARD_COOLDOWN)
    @ctx_wrapper
    @channel_redirect
    async def topGlobalAICommand(self, ctx, amount=None):
        await self.globalLeaderboardObject(ctx, "ai", "🏆 [Global] AI Total Uses Leaderboard", amount)

    @commands.command(name="globalservi", aliases=["gsi", "GSI", "Gsi"])
    @discord.ext.commands.cooldown(*LEADERBOARD_COOLDOWN)
    @ctx_wrapper
    @channel_redirect
    async def topGlobalFindImgCommand(self, ctx, amount=None):
        await self.globalLeaderboardObject(ctx, "imgur", f"🏆 [Global] Findimg Total Uses Leaderboard", amount)

    @commands.command(name="globalservf", aliases=["gsf", "GSF", "Gsf"])
    @discord.ext.commands.cooldown(*LEADERBOARD_COOLDOWN)
    @ctx_wrapper
    @channel_redirect
    async def topGlobalFindSeedCommand(self, ctx, amount=None):
        await self.globalLeaderboardObject(ctx, "findseed", f"🏆 [Global] Findseed Total Uses Leaderboard", amount)

    @commands.command(name="globalservs", aliases=["gss", "GSS", "Gss"])
    @discord.ext.commands.cooldown(*LEADERBOARD_COOLDOWN)
    @ctx_wrapper
    @channel_redirect
    async def topGlobalAtSomeoneCommand(self, ctx, amount=None):
        await self.globalLeaderboardObject(ctx, "@someone", f"🏆 [Global] @Someone Total Uses Leaderboard", amount)

    @commands.command(name="globalservpr", aliases=["gspr", "GSPR", "Gspr"])
    @discord.ext.commands.cooldown(*LEADERBOARD_COOLDOWN)
    @ctx_wrapper
    @channel_redirect
    async def topGlobalPlayRandomCommand(self, ctx, amount=None):
        await self.globalLeaderboardObject(ctx, "playrandom", f"🏆 [Global] Playrandom Total Uses Leaderboard", amount)

    @commands.command(name="globalservw", aliases=["gsw", "GSW", "Gsw"])
    @discord.ext.commands.cooldown(*LEADERBOARD_COOLDOWN)
    @ctx_wrapper
    @channel_redirect
    async def topGlobalWhisperCommand(self, ctx, amount=None):
        await self.globalLeaderboardObject(ctx, "whisper", f"🏆 [Global] Whisper Total Uses Leaderboard", amount)

    @commands.command(name="globalservp", aliases=["gsp", "GSP", "Gsp"])
    @discord.ext.commands.cooldown(*LEADERBOARD_COOLDOWN)
    @ctx_wrapper
    @channel_redirect
    async def topGlobalWhisperCommand(self, ctx, amount=None):
        await self.globalLeaderboardObject(ctx, "play", f"🏆 [Global] Play Total Uses Leaderboard", amount)

    @commands.command(name="data", aliases=[])
    @ctx_wrapper
    @channel_redirect
    async def getDataCommand(self, ctx):
        prefix = self.bot.data["servers"][ctx.server]["prefix"]

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
            [0, 0, f"{prefix}ai & {prefix}chat"],
            [0, 0, f"{prefix}findimg"],
            [0, 0, f"{prefix}findseed"],
            [0, 0, f"{prefix}playrandom"],
            [0, 0, f"{prefix}whisper"],
            [0, 0, f"{prefix}play"],
            [0, 0, f"@someone"],
        ]
        for server in self.bot.data["servers"]:
            for user in self.bot.data["servers"][server]["users"]:
                user_obj = self.bot.data["servers"][server]["users"][user]

                for tagNum, tag in enumerate(["ai", "imgur", "findseed", "playrandom",
                                              "whisper", "play", "@someone"], start=1):
                    if tag in user_obj:
                        part2[tagNum][1] += user_obj[tag]["total_uses"]
                        if server == ctx.server:
                            part2[tagNum][0] += user_obj[tag]["total_uses"]
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
