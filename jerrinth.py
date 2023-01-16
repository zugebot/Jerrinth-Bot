# Jerrin Shirks

# native imports
from discord.ext import commands

# custom imports
from support import *
from data_manager import DataManager
from funcs.nsp import NumericStringParser
from funcs.ai import AI
from funcs.imgur import Imgur



class JerrinthBot(commands.Bot, DataManager):
    def __init__(self, data_version: int,
                 debug: bool = False,
                 maintenance: bool = False,
                 direct_message: bool = True) -> None:
        if not os.path.isdir("data"):
            os.mkdir("data")

        commands.Bot.__init__(self,
                              command_prefix=self.getPrefixes,
                              intents=discord.Intents().all(),
                              help_command=None,
                              activity=discord.Activity(type=discord.ActivityType.listening, name=",help"))

        DataManager.__init__(self,
                             filename="data/data.json",
                             version=data_version
                             )

        # fields
        self.debug = debug
        self.maintenance = maintenance
        self.direct_message = direct_message

        # settings
        self.settings_file = "data/settings.json"
        self.settings = read_json(self.settings_file)
        self.logChannelID = self.settings["log_channel_id"]

        # prepare packages
        self.nsp = NumericStringParser()
        self.imgur = Imgur(self)
        self.ai = AI(self)


    def begin(self):
        self.run(self.settings["discord_token"])

    def getLogChannel(self):
        return self.get_channel(self.settings["log_channel_id"])

    async def setup_hook(self) -> None:
        """ This is called when the bot boots, to set up the global commands """
        await self.tree.sync(guild=None)

    def saveSettings(self) -> bool:
        return save_json(self.settings_file, self.settings)

    def getEmoji(self, name):
        return str(discord.utils.get(self.emojis, name=name))

    def getPrefix(self, ctx):
        return self.data[ctx.server]["prefix"]

    def getPrefixes(self, bot, message) -> str:
        if message.content.startswith("@someone"):
            return "@"
        if message.content.startswith(",setprefix "):
            return ","
        if message.content.startswith(",help"):
            return ","
        if message.content.startswith(",reload"):
            return ","
        return self.data[str(message.guild.id)]["prefix"]
