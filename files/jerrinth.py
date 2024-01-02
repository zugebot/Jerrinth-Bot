# Jerrin Shirks
import asyncio
# native imports
import os
from datetime import datetime

# custom imports
from files.support import *
from files.data_manager import DataManager
from funcs.chatai import CHATAI, Memory
from funcs.imgur import Imgur


class JerrinthBot(commands.Bot, DataManager):

    def __init__(self, data_version: int,
                 debug: bool = False,
                 maintenance: bool = False,
                 direct_message: bool = True) -> None:

        if not os.path.isdir("data"):
            os.mkdir("data")

        script_path = os.path.abspath(__file__)
        self.directory = os.path.dirname(os.path.dirname(script_path)).replace("\\", "/") + "/"

        commands.Bot.__init__(
            self,
            command_prefix=self.getPrefixes,
            intents=discord.Intents().all(),
            help_command=None,
            activity=discord.Activity(type=discord.ActivityType.listening, name=",help")
        )

        DataManager.__init__(self,
                             filename=self.directory + "data/data.json",
                             version=data_version
                             )

        # fields
        self.debug = debug
        self.maintenance = maintenance
        self.direct_message = direct_message

        # settings
        self.settings_file = self.directory + "data/settings.json"
        self.settings = read_json(self.settings_file, EMPTY_SETTINGS)
        self.logChannelID = self.settings["channel_log_dm"]

        # banned
        self.banned_users_file = self.directory + "data/banned.json"
        self.banned_users = read_json(self.banned_users_file)

        self.badwords_file = self.directory + "data/badwords.json"
        self.badwords = read_json(self.badwords_file)["badwords"]

        # custom prompts
        self.ai_prompts = os.listdir(self.directory + "data/prompts")
        print("List of prompts:", ", ".join(self.ai_prompts))
        self.ai_prompt_dict = {}
        for file in os.listdir(self.directory + f"data/prompts"):
            key = file.split(".")[0]
            with open(self.directory + f"data/prompts/{file}", "r", encoding='utf-8') as f:
                self.ai_prompt_dict[key] = f.read()

        # ensure settings are good
        if self.settings["discord_token"] is None:
            raise Exception("No discord token found in ~/data/settings.json.")

        # server specific nonsense
        self.hooks_on_raw_reaction_add = {}
        self.hooks_on_raw_reaction_remove = {}
        self.hooks_on_member_join = {}
        self.hooks_on_message = {}

        # other stuff
        self.imgur = Imgur(self)

    def begin(self):
        self.run(self.settings["discord_token"])

    def getLogChannel(self):
        return self.get_channel(self.settings["channel_log_dm"])

    async def setup_hook(self) -> None:
        """ This is called when the bot boots, to set up the global commands """
        await self.tree.sync(guild=None)

    def saveSettings(self) -> bool:
        return save_json(self.settings_file, self.settings)

    def saveBannedUsers(self) -> bool:
        return save_json(self.banned_users_file, self.banned_users)

    def getEmoji(self, name):
        return str(discord.utils.get(self.emojis, name=name))

    def getPrefix(self, ctx):
        return self.data["servers"][ctx.server]["prefix"]

    def getPrefixes(self, bot, message) -> str:
        if message.content.startswith("@someone"):
            return "@"
        if message.content.startswith(",setprefix "):
            return ","
        if message.content.startswith(",help"):
            return ","
        if message.content.startswith(",reload"):
            return ","
        return self.data["servers"][str(message.guild.id)]["prefix"]

    async def on_member_join(self, member) -> None:
        if member.guild.id is None:
            return

        func = self.hooks_on_member_join.get(member.guild.id, None)
        if callable(func):
            await func(member)

    async def on_raw_reaction_add(self, payload):
        if payload.guild_id is None:
            return

        func = self.hooks_on_raw_reaction_add.get(payload.guild_id, None)
        if callable(func):
            await func(payload)

    async def on_raw_reaction_remove(self, payload):
        if payload.guild_id is None:
            return

        func = self.hooks_on_raw_reaction_remove.get(payload.guild_id, None)
        if callable(func):
            await func(payload)

    async def on_guild_join(self, guild: discord.Guild):
        private_log = self.get_channel(self.settings["channel_log_private"])
        self.ensureServerExists(guild.id, guild.name)
        self.getServer(guild.id).pop("presence", None)

        embed = newEmbed()
        if guild.icon is not None:
            embed.set_thumbnail(url=guild.icon.url)

        embed.add_field(name="Joined a server!",
                        inline=False,
                        value=f"Name: **{guild.name}**"
                              f"\nMember Count: **{guild.member_count}**"
                              f"\nChannel Count: **{len(guild.channels)}**"
                              f"\nCreated On: <t:{int(datetime.timestamp(guild.created_at))}>"
                        )
        await private_log.send(embed=embed)

    async def on_guild_remove(self, guild: discord.Guild):
        await self.wait_until_ready()
        private_log = self.get_channel(self.settings["channel_log_private"])
        self.ensureServerExists(guild.id, guild.name)
        self.getServer(guild.id)["presence"] = False

        embed = newEmbed(color=discord.Color.blue())

        embed.add_field(name="I was removed from a server...",
                        inline=False,
                        value=f"Name: **{guild.name}**"
                              f"\nMember Count: **{guild.member_count}**"
                              f"\nChannel Count: **{len(guild.channels)}**"
                        )
        await private_log.send(embed=embed)

    async def on_ready(self) -> None:
        """
        Loads all cogs, and prints startup message to console.
        Prepares the Imgur library.
        """
        await self.imgur.loadRandomImages()

        print("\nCogs:")
        for filename in os.listdir(self.directory + "cogs"):
            if filename.endswith(".py"):
                await self.load_extension(f"cogs.{filename[:-3]}")
                print(f"loaded cogs.{filename[:-3]}")

        print("\nServer Specific:")
        for filename in os.listdir(self.directory + "cogs/servers"):
            if filename.endswith(".py"):
                await self.load_extension(f"cogs.servers.{filename[:-3]}")
                print(f"loaded cogs.servers.{filename[:-3]}")

        print("\nStart up successful!")
