# Jerrin Shirks

# native imports
from discord.ext import commands

# custom imports
from jerrinth import JerrinthBot
from wrappers import *
from support import *
from config import *


class HelpCog(commands.Cog):
    def __init__(self, bot):
        self.bot: JerrinthBot = bot
        self.star = "☆"  # ☆★⭐

    @commands.command(name="help", aliases=["h2"])
    @ctx_wrapper
    async def displayHelpCommand(self, ctx, page=None):

        possible_args = [
            ["profile", "channels", "debug", "ping"],
            ["ai", "openai", "solve", "engine", "setfooter"],
            ["fun", "findimg", "findseed", "eyecount", "someone", "@someone", "8ball"],
            ["leaderboard", "board", "data", "tsa", "tsi", "tsf", "tss"],
            ["admin", "mod", "prefix", "censor", "redirect",
             "addchannel", "delchannel", "deletechannel", "removechannel",
             "channelengine"],
            ["other"],
            ["about"],
        ]

        # parse the arg:
        if page == "":
            page = 0
        elif page is None:
            page = 0
        elif page.isnumeric():
            page = int(page)
            if not (0 < page < 6):
                page = 0
        else:
            for n, arg_list in enumerate(possible_args):
                if page in arg_list:
                    page = n + 1
                    break
            else:
                page = 0

        prefix = self.bot.data[ctx.server]["prefix"]
        start = f"{self.star} ``{prefix}"
        start2 = f"{self.star} ``"

        embed1 = newEmbed(f"  Hey there! My name's Jerrinth. "
                          f"\nI was created specifically to answer your every question! "
                          f"\nHere's what I can do for you:"
                          f"\n"
                          f"\n``Page 1``: Commands: Overview"
                          f"\n``Page 2``: Commands: AI"
                          f"\n``Page 3``: Commands: FUN"
                          f"\n``Page 4``: Commands: Leaderboard"
                          f"\n``Page 5``: Commands: Admin")
        # f"\n``Page 6``: Update Log")
        embed1.set_author(name="0/5 - Help Page", icon_url=ctx.author.avatar)

        embed2 = newEmbed(f"  {start}profile *id`` - meant to show all your stats!"
                          f"\n{start}channels   `` - shows a list of all usable channels in this server."
                          f"\n{start}debug      `` - a toggle for use debugging me."
                          f"\n{start2}/ping       `` - The bot will reply with it's ping!"
                          f"\n"
                          f"\n★ All multi-word commands can also be used with their acronyms."
                          f"\n★ (arg) after a command means you need to pass a value to it."
                          f"\n★ (*arg) means the argument is not required."
                          f"\n"
                          f"\n★You can invite me to your server from my profile!"
                          f"\n★DM me to send update requests/bug reports/ask for help!"
                          f"\n"
                          f"\nCreated by: <@611427346099994641>"
                          f"\n__**[You can find my owner here!](https://discord.gg/vGW4pSF8wc)**__")

        embed2.set_author(name="1/5 - Commands: Overview", icon_url=ctx.author.avatar)

        embed3 = newEmbed(f"  {start}ai *args `` - Ask me anything!"
                          f"\n{start}solve equ`` - Will solve any non-variable problem."
                          f"\n{start}engine *n`` - set engine for use of the **AI** command."
                          f"\n{start}aifooter `` - shows the current engine in response footer."
                          f"\n{start}aihelp   `` - indepth use of args for the **AI** command."
                          f"\n{start}togglenginehelp`` - Toggles {prefix}engine showing help.")
        embed3.set_author(name="2/5 - Commands: AI", icon_url=ctx.author.avatar)

        embed4 = newEmbed(f"\n{start}findseed `` - roll a random minecraft end portal!"
                          f"\n{start}eyecount `` - display how many rolls you have of each eye count!"
                          f"  {start}findimg  `` - sends a random imgur link!"
                          f"\n{start2}@someone`` - ping a random person!"
                          f"\n{start}8ball ...`` - ask the magical :8ball: a question!"
                          f"\n{self.star} ``more coming soon.``")
        embed4.set_author(name="3/5 - Commands: FUN", icon_url=ctx.author.avatar)

        embed5 = newEmbed(f"  {start}data   `` - shows *my* overall accomplishments!"
                          f"\n{start}tsa *n `` - leaderboard of **AI** command uses."
                          f"\n{start}tsi *n `` - leaderboard of **FINDIMG** command uses."
                          f"\n{start}tsf *n `` - leaderboard of **FINDSEED** command uses."
                          f"\n{start}tss *n `` - leaderboard of **@SOMEONE** command uses.")
        embed5.set_author(name="4/5 - Commands: Leaderboard", icon_url=ctx.author.avatar)

        embed6 = newEmbed(f"\n{start}setprefix prefix `` - allows changing the server bot prefix."
                          f"\n{start}togglecensor     `` - Toggles the censorship of 18+ words."
                          f"\n{start}toggleredirect   `` - Toggles me showing guidance to the clueless."
                          f"\n{start}togglesomeone    `` - Toggles letting people use @someone."
                          f"\n{start}toggletimeleft   `` - Toggles showing command refresh time."
                          f"\n{start}togglereal       `` - Toggles me saying \"true\" when one says \"true\"."
                          f"\n{start}togglereal       `` - Toggles me saying \"real\" when one says \"real\"."
                          f"\n"
                          f"\n{start}addchannel *id`` - allows a channel to use commands."
                          f"\n{start}addchannel all`` - allows **all** channels to use commands."
                          f"\n"
                          f"\n{start}delchannel *id`` - disables a channel from using commands."
                          f"\n{start}delchannel all`` - disables **all** channels from using commands."
                          f"\n"
                          f"\n{start}channelengine *n `` - makes all users in a channel use set engine."
                          f"\n{start}channelengine del`` - removes a set engine from a channel.")

        embed6.set_author(name="5/5 - Commands: Admin", icon_url=ctx.author.avatar)

        """
        embed7 = newEmbed(f"Last updated <t:{self.bot.settings['last_update']}>."
                          f"\n\n ★ **{prefix}ai**: raised cap for it's usage"
                          f"\n   There is a far lower chance of being rate limited!"
                          f"\n\n ★ **{prefix}ai**: rewrote response to be asynchronous."
                          f"\n   This means multiple people can use it at the same time!"
                          f"\n\n ★ **{prefix}findimg**: rewrote response to be asynchronous."
                          f"\n   This means multiple people can use it at the same time!"
                          f"\n\n ★ **{prefix}setfooter**: New Command!")
        embed7.set_author(name="6/6 - Update Log", icon_url=ctx.author.avatar)
        """

        pages = [embed1, embed2, embed3, embed4, embed5, embed6]
        menu = ButtonMenu(pages, index=page, timeout=180)
        try:
            await ctx.super.send(embed=pages[page], view=menu)
        except discord.errors.Forbidden:
            await ctx.send("Something with my permissions prevents me from sending the help command. "
                           "Consider giving me elevated roles and try again.")

    @commands.command(name="aihelp", aliaes=[])
    @ctx_wrapper
    @channel_redirect
    async def displayAIHelpCommand(self, ctx):
        prefix = self.bot.data[ctx.server]["prefix"]

        embed = newEmbed(f"  Place any argument you want after the command,"
                         f"\nwhere each argument is separated with a space.")
        embed.set_author(name=f"{prefix}ai Help Page")

        embed.add_field(name=f"Using the _Format_ Argument: **f=#**",
                        inline=False,
                        value=f"\nThis argument changes the format of the text that I respond with." \
                              f"\n**``1. f=e``**: My response will be in an embed (default)." \
                              f"\n**``2. f=t``**: My response will be plaintext." \
                              f"\n**``3. f=c``**: My response will be inside a code-block." \
                              f"\n• when using **f=c**, if you include the name of a coding language," \
                              f"\n• The code-block will have colored syntax.")

        embed.add_field(name=f"Using the _Random_ Argument: **r=#**",
                        inline=False,
                        value=f"\nIf you use the argument **r**, responses will no longer be the same." \
                              f"\nThis argument can also be phrased as **r=N**, where 0 < N < 1.")

        embed.add_field(
            name=f"**Examples!**",
            inline=False,
            value=f"  **{prefix}ai** **f=c** write me a __python__ calculator program!" \
                  f"\n**{prefix}ai** **r=1** **f=t** pick a random number between 1 and 10.")

        await ctx.send(embed)

    @commands.command(name="server", aliases=[])
    @ctx_wrapper
    # @channel_redirect
    async def displayServer(self, ctx):
        embed = trophyEmbed("[You can find my owner here! [discord server]](https://discord.gg/vGW4pSF8wc)")
        await ctx.send(embed)


async def setup(bot):
    await bot.add_cog(HelpCog(bot))
