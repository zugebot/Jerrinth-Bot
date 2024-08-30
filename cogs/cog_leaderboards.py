# Jerrin Shirks
# native imports

# custom imports
from files.jerrinth import JerrinthBot
from files.discord_objects import *
from files.makeTable import makeTable
from files.wrappers import *
from files.support import *
from files.config import *


class LeaderBoardsCog(commands.Cog):
    def __init__(self, bot):
        self.bot: JerrinthBot = bot
        self.leaderboard_amount = 15
        self.empty_message = "Apparently no one has used the **{}{}** command..."

    @wrapper_command(name="leaderboard")
    async def showLeaderboardsCommand(self, ctx, board, amount=None):
        amount = self.getAmount(amount)
        title = "🏆 {} Total Uses Leaderboard"
        key = board.lower().replace("@", "")
        keys = {
            "chat": ["chat", "Chat"],
            "findimg": ["imgur", "Findimg"],
            "findseed": ["findseed", "Findseed"],
            "findblock": ["findblock", "FindBlock"],
            "whisper": ["whisper", "Whisper"],
            "play": ["play", "Play"],
            "playrandom": ["playrandom", "Playrandom"],
            "someone": ["someone", "@Someone"]
        }

        _help = f"try **{self.bot.gp(ctx)}help leaderboard** for more info!"
        if board is None:
            return await ctx.send(f"You must specify a leaderboard type, {_help}")
        if key not in keys:
            return await ctx.send(f"There is no **'{key}'** leaderboard, {_help}")

        keys = keys[key]
        await self.globalLeaderboardObject(ctx, keys[0], title.format(keys[1]), amount)

    def getAmount(self, amount=None):
        if amount is None:
            return self.leaderboard_amount
        else:
            return int(amount)

    """
    async def serverLeaderboardObject(self, ctx, dict_key="", title="🏆 BLANK Total Uses Leaderboard", amount=None):
        items = [i for i in self.bot.getUserDict(ctx).items() if dict_key in i[1]]
        if len(items) == 0:
            return await ctx.sendError(self.empty_message.format(self.bot.getPrefix(ctx), dict_key))
        users = sorted(items, key=lambda x: x[1][dict_key]["use_total"], reverse=True)

        table = []
        amount = self.getAmount(amount)
        for n, user in enumerate(users):
            key, value = user
            print(value[dict_key]["use_total"])
            if n >= amount + 1 or value[dict_key]["use_total"] == 0:
                break
            table.append([value[dict_key]["use_total"], f"<@{key}>"])

        leaderboard = makeTable(table,
                                show_index=True,
                                code=[0]
                                )
        await ctx.send(newEmbed(leaderboard, title=title))

    @unified_wrapper(name="topservai", aliases=["tsa"], cooldown=LEADERBOARD_COOLDOWN)
    async def topServerAICommand(self, ctx, amount=None):
        await self.serverLeaderboardObject(ctx, "ai", "🏆 [Server] AI Total Uses Leaderboard", amount)

    @unified_wrapper(name="topservi", aliases=["tsi"], cooldown=LEADERBOARD_COOLDOWN)
    async def topServerFindImgCommand(self, ctx, amount=None):
        await self.serverLeaderboardObject(ctx, "imgur", f"🏆 [Server] Findimg Total Uses Leaderboard", amount)

    @unified_wrapper(name="topservf", aliases=["tsf"], cooldown=LEADERBOARD_COOLDOWN)
    async def topServerFindSeedCommand(self, ctx, amount=None):
        await self.serverLeaderboardObject(ctx, "findseed", f"🏆 [Server] Findseed Total Uses Leaderboard", amount)

    @unified_wrapper(name="topservs", aliases=["tss"], cooldown=LEADERBOARD_COOLDOWN)
    async def topAtSomeoneCommand(self, ctx, amount=None):
        await self.serverLeaderboardObject(ctx, "@someone", f"🏆 [Server] @Someone Total Uses Leaderboard", amount)

    @unified_wrapper(name="topservpr", aliases=["tspr"], cooldown=LEADERBOARD_COOLDOWN)
    async def topServerPlayRandomCommand(self, ctx, amount=None):
        await self.serverLeaderboardObject(ctx, "playrandom", f"🏆 [Server] Playrandom Total Uses Leaderboard", amount)

    @unified_wrapper(name="topservw", aliases=["tsw"], cooldown=LEADERBOARD_COOLDOWN)
    async def topServerPlayRandomCommand(self, ctx, amount=None):
        await self.serverLeaderboardObject(ctx, "whisper", f"🏆 [Server] Whisper Total Uses Leaderboard", amount)

    @unified_wrapper(name="topservp", aliases=["tsp"], cooldown=LEADERBOARD_COOLDOWN)
    async def topServerPlayRandomCommand(self, ctx, amount=None):
        await self.serverLeaderboardObject(ctx, "play", f"🏆 [Server] Play Total Uses Leaderboard", amount)
    """

    async def globalLeaderboardObject(self, ctx, dict_key="chat", title="", maximum_users=None):
        items = [i for i in self.bot.data["users"].items() if dict_key in i[1]]
        if len(items) == 0:
            return await ctx.sendError(self.empty_message.format(self.bot.gp(ctx), dict_key))

        users = sorted(items,
                       key=lambda x: x[1][dict_key]["use_total"],
                       reverse=True)
        table = []
        maximum_users = self.getAmount(maximum_users)
        for n, (key, value) in enumerate(users):
            if n >= maximum_users or value[dict_key]["use_total"] == 0:
                break
            table.append([value[dict_key]["use_total"], f"<@{key}>"])
        leaderboard = makeTable(table, show_index=True, code=[0])

        await ctx.send(newEmbed(leaderboard, title=title))

    @wrapper_command(name="data")
    async def getDataCommand(self, ctx):
        prefix = self.bot.gp(ctx)

        server_count = len(self.bot.guilds)
        server_user_total_count = self.bot.get_guild(ctx.serverInt).member_count
        user_count_server = len(self.bot.getUserDict(ctx))

        part1 = [
            [server_count, "Servers I am in!"],
            [user_count_server, "Unique Users!"],
            [server_user_total_count, "Users in this Server!"]
        ]
        table1 = makeTable(data=part1,
                           bold_col=1,
                           code=0,
                           sep={0: " - "})
        embed = trophyEmbed(title="🏆 These are my Stats!")
        embed.add_field(name="General",
                        inline=False,
                        value=table1)

        part2 = [
            [0, f"{prefix}chat"],
            [0, f"{prefix}findimg"],
            [0, f"{prefix}findseed"],
            [0, f"{prefix}findblock"],
            [0, f"{prefix}whisper"],
            [0, f"{prefix}play"],
            [0, f"{prefix}playrandom"],
            [0, f"@someone"],
        ]

        command_list = ["chat", "imgur", "findseed", "findblock", "whisper", "play", "playrandom", "someone"]

        # TODO: store the total command count elsewhere
        for user in self.bot.data["users"]:
            user_obj = self.bot.data["users"][user]

            for tagNum, tag in enumerate(command_list):
                if tag in user_obj:
                    part2[tagNum][0] += user_obj[tag]["use_total"]

        table2 = makeTable(data=part2,
                           bold_row=[0],
                           bold_col=[1],
                           code=[0],
                           sep={0: " - "}
                           )
        embed.add_field(name="Command Usage Count",
                        inline=False,
                        value=table2)

        await ctx.send(embed)


async def setup(bot):
    await bot.add_cog(LeaderBoardsCog(bot))
