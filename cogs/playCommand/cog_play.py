# Jerrin Shirks

# native imports

# custom imports
from files.jerrinth import JerrinthBot
from files.wrappers import *
from files.support import *
from files.makeTable import makeTable
from files.buttonMenu import ButtonMenu

from discord import FFmpegPCMAudio
from typing import Tuple, Dict, List
import aiofiles
import aiohttp
import inspect
import signal
import random
import re
from youtube_search import YoutubeSearch

from discord.ui import Button, View
import discord

from cogs.playCommand.YDL import *


def format_time(seconds):
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    if hours > 0:
        return f"{int(hours)}:{int(minutes):02}:{int(seconds):02}"
    elif minutes >= 10:
        return f"{int(minutes)}:{int(seconds):02}"
    else:
        return f"{int(seconds):02}"


def run_async_callback(loop, callback, *args):
    future = asyncio.run_coroutine_threadsafe(callback(*args), loop)
    return future


def wrapper_play(in_vc: bool = False, stop_playing: bool = False):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(self, ctx, *args, **kwargs):
            if in_vc:
                if not ctx.author.voice:
                    return await ctx.send("You're not in a voice channel.")
            if stop_playing:
                vc = await self.joinAndGetVC(ctx)
                if vc.is_playing():
                    vc.stop()
            return await func(self, ctx, *args, **kwargs)

        return wrapper

    return decorator


class AudioSelectionView(View):
    def __init__(self, parent, ctx, videos):
        super().__init__(timeout=60)
        self.cap = 5
        self.ctx = ctx
        self.videos = videos
        self.parent: PlayCog = parent
        self.message = None
        self.deleted_message = False

        # Add a button for each search result (up to a limit, let's say 10)
        for i in range(len(self.videos[:self.cap])):
            button = Button(label=str(i + 1), custom_id=str(i), style=discord.ButtonStyle.primary)
            button.callback = self.button_callback
            self.add_item(button)

        # Add a cancel button
        cancel_button = Button(label="Cancel", custom_id="cancel", style=discord.ButtonStyle.danger)
        cancel_button.callback = self.button_callback
        self.add_item(cancel_button)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user == self.ctx.super.author

    async def button_callback(self, interaction: discord.Interaction):
        custom_id = interaction.data["custom_id"]

        if custom_id == "cancel":
            await interaction.response.send_message("Search canceled.", ephemeral=True)
            await self.delete_message()
            self.stop()
            return

        index = int(custom_id)
        if 0 <= index < len(self.videos):
            selected_result = self.videos[index]
            string = f"https://youtu.be/{selected_result['id']}"
            await self.delete_message()

            settings = await self.parent.setup_settings(self.ctx, string)
            await self.parent.determine_play_type(settings)
            await self.parent.stream_and_save_audio(self.ctx, settings)
            self.stop()
        else:
            await interaction.response.send_message("Invalid selection.", ephemeral=True)

    async def delete_message(self):
        if self.message is not None and not self.deleted_message:
            try:
                await self.message.delete()
                self.deleted_message = True
            except:
                print_red("failed to delete interaction embed")

    async def on_timeout(self):
        await self.delete_message()
        self.stop()

    async def send_embed(self):
        embed = discord.Embed(title="Search Results", description="Please choose a video from the list below:")

        for i, result in enumerate(self.videos[:self.cap]):

            try:
                view_count = int(result['views'].split(' views')[0].replace(",", ""))
                if view_count > 1_000_000_000:
                    view_count = f"{int(view_count / 1_000_000_000)}B"
                elif view_count > 1_000_000:
                    view_count = f"{int(view_count / 1_000_000)}M"
                elif view_count > 1_000:
                    view_count = f"{int(view_count / 1_000)}K"
            except:
                view_count = "?"

            value = f":clock:``{result['duration']}``    " \
                    f":eye:``{view_count}``    " \
                    f":link:[``link``](https://youtu.be/{result['id']})    " \
                    f":person:``{result['channel']}``"

            title_cap = 56
            title = f"``{result['title'][:title_cap]}``"
            if len(title) > title_cap + 4:
                title += "..."

            embed.add_field(name=f"{i + 1}: {title}", value=value, inline=False)

        self.message = await self.ctx.super.send(embed=embed, view=self, ephemeral=True)


