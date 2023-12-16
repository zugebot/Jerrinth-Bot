# Jerrin Shirks

# native imports

# custom imports
from files.jerrinth import JerrinthBot
from files.wrappers import *
from files.support import *
from files.config import *


class HelpCog(commands.Cog):
    def __init__(self, bot):
        self.bot: JerrinthBot = bot

    @commands.command(name="help", aliases=["h2"])
    @ctx_wrapper
    async def displayHelpCommand(self, ctx, page=None):
        star = "☆"  # ☆★⭐

        possible_args = [
            [],
            ["profile", "channels", "debug", "ping"],
            ["ai", "openai", "solve", "engine", "setfooter", "whisper"],
            ["chat", "history"],
            ["fun", "findimg", "findseed", "eyecount", "someone", "@someone", "8ball"],
            ["leaderboard", "board", "data", "tsa", "tsi", "tsf", "tss"],
            ["join", "leave", "play", "playrandom", "playlist", "playlist", "voice", "voicechat", "vc", "playrename"],
            ["admin", "mod", "prefix", "censor", "redirect",
             "addchannel", "delchannel", "deletechannel", "removechannel", "omni",
             "channelengine", "channeladd", "channeldel", "channeldelete", "channelremove"],
            ["other"],
        ]

        if isinstance(page, int):
            page = str(page - 1)
        if not page:
            page = 0
        elif page.isnumeric():
            page = int(page)
            if not (0 < page < 8):
                page = 0
        else:
            for n, arg_list in enumerate(possible_args):
                if page in arg_list:
                    page = n
                    break
            else:
                page = 0

        prefix = self.bot.data["servers"][ctx.server]["prefix"]
        start = f"{star} ``{prefix}"
        start2 = f"{star} ``"

        embed1 = newEmbed(f"  Hey there! My name's Jerrinth. "
                          f"\nI was created specifically to answer your every question! "
                          f"\nHere's what I can do for you:"
                          f"\n"
                          f"\n``Page 1``: Commands: Overview"
                          f"\n``Page 2``: Commands: AI"
                          f"\n``Page 3``: Commands: Chat"
                          f"\n``Page 4``: Commands: FUN"
                          f"\n``Page 5``: Commands: Leaderboard"
                          f"\n``Page 6``: Commands: Voicechat"
                          f"\n``Page 7``: Commands: Admin")

        embed1.set_author(name="0/7 - Help Page", icon_url=ctx.author.avatar)

        embed2 = newEmbed(f"  {start}profile *id`` - meant to show all your stats!"
                          f"\n{start}channels   `` - shows a list of all usable channels in this server."
                          f"\n{start}debug      `` - a toggle for use debugging me."
                          f"\n{start}server     `` - sends a link to the bot's main server."
                          f"\n{start2}/ping       `` - the bot will reply with it's ping!"
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

        embed2.set_author(name="1/7 - Commands: Overview", icon_url=ctx.author.avatar)

        embed3 = newEmbed(f"  {start}ai *args `` - Ask me anything!"
                          f"\n{start}solve equ`` - Will solve any non-variable problem."
                          f"\n{start}engine *n`` - set engine for use of the **AI** command."
                          f"\n{start}aifooter `` - shows the current engine in response footer."
                          f"\n{start}aihelp   `` - indepth use of args for the **AI** command."
                          f"\n{start}togglenginehelp`` - Toggles {prefix}engine showing help."
                          f"\n"
                          f"\n{start}whisper    `` - Upload an audio file, and I will convert it to text!"
                          f"\n{start}whisper raw`` - returns non-formatted text from the file."
                          f"\n**{prefix}whisper** supports __mp3__, __mp4__, __mpeg__, __mpga__, "
                          f"__m4a__, __wav__, and __webm__ files.")
        embed3.set_author(name="2/7 - Commands: AI", icon_url=ctx.author.avatar)

        embed4 = newEmbed(f"  {start}chat *msg   `` - Just like **{prefix}ai**, but with memory!"
                          f"\n{start}chat clear  `` - Clears the bot's message memory."
                          f"\n{start}chat prompt `` - Shows the current prompt."
                          f"\n{start}chat setprompt *msg`` - Sets the prompt for the bot to follow."
                          f"\n{start}chat resetprompt `` - Resets the prompt that bot follows. "
                          f"\n{start}chat history`` - Sends a .json file of the chat history."
                          f"\n{start}chat load   `` - Resets the prompt that bot follows. "
                          f"\nTo use **,chat load**, send the .json from **,chat history**."
                          f"\n"
                          f"\n★ Chat's are per channel."
                          f"\n"
                          f"\n★ The Default prompt is: **'You are a helpful assistant.'**"
                          f"\n★ Think of the default prompt, as the main rule the bot follows"
                          f"\n★ whilst answering your questions.")
        embed4.set_author(name="3/7 - Commands: Chat", icon_url=ctx.author.avatar)

        embed5 = newEmbed(f"\n{start}findseed  `` - roll a random minecraft end portal!"
                          f"\n{start}eyecount  `` - display how many rolls you have of each eye count!"
                          f"\n{start}findimg   `` - sends a random imgur link!"
                          f"\n{start2}@someone   `` - ping a random person!"
                          f"\n{start}8ball *msg`` - ask the magical :8ball: a question!"
                          f"\n{star}  ``more coming soon.``")
        embed5.set_author(name="4/7 - Commands: FUN", icon_url=ctx.author.avatar)

        embed6 = newEmbed(f"  {start}data   `` - shows *my* overall accomplishments!"
                          f"\n"
                          f"\nYou can access leaderboards containing command uses with these:"
                          f"\n{start}leaderboard ai *n`` - **``{prefix}ai``** command uses."
                          f"\n{start}leaderboard findimg  *n`` - **``{prefix}findimg``** command uses."
                          f"\n{start}leaderboard findseed  *n`` - **``{prefix}findseed``** command uses."
                          f"\n{start}leaderboard play *n`` - **``{prefix}play``** command uses."
                          f"\n{start}leaderboard playrandom *n`` - **``{prefix}playrandom``** command uses."
                          f"\n{start}leaderboard @someone  *n`` - **``@someone``** command uses.")
        embed6.set_author(name="5/7 - Commands: Leaderboard", icon_url=ctx.author.avatar)

        embed7 = newEmbed(f"  {start}join`` - joins a vc (only if you are in it)"
                          f"\n{start}leave`` - leaves a vc (only if you are in it)"
                          f"\n"
                          f"\n{start}stop `` - stops the current song that is playing."
                          f"\n{start}play `` - play a piece of media in your voicechat!"
                          f"\n**,play** supports filenames, youtube links and discord uploads."
                          f"\nyoutube uploads must be shorter than 15 minutes in length."
                          f"\nall videos played using this command stays on my server for the **,playrandom** command."
                          f"\n"
                          f"\n{start}volume *number`` - value between 0-100. Adjusts bot volume."
                          f"\n{start}playrandom    `` - plays a random video/audio file from my server."
                          f"\n{start}playlist      `` - shows an interactive list of all files on my server."
                          f"\n{start}playrename *oldname *newname`` - renames a file on my server."
                          f"\n{start}playsearch keyword`` - Returns a list of files with that keyword."
                          f"\n")
        embed7.set_author(name="5/7 - Commands: Voicechat", icon_url=ctx.author.avatar)

        embed8 = newEmbed(f"**All commands here can only be used by those with admin privileges.**"
                          f"\n"
                          f"\n_Toggleable default settings for the server._"
                          f"\n{start}setprefix prefix`` - allows changing the server bot prefix."
                          f"\n{start}togglecensor    `` - Toggles the censorship of 18+ words."
                          f"\n{start}toggleredirect  `` - Toggles me showing guidance to the clueless."
                          f"\n{start}togglesomeone   `` - Toggles letting people use @someone."
                          f"\n{start}toggletimeleft  `` - Toggles showing command refresh time."
                          f"\n{start}togglereal      `` - Toggles saying **\"true\"** when one says **\"true\"**."
                          f"\n{start}togglereal      `` - Toggles saying **\"real\"** when one says **\"real\"**."
                          f"\n"
                          f"\n_In order to use me, add me to a channel with these commands._"
                          f"\n{start}addchannel *id`` - allows a channel to use commands."
                          f"\n{start}omni          `` - allows **all** channels to use commands."
                          f"\n"
                          f"\n_You can remove my access to channels with these commands._"
                          f"\n{start}delchannel *id`` - disables a channel from using commands."
                          f"\n{start}delchannel all`` - disables **all** channels from using commands."
                          f"\n"
                          f"\n_The Use of any of these commands are channel specific._"
                          f"\n{start}channelengine *n `` - makes all users in a channel use set engine."
                          f"\n{start}channelengine del`` - removes a set engine from a channel."
                          f"\n"
                          f"\n_The Use of any of these commands are channel and 'chat-turbo-3.5' specific._"
                          f"\n{start}channelprompt *msg`` - makes all **{prefix}chat** use a custom prompt."
                          f"\n{start}channelprompt del `` - removes the channel prompt.")

        embed8.set_author(name="7/7 - Commands: Admin", icon_url=ctx.author.avatar)

        """
        embed8 = newEmbed(f"Last updated <t:{self.bot.settings['last_update']}>."
                          f"\n\n ★ **{prefix}ai**: raised cap for it's usage"
                          f"\n   There is a far lower chance of being rate limited!"
                          f"\n\n ★ **{prefix}ai**: rewrote response to be asynchronous."
                          f"\n   This means multiple people can use it at the same time!"
                          f"\n\n ★ **{prefix}findimg**: rewrote response to be asynchronous."
                          f"\n   This means multiple people can use it at the same time!"
                          f"\n\n ★ **{prefix}setfooter**: New Command!")
        embed8.set_author(name="6/6 - Update Log", icon_url=ctx.author.avatar)
        """

        pages = [embed1, embed2, embed3, embed4, embed5, embed6, embed7, embed8]
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
        prefix = self.bot.data["servers"][ctx.server]["prefix"]

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
