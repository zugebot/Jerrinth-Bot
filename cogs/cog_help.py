# Jerrin Shirks
# native imports
# custom imports
from files.jerrinth import JerrinthBot
from files.buttonMenu import ButtonMenu
from files.discord_objects import *
from files.wrappers import *
from files.support import *
from files.config import *


class HelpCog(commands.Cog):
    def __init__(self, bot):
        self.bot: JerrinthBot = bot

    @wrapper_command(name="help", redirect=False)
    async def helpCommand(self, ctx, page=None):
        await makeHelpMenu(self, ctx, page)

    @wrapper_command(name="server", redirect=False)
    async def displayServer(self, ctx):
        embed = trophyEmbed("[You can find my owner here! [discord server]](https://discord.gg/vGW4pSF8wc)")
        await ctx.send(embed)


async def makeHelpMenu(bot_obj, ctx, page=None):

    possible_args = [
        [],
        ["profile", "channels", "debug", "ping"],
        ["chat", "history"],
        ["fun", "findimg", "findseed", "findblock", "eyecount", "someone", "@someone", "8ball"],
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

    prefix = bot_obj.bot.data["servers"][ctx.server].get("prefix", ",")
    start = f"``{prefix}"  # {star}
    start2 = f"``"  # {star}

    embed1 = newEmbed(f"  Hey there! My name's Jerrinth. "
                      f"\nI was created specifically to answer your every question! "
                      f"\nHere's what I can do for you:"
                      f"\n"
                      f"\n``Page 1``: Commands: Overview"
                      # f"\n``Page 2``: Commands: AI"
                      f"\n``Page 2``: Commands: Chat"
                      f"\n``Page 3``: Commands: FUN"
                      f"\n``Page 4``: Commands: Leaderboard"
                      f"\n``Page 5``: Commands: Voicechat"
                      f"\n``Page 6``: Commands: Admin")

    embed1.set_author(name="0/6 - Help Page", icon_url=ctx.author.avatar)

    embed2 = newEmbed(f"- {start}profile *id``"
                      f"\nmeant to show all your stats!"
                      f"\n- {start}channels``"
                      f"\nshows a list of all usable channels in this server."
                      f"\n- {start}debug``"
                      f"\na toggle for use debugging me."
                      f"\n- {start}server``"
                      f"\nsends a link to the bot's main server."
                      f"\n- {start2}/ping``"
                      f"\nthe bot will reply with it's ping!"
                      f"\n- {start}solve equ``"
                      f"\nwill solve any non-variable problem (calculator)."
                      f"\n"
                      f"\n★ Most multi-word commands can be used with their acronyms."
                      f"\n★ (arg) after a command means you **need** to pass a value to it."
                      f"\n★ (*arg) means the argument is not required."
                      f"\n"
                      f"\n★You can invite me to your server from my profile!"
                      f"\n★DM me to send update requests/bug reports/ask for help!"
                      f"\n"
                      f"\nCreated by: <@611427346099994641>"
                      f"\n__**[You can find my owner here!](https://discord.gg/vGW4pSF8wc)**__")

    embed2.set_author(name="1/6 - Commands: Overview", icon_url=ctx.author.avatar)
    """
    embed3 = newEmbed(f"  {start}ai *args `` - Ask me anything!"
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
    """
    embed4 = newEmbed(f"- {start}chat *msg``"
                      f"\nTalk to Jerrinth Bot!"
                      f"\n- {start}chat clear``"
                      f"\nClears the bots message memory."
                      f"\n- {start}chat prompt``"
                      f"\nShows the current prompt."
                      f"\n- {start}chat setprompt *msg``"
                      f"\nSets the prompt for the bot to follow."
                      f"\n- {start}chat resetprompt``"
                      f"\nResets the prompt that bot follows. "
                      f"\n- {start}chat history``"
                      f"\nSends a .json file of the chat history."
                      f"\n- {start}chat load``"
                      f"\nResets the prompt that bot follows. "
                      f"\nTo use **,chat load**, send the .json from **,chat history**."
                      f"\n"
                      f"\n★ Chat's are per channel."
                      f"\n"
                      f"\n★ The Default prompt is: **'You are a helpful assistant.'**"
                      f"\n★ Think of the default prompt, as the main rule the bot follows"
                      f"\n★ whilst answering your questions.")
    embed4.set_author(name="2/6 - Commands: Chat", icon_url=ctx.author.avatar)

    embed5 = newEmbed(f"\n- {start}findseed``"
                      f"\nroll a random minecraft end portal!"
                      f"\n- {start}findblock``"
                      f"\nroll UGBC-glitch blocks for end portals!"
                      f"\n- {start}eyecount``"
                      f"\ndisplay how many rolls you have of each eye count!"
                      f"\n- {start}findimg``"
                      f"\nsends a random imgur link!"
                      f"\n- {start2}@someone``"
                      f"\nping a random person!"
                      f"\n- {start}8ball *msg``"
                      f"\nask the magical :8ball: a question!"
                      f"\n- ``more coming soon.``")
    embed5.set_author(name="3/6 - Commands: FUN", icon_url=ctx.author.avatar)

    embed6 = newEmbed(f"  {start}data   `` - shows *my* overall accomplishments!"
                      f"\n"
                      f"\nYou can access leaderboards with these:"
                      f"\n- {start}leaderboard ai *n``"
                      f"\n**``{prefix}chat``** command uses."
                      f"\n- {start}leaderboard findimg *n``"
                      f"\n**``{prefix}findimg``** command uses."
                      f"\n- {start}leaderboard findseed *n``"
                      f"\n**``{prefix}findseed``** command uses."
                      f"\n- {start}leaderboard play *n``"
                      f"\n**``{prefix}play``** command uses."
                      f"\n- {start}leaderboard playrandom *n``"
                      f"\n**``{prefix}playrandom``** command uses."
                      f"\n- {start}leaderboard @someone *n``"
                      f"\n**``@someone``** command uses.")
    embed6.set_author(name="4/6 - Commands: Leaderboard", icon_url=ctx.author.avatar)

    embed7 = newEmbed(f"- {start}playjoin``"
                      f"\njoins a vc (only if you are in it)"
                      f"\n- {start}playleave``"
                      f"\nleaves a vc (only if you are in it)"
                      f"\n- {start}playstop``"
                      f"\nstops the current song that is playing."
                       f"\n- {start}playskip``"
                      f"\nskips the current song that is playing."
                      f"\n- {start}play``"
                      f"\nplay a piece of media in your voicechat!"
                      f"\n**,play** supports __filenames__, __youtube links__, and can even search youtube!"
                      f"\nall videos played using this command stays on my server for the **,playrandom** command."
                      f"\n"
                      f"\n- {start}playvolume *number``"
                      f"\nvalue between 0-100. Adjusts bot volume."
                      f"\n- {start}playrandom``"
                      f"\nplays a random video/audio file from my server."
                      f"\n- {start}playlist **search``"
                      f"\nshows an interactive list of all files on my server."
                      f"\nit will filter by search if you provide one."
                      f"\n- {start}playrename *oldname *newname``"
                      f"\nrenames a file on my server."
                      f"\n- {start}playdelete *filename``"
                      f"\nRemoves a file from my server."
                      f"\n")
    embed7.set_author(name="5/6 - Commands: Voicechat", icon_url=ctx.author.avatar)

    embed8 = newEmbed(f"**Admin privileges are required for these commands.**"
                      f"\n"
                      f"\n_Toggleable default settings for the server._"
                      f"\n- {start}setprefix prefix``"
                      f"\nallows changing the server bot prefix."
                      f"\n- {start}togglecensor``"
                      f"\nToggles the censorship of 18+ words."
                      f"\n- {start}toggleredirect``"
                      f"\nToggles me showing guidance to the clueless."
                      f"\n- {start}togglesomeone``"
                      f"\nToggles letting people use @someone."
                      f"\n- {start}toggletimeleft``"
                      f"\nToggles showing command refresh time."
                      f"\n- {start}toggletrue``"
                      f"\nToggles saying **\"true\"** when one says **\"true\"**."
                      f"\n- {start}togglereal``"
                      f"\nToggles saying **\"real\"** when one says **\"real\"**."
                      f"\n"
                      f"\n_**In order to use me, add me to a channel with these commands.**_"
                      f"\n- {start}addchannel *id``"
                      f"\nallows a channel to use commands."
                      f"\n- {start}omni``"
                      f"\nallows **all** channels to use commands."
                      f"\n"
                      f"\n_**You can remove my access to channels with these commands**._"
                      f"\n- {start}delchannel *id``"
                      f"\ndisables a channel from using commands."
                      f"\n- {start}delchannel all``"
                      f"\ndisables **all** channels from using commands."
                      f"\n"
                      f"\n_The Use of any of these commands are channel specific._"
                      # f"\n{start}channelengine *n `` - makes all users in a channel use set engine."
                      # f"\n{start}channelengine del`` - removes a set engine from a channel."
                      # f"\n"
                      f"\n- {start}channelprompt *msg``"
                      f"\nmakes all **{prefix}chat** use a custom prompt."
                      f"\n- {start}channelprompt del``"
                      f"\nremoves the channel prompt.")

    embed8.set_author(name="6/6 - Commands: Admin", icon_url=ctx.author.avatar)

    # embed3, embed4,
    pages = [embed1, embed2, embed4, embed5, embed6, embed7, embed8]
    menu = ButtonMenu(pages, index=page, timeout=180)
    try:
        await ctx.super.send(embed=pages[page], view=menu)
    except discord.errors.Forbidden:
        await ctx.send("Something with my permissions prevents me from sending the help command. "
                       "Consider giving me elevated roles and try again.")


async def setup(bot):
    await bot.add_cog(HelpCog(bot))