class PlayType:
    NONE = -3

    ERROR_FILENAME_TOO_SHORT = -2

    FILE_NOT_FINISHED_DOWNLOADING = -1
    FILE_DOWNLOADED = 0

    ATTACHMENT_DOWNLOAD = 1

    YT_STREAM_DOWNLOAD = 2
    YT_STREAM_NO_DOWNLOAD = 3
    YT_SEARCH = 4

    @staticmethod
    def toString(_play_type):
        if _play_type == PlayType.ERROR_FILENAME_TOO_SHORT:
            return "ERROR_FILENAME_TOO_SHORT"

        if _play_type == PlayType.FILE_DOWNLOADED:
            return "FILE_DOWNLOADED"
        if _play_type == PlayType.FILE_NOT_FINISHED_DOWNLOADING:
            return "FILE_NOT_FINISHED_DOWNLOADING"

        if _play_type == PlayType.ATTACHMENT_DOWNLOAD:
            return "ATTACHMENT_DOWNLOAD"

        if _play_type == PlayType.YT_STREAM_DOWNLOAD:
            return "YT_STREAM_DOWNLOAD"
        if _play_type == PlayType.YT_STREAM_NO_DOWNLOAD:
            return "YT_STREAM_NO_DOWNLOAD"
        if _play_type == PlayType.YT_SEARCH:
            return "YT_SEARCH"

        return "NONE"

    @staticmethod
    def usesYT(_play_type):
        return _play_type == PlayType.YT_STREAM_DOWNLOAD or _play_type == PlayType.YT_STREAM_NO_DOWNLOAD


