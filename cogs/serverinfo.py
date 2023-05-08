# Jerrin Shirks

# native imports

# custom imports
from files.jerrinth import JerrinthBot
from files.wrappers import *
from files.support import *



class ServerInfoCog(commands.Cog):
    def __init__(self, bot):
        self.bot: JerrinthBot = bot


    @commands.command(name="settings", aliases=[])
    @ctx_wrapper
    async def serverSettingsCommand(self, ctx):
        def emoji(flag: bool) -> str:
            if flag:
                return "✅"
            return "❌"

        server = self.bot.getServer(ctx)
        prefix = server.get("prefix", ",")
        censor = server.get("censorship", True)
        someone = server.get("@someone", False)
        everywhere = server.get("usable_everywhere", False)
        redirect = server.get("channel_redirect", True)
        timeleft = server.get("show_time_left", True)
        sayreal = server.get("say_real", True)
        saytrue = server.get("say_true", True)

        table = [
            [emoji(everywhere), f"Usable Everywhere", f"{prefix}omni"],
            [emoji(censor), f"Channel Redirect", f"{prefix}toggleredirect"],
            [emoji(someone), f"@someone Command", f"{prefix}togglesomeone"],
            [emoji(redirect), f"{prefix}ai Censorship", f"{prefix}togglecensor"],
            [emoji(timeleft), f"Show Time Left", f"{prefix}toggletimeleft"],
            [emoji(sayreal), f"\"True\" Response", f"{prefix}toggletrue"],
            [emoji(saytrue), f"\"Real\" Response", f"{prefix}togglereal"]
        ]

        data = makeTable(table,
                         show_index=False,
                         code=[1],
                         sep={1: " - "},
                         direction=2)

        embed = newEmbed(f"Prefix: **{prefix}**\n" + data, title="Server Settings")
        await ctx.send(embed)


async def setup(bot):
    await bot.add_cog(ServerInfoCog(bot))
