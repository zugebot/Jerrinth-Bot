# Jerrin Shirks
import asyncio
# native imports
import os
from datetime import datetime
# import openai
import signal
from pathlib import Path

# custom imports
from files.support import *
from files.data_manager import DataManager
from files.discord_objects import *
from files.config import *
# from funcs.chatai import CHATAI, Memory

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

        # fields
        self.debug = debug
        self.maintenance = maintenance
        self.direct_message = direct_message

        database_name = "jerrinth_debug.sqlite3" if self.debug else "jerrinth.sqlite3"
        DataManager.__init__(
            self,
            database_path=Path(self.directory) / "data" / database_name,
            version=data_version,
        )

        # self.openai = openai

        # on exit
        self.exiting = False
        signal.signal(signal.SIGINT, self.signal_handler)

        # settings
        self.settings_file = self.directory + "data/settings.json"
        self.settings: dict = read_json(self.settings_file, EMPTY_SETTINGS)
        self.logChannelID = self.settings["channel_log_dm"]

        # openai for whisper
        # self.settings.setdefault("openai_token", None)
        # if self.settings["openai_token"] is not None:
        #     self.openai.api_key = self.settings["openai_token"]

        # Moderation data is stored in the selected production/debug database.
        self.banned_users = self.load_banned_users()
        self.badwords = self.load_badwords()

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

        # ffmpeg
        self.ffmpeg = {
            "Linux": self.directory + "bin/ffmpeg-6.0-i686-static/ffmpeg",
            "Windows": self.directory + "bin/ffmpeg.exe",
        }.get(OS, "")

        # server specific nonsense
        self.hooks_on_raw_reaction_add = {"all": []}
        self.hooks_on_raw_reaction_remove = {"all": []}
        self.hooks_on_member_join = {"all": []}
        self.hooks_on_message = {"all": []}
        self.hooks_on_voice_state_update = {"all": []}
        self.hooks_on_bot_message = {"all": []}
        self.hooks_on_bot_edit_message = {"all": []}

        # other stuff
        self.imgur = Imgur(self)

    def begin(self):
        self.run(self.settings["discord_token"])

    def getLogChannel(self):
        return self.get_channel(self.settings["channel_log_dm"])

    async def setup_hook(self) -> None:
        pass

    def saveSettings(self) -> bool:
        return save_json(self.settings_file, self.settings)

    async def saveBannedUsers(self) -> bool:
        try:
            snapshot = dict(self.banned_users)
            await asyncio.to_thread(self.replace_banned_users, snapshot)
            return True
        except Exception as error:
            print_red(f"Error saving banned users: {error}")
            return False

    def getEmoji(self, name):
        return str(discord.utils.get(self.emojis, name=name))

    def gp(self, ctx):
        server = self.getServer(ctx)
        return server.get("prefix", ",") if server is not None else ","

    def getPrefixes(self, bot, message) -> str:
        if message.content.startswith("@someone"):
            return "@"
        if message.content.startswith(",setprefix "):
            return ","
        if message.content.startswith(",help"):
            return ","
        if message.content.startswith(",reload"):
            return ","
        if message.guild is None:
            return ","
        server = self.getServer(message.guild.id)
        return server.get("prefix", ",") if server is not None else ","

    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        func = self.hooks_on_bot_edit_message.get(after.guild.id, None)
        if callable(func):
            try:
                await func(before, after)
            except Exception as e:
                print(e)

    async def on_member_join(self, member: discord.Member) -> None:
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
        self.getServer(guild.id).pop("not_in_server", None)
        self.saveData()

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
        self.getServer(guild.id)["not_in_server"] = True
        self.saveData()

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

        print("\nLoading cogs...")
        await self.load_extension(f"cogs.cog_utils")
        await self.load_extension(f"cogs.__init__")

        print("\nServer Specific:")
        folders = [entry.name for entry in Path(self.directory + "/cogs").iterdir()
                   if entry.is_dir() and entry.name not in ["__pycache__", "unused", "main"]]

        for folder in folders:
            print(f"Loading all cogs from folder '{folder}':")
            for filename in os.listdir(f"cogs/{folder}"):
                if filename.startswith("cog") and filename.endswith(".py"):
                    extension = f"cogs.{folder}.{filename[:-3]}"
                    await self.load_extension(extension)
                    print(f"loading extension \"{extension}\".")

        if hasattr(self, "_post_cog_load_hook"):
            await self._post_cog_load_hook()

        print("\nStart up successful!")


    def signal_handler(self, signum, frame):
        print("SIGINT: Preparing to shutdown...")

        # cog stuff
        self.exiting = True

        # shut myself off
        loop = asyncio.get_event_loop()
        loop.create_task(self.async_close())

    async def async_close(self):
        await self.close()

    async def close(self):
        # vc: discord.VoiceProtocol
        # for vc in self.voice_clients:
        #     await vc.disconnect(force=True)
        #     print_red(f"SIGINT: voice call: disconnected from {vc.channel.id} ({vc.channel})")
        try:
            await super().close()
        finally:
            await self.close_database()