class PlayCog(commands.Cog):
    class Strings:
        JOIN_VC_BUT_USER_LEFT = "I wanted to be YOUR DJ!!!!!!@##$@#$@#!!@!, but you left the voice channel! Hopefully later my developer makes this join regardless."
        VIDEO_TOO_LONG = "Video is too long! ({}s > {}s)"
        SKIP_CURRENT_AUDIO = "Skipped the current audio."
        NO_AUDIO_PLAYING = "No audio is currently playing."
        DISCONNECTED_FROM_VC = "Disconnected from the voice channel."
        NOT_CONNECTED_TO_VC = "I'm not connected to a voice channel."
        ERROR_OCCURRED = "@{}: An error occurred: {}"
        ALREADY_DOWNLOADING = "Hold your horses!- I'm still downloading that!"
        DOWNLOAD_NOT_FOUND_WHEN_FINISHED = "my life sucks: download_complete_callback somehow ended on a file that doesn't exist?"
        STREAM_BUT_NO_DOWNLOAD = "Will not download: {} is longer than {}min.\n"
        NOT_DONE_DOWNLOADING = "That file isn't finished downloading yet! Please try a link or a different file."
        NOTHING_TO_GO_OFF_OF = "I would search that up on YT for you, but that isn't enough to go off of!"
        I_COULD_PLAY_NOTHING = "I *could* play nothing, but that's boring."

    def __init__(self, bot):
        self.bot: JerrinthBot = bot
        self.dir: str = bot.directory + "data/mp3/"
        self.file_length_cap = 15 * 60  # 15 minutes
        self.file_size_cap = 25 * (1024 * 1024)  # 25 megabytes

        self.ffmpeg_opts = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn'
        }
        self.ydl = YDL()
        self.current_downloads: Dict[str: str] = {}
        self.waiting_to_rename: Dict[str: str] = {}
        self.music_queue: Dict[str: List[Dict[str: str]]] = {}

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if before.channel is None:
            return

        if len(before.channel.members) == 1:
            if before.channel.members[0].bot:
                if before.channel.guild.voice_client is not None:
                    await before.channel.guild.voice_client.disconnect()

    def ensureUserExistsPlayRandom(self, ctx):
        self.bot.ensureUserExists(ctx)
        if self.bot.getUser(ctx).get("playrandom", None) is None:
            self.bot.getUser(ctx)["playrandom"] = EMPTY_OBJECT.copy()

    def ensureUserExistsPlay(self, ctx):
        self.bot.ensureUserExists(ctx)
        if self.bot.getUser(ctx).get("play", None) is None:
            self.bot.getUser(ctx)["play"] = EMPTY_OBJECT.copy()

    def getVolume(self, ctx):
        return self.bot.getServer(ctx).get("vc_volume", 50)

    async def joinAndGetVC(self, ctx):
        if ctx.super.voice_client and ctx.super.voice_client.channel == ctx.super.author.voice.channel:
            vc = ctx.super.voice_client
        else:
            try:
                vc = await ctx.super.author.voice.channel.connect()
            except Exception as e:
                await ctx.send(self.Strings.JOIN_VC_BUT_USER_LEFT)
                return None
        return vc

    async def monitor_playback(self, vc, ctx, settings, source):
        """Monitor playback and keep the event loop active until the audio finishes."""
        parsed_filename = settings["parsed_filename"]

        try:
            while vc.is_playing():
                new_volume = self.getVolume(ctx)
                if source.volume != new_volume / 100:
                    source.volume = new_volume / 100
                await asyncio.sleep(1)
        except Exception as error:
            print(self.Strings.ERROR_OCCURRED.format("playback_complete_callback", error))
        finally:
            print("Playback complete.")
            if parsed_filename in self.waiting_to_rename:
                if os.path.exists(self.dir + parsed_filename):
                    os.rename(self.dir + parsed_filename, self.dir + self.waiting_to_rename[parsed_filename])
                    del self.waiting_to_rename[parsed_filename]
                    print("Renamed \"{}\" to \"{}\"!")

    async def monitor_download(self, audio_url: str, filename: str):
        """Handle downloading and writing the audio to a file independently."""
        try:
            async with aiofiles.open(self.dir + filename, 'wb') as f:
                async with aiohttp.ClientSession() as session:
                    async with session.get(audio_url) as resp:
                        while True:
                            if self.bot.exiting:
                                break
                            chunk = await resp.content.read(1024)
                            if not chunk:
                                break
                            await f.write(chunk)
            if self.bot.exiting:
                try:
                    os.remove(self.dir + filename)
                    print(f"Deleted partially downloaded file: {filename}")
                except Exception as e:
                    print(f"Error deleting file {filename}: {e}")
        except Exception as e:
            await self.download_complete_callback(filename, e)
        else:
            if not self.bot.exiting:
                await self.download_complete_callback(filename)

    async def download_complete_callback(self, filename, error=None):
        if error:
            print(self.Strings.ERROR_OCCURRED.format("download_complete_callback", error))
        else:
            if filename in self.current_downloads:
                del self.current_downloads[filename]
                print(f"Successfully removed \"{filename}\" from the list of current downloads.")
            else:
                print(self.Strings.DOWNLOAD_NOT_FOUND_WHEN_FINISHED)
            print("Download complete.")

    @staticmethod
    async def setup_settings(ctx, string: str):

        # create the settings
        settings = {"mode": None}
        is_youtube, yt_video, yt_list = extract_youtube_info(string)
        is_spotify, sp_video, sp_list = extract_spotify_info(string)

        if is_spotify:
            settings["mode"] = "spotify"
            settings["url"] = sp_video
            settings["info_dict"] = {}
            return await ctx.send("That is not ready yet!")
        elif is_youtube:
            settings["mode"] = "youtube"
            settings["url"] = yt_video
            if yt_list:
                settings["list"] = yt_list
            settings["info_dict"] = await YDL().getInfoDict(yt_video)
            settings["filename"] = YDL().getFileName(settings["info_dict"])
        elif ctx.message.attachments:
            settings["mode"] = "attachment"
            settings["attachment"] = ctx.message.attachments[0]
            settings["filename"] = settings["attachment"].filename
        else:
            settings["mode"] = "search"
            settings["search"] = string
            settings["filename"] = settings["search"]
        return settings

    async def determine_play_type(self, settings):

        # determine how to play the audio

        parsed_filename = replace_spaces(settings["filename"])[:56]
        settings["parsed_filename"] = parsed_filename
        is_a_yt_url = settings["mode"] == "youtube" and settings["url"] != ""
        file_exists = os.path.exists(self.dir + parsed_filename) and parsed_filename != ""
        is_currently_downloading = parsed_filename in self.current_downloads
        has_attachment = settings["mode"] == "attachment"

        # set up the play type
        if is_a_yt_url and is_currently_downloading:
            settings["play_type"] = PlayType.YT_STREAM_NO_DOWNLOAD
        # stream AND download the audio from YouTube.
        elif is_a_yt_url and not file_exists:
            settings["play_type"] = PlayType.YT_STREAM_DOWNLOAD
            duration = settings["info_dict"].get('duration')
            if duration is None or duration > self.file_length_cap:
                settings["play_type"] = PlayType.YT_STREAM_NO_DOWNLOAD
        # play the file with the associated file name.
        # (is_a_yt_url and not is_currently_downloading) or file_exists
        elif file_exists and is_currently_downloading:
            settings["play_type"] = PlayType.FILE_NOT_FINISHED_DOWNLOADING
        elif file_exists:
            settings["play_type"] = PlayType.FILE_DOWNLOADED
        elif has_attachment:
            settings["play_type"] = PlayType.ATTACHMENT_DOWNLOAD
        elif len(parsed_filename) < 4:
            settings["play_type"] = PlayType.ERROR_FILENAME_TOO_SHORT
        else:
            settings["play_type"] = PlayType.YT_SEARCH

        return settings

    async def stream_and_save_audio(self, ctx, settings: dict):
        vc = await self.joinAndGetVC(ctx)

        if settings['play_type'] != PlayType.YT_SEARCH:
            await ctx.sendDebug(f"PlayType: ``{PlayType.toString(settings['play_type'])}``")

        # these three statements all return early
        if settings["play_type"] == PlayType.FILE_NOT_FINISHED_DOWNLOADING:
            return await ctx.sendError(self.Strings.NOT_DONE_DOWNLOADING)

        elif settings["play_type"] == PlayType.ERROR_FILENAME_TOO_SHORT:
            if len(settings["parsed_filename"]) == 0:
                return await ctx.sendError(self.Strings.I_COULD_PLAY_NOTHING)
            else:
                return await ctx.sendError(self.Strings.NOTHING_TO_GO_OFF_OF)

        elif settings["play_type"] == PlayType.YT_SEARCH:
            message = await ctx.sendEmbed(
                "I couldn't find that in my storage, let me search that on YT for you!")

            results = YoutubeSearch(settings["filename"], max_results=10).to_dict()
            try:
                await message.delete()
            except:
                pass
            if len(results) == 0:
                return await ctx.send("I couldn't find anything with that! Try simplifying your search.")
            view = AudioSelectionView(self, ctx, results)
            return await view.send_embed()

        # these all call vc.play and whatnot
        if settings["play_type"] == PlayType.FILE_DOWNLOADED:
            download_file = False
            download_url = ""
            play_filepath = self.dir + settings["parsed_filename"]

            description = f"Playing cached file:\n``{settings['parsed_filename']}``"
            audio = FFmpegPCMAudio(play_filepath)


        elif settings["play_type"] == PlayType.ATTACHMENT_DOWNLOAD:
            attachment = settings["attachment"]
            download_file = attachment.size < self.file_size_cap
            download_url = attachment.url

            if attachment.filename in self.current_downloads:
                download_file = False

            description = f"Playing attachment:\n``{attachment.filename}``"
            audio = FFmpegPCMAudio(download_url, **self.ffmpeg_opts)


        elif settings["play_type"] == PlayType.YT_STREAM_NO_DOWNLOAD:
            info_dict = settings["info_dict"]
            download_file = False
            download_url = info_dict['url']

            duration = info_dict.get('duration')

            description = f"Played a youtube video!" \
                          f"Video is too long to download." \
                          f"\nurl: {settings['url']}"
            audio = FFmpegPCMAudio(download_url, **self.ffmpeg_opts)


        elif settings["play_type"] == PlayType.YT_STREAM_DOWNLOAD:
            info_dict = settings["info_dict"]
            download_file = True
            download_url = info_dict['url']

            description = f"Played a youtube video!" \
                          f"\n\nFilename:\n``{settings['parsed_filename']}``" \
                          f"\n[**{info_dict['title']}**]({settings['url']})"
            audio = FFmpegPCMAudio(download_url, **self.ffmpeg_opts)
        else:
            return

        # play the audio source
        await ctx.sendEmbed(
            f"**{self.bot.gp(ctx)}play** used by <@{ctx.user}>\n{description}")
        source = discord.PCMVolumeTransformer(audio)
        vc.play(source)
        if not download_file:
            await self.monitor_playback(vc, ctx, settings, source)
        else:
            self.current_downloads[settings["parsed_filename"]] = True
            await asyncio.gather(
                self.monitor_download(download_url, settings["parsed_filename"]),
                self.monitor_playback(vc, ctx, settings, source))

    async def playAudio(self, ctx, string: str = "", force: bool = None):
        vc = await self.joinAndGetVC(ctx)
        if vc.is_playing():
            vc.stop()

        settings = await self.setup_settings(ctx, string)
        await self.determine_play_type(settings)
        if settings is None: return

        await self.stream_and_save_audio(ctx, settings)

    @wrapper_command(name="current_downloads")
    async def current_downloads(self, ctx):
        string = "```" + "\n".join([i for i in self.current_downloads]) + "```"
        await ctx.send(string)

    @wrapper_command(name="play")
    @wrapper_play(in_vc=True)
    async def play(self, ctx, *, string: str = ""):
        self.ensureUserExistsPlay(ctx)
        updateUsage(self.bot.getUser(ctx)["play"])
        self.bot.saveData()

        await self.playAudio(ctx, string)

    @wrapper_command(name="playskip")
    @wrapper_play(in_vc=True)
    async def skip(self, ctx):
        """Command to skip the currently playing audio."""
        if ctx.super.voice_client and ctx.super.voice_client.is_playing():
            ctx.super.voice_client.stop()
            await ctx.send(self.Strings.SKIP_CURRENT_AUDIO)
        else:
            await ctx.send(self.Strings.NO_AUDIO_PLAYING)

    @wrapper_command(name="playstop")
    @wrapper_play(in_vc=True)
    async def stop(self, ctx):
        """Command to stop playing and disconnect the bot."""
        if ctx.super.voice_client:
            await ctx.super.voice_client.disconnect()
            await ctx.send(self.Strings.DISCONNECTED_FROM_VC)
        else:
            await ctx.send(self.Strings.NOT_CONNECTED_TO_VC)

    @wrapper_command(name="playrandom")
    @wrapper_play(in_vc=True)
    async def playrandom(self, ctx):
        self.ensureUserExistsPlayRandom(ctx)
        updateUsage(self.bot.getUser(ctx)["playrandom"])
        self.bot.saveData()

        filename = random.choice(os.listdir(self.dir))
        await self.playAudio(ctx, filename)

    @wrapper_command(name="playrename")
    async def playRename(self, ctx, oldName: str, newName: str):
        if oldName == "" or newName == "":
            return await ctx.send("You must supply the before and after file names.")

        old_path = os.path.join(self.dir, oldName)

        if not os.path.exists(old_path):
            return await ctx.send("That file doesn't seem to exist.")

        # Get the file extension of the old file
        old_ext = os.path.splitext(oldName)[1]

        # Remove any incorrect extension from the new name
        new_base = os.path.splitext(newName)[0]

        # Append the correct extension
        newName = new_base + old_ext

        new_path = os.path.join(self.dir, newName)

        try:
            os.rename(old_path, new_path)
            await ctx.send(f"Renamed ``{oldName}`` to ``{newName}``!")
        except Exception as e:
            self.waiting_to_rename[oldName] = newName
            print(self.waiting_to_rename)
            await ctx.send(f"Should rename ``{oldName}`` to ``{newName}`` when it's finished playing.")

    @wrapper_command(name="playdelete")
    async def playRenameCommand(self, ctx, filename: str):
        for char in "/\\*? ":
            if char in filename:
                return await ctx.sendError(f"You cannot delete files including the character '{char}'.")

        files = os.listdir(self.dir)
        if len(files) == 0:
            prefix = self.bot.gp(ctx)
            return await ctx.sendError(f"There are no files to delete! Consider using {prefix}play to add some.")

        if filename not in files:
            return await ctx.sendError(f"That files doesn't seem to exist. Please try again.")

        try:
            os.remove(f"{self.dir}/{filename}")
            await ctx.send(newEmbed(f"Successfully deleted ```{filename}```"))
        except:
            return await ctx.sendError(f"Something went wrong. Idk lol")

    @wrapper_command(name="playvolume")
    @wrapper_play(in_vc=True)
    async def playVolume(self, ctx, value=None):
        if value is None:
            embed = newEmbed(f"Current Volume: **{'%.0f' % self.getVolume(ctx)}%**\n"
                             f"\nChange the Volume with"
                             f"\n**{self.bot.gp(ctx)}volume *NEW_VOLUME**")
            return await ctx.send(embed)

        self.bot.ensureServerExists(ctx)
        new_volume = int(value)

        self.bot.getServer(ctx)["vc_volume"] = new_volume
        self.bot.saveData()

    @wrapper_command(name="playlist")
    async def playList(self, ctx, search: str = None):
        length = 20

        files = os.listdir(self.dir)
        files = [i.lower() for i in files]
        if search is not None:
            search = search.lower()
            files = [i for i in files if search in i]

        file_sections = [files[i:i + length] for i in range(0, len(files), length)]

        embeds = []
        page_len = len(file_sections)
        number = 1
        for index, section in enumerate(file_sections):
            real_section = []
            for sect in section:
                real_section.append([f"{number}.", sect])
                number += 1
            table = makeTable(real_section, code=[0, 1], direction=1)
            pager = f" {index + 1}/{page_len}"
            title = [f"Play{pager}", f"Search{pager}"][search is not None]
            embed = newEmbed(title=title, description=table)
            embeds.append(embed)

        menu = ButtonMenu(embeds, index=0, timeout=180)
        try:
            await menu.send(ctx)
        except discord.errors.Forbidden:
            await ctx.send("Something went wrong with the interaction.")

    @wrapper_command(name="playleave")
    @wrapper_play(in_vc=True)
    async def leaveCommand(self, ctx):
        await ctx.super.voice_client.disconnect()

    @wrapper_command(name="playjoin")
    async def joinCommand(self, ctx):
        try:
            await ctx.super.author.voice.channel.connect()
        except discord.ext.commands.errors.CommandInvokeError:
            return await ctx.sendError("I am already being used in a different channel!")


async def setup(bot):
    await bot.add_cog(PlayCog(bot))
