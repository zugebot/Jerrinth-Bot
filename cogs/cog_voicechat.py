# Jerrin Shirks

# native imports
import asyncio
import time

import aiohttp
import discord.ext.commands.errors
import yt_dlp as youtube_dl

from files.buttonMenu import ButtonMenu
# custom imports
from files.jerrinth import JerrinthBot
from files.makeTable import makeTable
from files.wrappers import *
from files.support import *
from files.config import *
from files.discord_objects import *


async def download_file(url, file_name):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            with open(file_name, 'wb') as file:
                while True:
                    chunk = await response.content.read(1024)
                    if not chunk:
                        break
                    file.write(chunk)


def wrapper_in_vc():
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(self, ctx, *args, **kwargs):
            if not ctx.author.voice:
                return await ctx.send("You're not in a voice channel.")
            return await func(self, ctx, *args, **kwargs)
        return wrapper
    return decorator


def wrapper_stop_playing():
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(self, ctx, *args, **kwargs):
            vc = await self.joinVC(ctx)
            if vc.is_playing():
                vc.stop()
            return await func(self, ctx, *args, **kwargs)
        return wrapper
    return decorator


def wrapper_play(in_vc: bool = False, stop_playing: bool = False):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(self, ctx, *args, **kwargs):
            if in_vc:
                if not ctx.author.voice:
                    return await ctx.send("You're not in a voice channel.")
            if stop_playing:
                vc = await self.joinVC(ctx)
                if vc.is_playing():
                    vc.stop()
            return await func(self, ctx, *args, **kwargs)
        return wrapper
    return decorator


class VoiceChatCog(commands.Cog):

    def __init__(self, bot):
        self.bot: JerrinthBot = bot
        self.dir: str = bot.directory + "data/mp3/"
        self.ffmpeg = {
            "Linux": bot.directory + "bin/ffmpeg-6.0-i686-static/ffmpeg",
            "Windows": bot.directory + "bin/ffmpeg.exe",
        }.get(OS, "")

        self.video_length_cap_seconds = 900
        self.downloading_urls = []

    def ensureUserExistsPlayRandom(self, ctx):
        self.bot.ensureUserExists(ctx)
        if self.bot.getUser(ctx).get("playrandom", None) is None:
            self.bot.getUser(ctx)["playrandom"] = EMPTY_OBJECT.copy()

    def ensureUserExistsPlay(self, ctx):
        self.bot.ensureUserExists(ctx)
        if self.bot.getUser(ctx).get("play", None) is None:
            self.bot.getUser(ctx)["play"] = EMPTY_OBJECT.copy()

    def getFileList(self):
        return os.listdir(self.dir)

    @staticmethod
    async def joinVC(ctx):
        if ctx.super.voice_client and ctx.super.voice_client.channel == ctx.super.author.voice.channel:
            vc = ctx.super.voice_client
        else:
            try:
                vc = await ctx.super.author.voice.channel.connect()
            except:
                return await ctx.sendError("I wanted to play a song, but you left the voice channel! Hopefully later "
                                           "my developer makes this join regardless.")
        return vc

    @staticmethod
    def getVC(ctx):
        return ctx.super.author.voice.channel.id

    def getVolume(self, ctx):
        return self.bot.getServer(ctx).get("vc_volume", 10) / 100

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if before.channel is None:
            return

        if len(before.channel.members) == 1:
            if before.channel.members[0].bot:
                if before.channel.guild.voice_client is not None:
                    await before.channel.guild.voice_client.disconnect()

    @wrapper_command(name="old_join", cooldown=VOICE_JOIN_CD)
    async def joinCommand(self, ctx):
        try:
            await ctx.super.author.voice.channel.connect()
        except discord.ext.commands.errors.CommandInvokeError:
            return await ctx.sendError("I am already being used in a different channel!")

    @joinCommand.error
    @wrapper_error(use_cooldown=True)
    async def joinCommandError(self, ctx, error):
        pass

    @wrapper_command(name="old_leaveall", user_req=1)
    async def leaveAllCommand(self, ctx):
        [await vc.disconnect(True) for vc in self.bot.voice_clients if not vc.is_playing()]

    @leaveAllCommand.error
    @wrapper_error()
    async def leaveAllCommandError(self, ctx, error):
        pass

    @wrapper_command(name="old_leave", cooldown=VOICE_LEAVE_CD)
    async def leaveCommand(self, ctx):
        await ctx.super.voice_client.disconnect()

    @leaveCommand.error
    @wrapper_error(use_cooldown=True)
    async def leaveCommandError(self, ctx, error):
        pass

    @wrapper_command(name="old_stop", cooldown=VOICE_LEAVE_CD)
    @wrapper_play(in_vc=True, stop_playing=True)
    async def stopCommand(self, ctx):
        pass

    @stopCommand.error
    @wrapper_error(use_cooldown=True)
    async def stopCommandError(self, ctx, error):
        pass

    @wrapper_command(name="old_volume", cooldown=VOICE_LEAVE_CD)
    @wrapper_play(in_vc=True)
    async def volumeCommand(self, ctx, new_volume=None):
        self.bot.ensureServerExists(ctx)

        if new_volume is None:
            embed = newEmbed(f"Current Volume: **{'%.0f' % self.getVolume(ctx)}%**\n"
                             f"\nChange the Volume with"
                             f"\n**{self.bot.gp(ctx)}volume *NEW_VOLUME**")
            return await ctx.send(embed)

        if new_volume.isdigit():
            new_volume = int(new_volume)
            if not (0 <= new_volume <= 200):
                return await ctx.send("Volume must be between 0 and 100.")

            self.bot.getServer(ctx)["vc_volume"] = new_volume
            self.bot.saveData()
            await ctx.sendEmbed(f"Volume has been set to **{'%.0f' % new_volume}%**")

    @stopCommand.error
    @wrapper_error(use_cooldown=True)
    async def volumeCommandError(self, ctx, error):
        pass

    # moving the bot, it can continue playing if the vc object is updated
    async def playAudio(self, ctx, vc, file_name):
        audio = discord.FFmpegPCMAudio(executable=self.ffmpeg, source=file_name)
        source = discord.PCMVolumeTransformer(audio)
        source.volume = self.getVolume(ctx)
        vc.play(source)

        self.bot.ensureServerExists(ctx)

        while vc.is_playing():
            await asyncio.sleep(1)
            new_volume = self.getVolume(ctx)
            if source.volume != new_volume:
                print("changed volume", new_volume)
                source.volume = new_volume

    def getYoutubeVideoOpts(self):
        return {
            'ffmpeg_location': self.bot.directory + "bin/",
            'format': 'bestaudio/best',
            'outtmpl': self.dir + '%(title)s',
            'restrictfilenames': True,  # to avoid issues with filename
            'quiet': True,
            'verbose': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '196',
            }],
        }

    def getYoutubeVideoFilenameNoExt(self, url: str = ""):
        ydl_opts = self.getYoutubeVideoOpts()
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            filename = ydl.prepare_filename(info_dict) + ".mp3"
            return filename.split("\\")[-1]

    def downloadYoutubeVideo(self, url: str = ""):
        ydl_opts = self.getYoutubeVideoOpts()
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            duration = info_dict.get('duration')

            if duration > self.video_length_cap_seconds:
                return 0, duration

            ydl.download([url])

            # Getting the title and cleaning it
            title = info_dict.get('title')
            filename = ydl.prepare_filename(info_dict) + ".mp3"

        return True, filename, title

    @wrapper_command(name="old_play", cooldown=VOICE_PLAY_CD)
    @wrapper_play(in_vc=True)
    async def playCommand(self, ctx, url: str = None):

        if url is None and not ctx.message.attachments:
            return await ctx.sendError("You must provide a URL or upload a file.")

        files = self.getFileList()

        # get from discord file
        # TODO: SHOULD STREAM THIS
        if ctx.message.attachments:
            _file = renameFileToLength(ctx.message.attachments[0].filename, 56)
            file_name = f"{self.dir}/{_file}"
            await ctx.message.attachments[0].save(file_name)
            description = f"Filename: ``{_file}``"

        # get from argument
        elif url is not None:

            # turns a YouTube link into a file if it already exists
            if url.startswith("http") and ("youtu" in url) and ("/" in url):
                index = url.find("&pp")
                if index != -1:
                    url = url[:index]
                index = url.find("?pp")
                if index != -1:
                    url = url[:index]
                index = url.find("?si")
                if index != -1:
                    url = url[:index]
                video_file_name = self.getYoutubeVideoFilenameNoExt(url)
                if video_file_name in files:
                    url = video_file_name

            # escaped_url = url.replace("_", "\\_")

            # if it is a link
            if url.startswith("http"):
                if "youtu" in url and "/" in url:
                    try:
                        if url in self.downloading_urls:
                            return await ctx.sendError(f"I am currently downloading that video! Hold your horses.")
                        loop = asyncio.get_event_loop()
                        self.downloading_urls.append(url)
                        arg1, filename, title = await loop.run_in_executor(None, self.downloadYoutubeVideo, url)
                        self.downloading_urls.remove(url)
                        if arg1 == 0:
                            hours = filename // 3600
                            _min = str(filename // 60).rjust(2, "0")
                            sec = str(int(filename % 60)).rjust(2, "0")
                            return await ctx.sendError(f"Video must be shorter than 30 minutes.\n"
                                                       f"**Video length:** ``{hours}:{_min}:{sec}``")
                        file_name = filename
                        disp_file_name = filename.split("\\")[-1]
                        description = f"Played a youtube video!\n\nFilename: ``{disp_file_name}``\n**{title}**\n{url}"

                    except Exception as err:
                        if url in self.downloading_urls:
                            self.downloading_urls.remove(url)
                        return await ctx.sendError(f"Something went wrong downloading this youtube video.\n"
                                                   f"Error: {err}")
                else:
                    file_name = f'{self.dir}temp.mp3'
                    description = f"Played a link!\n``{url}``"
                    await download_file(url, file_name)

            # it is a filename
            elif url in files:
                _file = renameFileToLength(url, 56)
                file_name = f'{self.dir}{_file}'
                description = f"Played a file by name.\n``{_file}``"
            else:
                return await ctx.sendError("That is not a valid link or previous file.")

        else:
            return await ctx.sendError("Something went wrong...")

        try:
            await ctx.message.delete()
        except:
            ""

        vc = await self.joinVC(ctx)
        if vc.is_playing():
            vc.stop()

        self.ensureUserExistsPlay(ctx)
        updateUsage(self.bot.getUser(ctx)["play"])
        self.bot.saveData()

        prefix = self.bot.gp(ctx)
        await ctx.sendEmbed(f"**{prefix}play** used by <@{ctx.user}>\n{description}")

        await self.playAudio(ctx, vc, file_name)

    @playCommand.error
    @wrapper_error(use_cooldown=True)
    async def playCommandError(self, ctx, error):
        pass

    @wrapper_command(name="old_playrandom", cooldown=VOICE_PLAY_CD)
    @wrapper_play(in_vc=True, stop_playing=True)
    async def playRandomCommand(self, ctx):
        vc = self.joinVC(ctx)

        # pick a random mp3
        files = self.getFileList()
        if len(files) == 0:
            prefix = self.bot.gp(ctx)
            return await ctx.sendError(f"There are no files to play! Consider using {prefix}play to add some.")

        file = random.choice(files)
        file_name = f'{self.dir}{file}'

        self.ensureUserExistsPlayRandom(ctx)
        updateUsage(self.bot.getUser(ctx)["playrandom"])
        self.bot.saveData()

        prefix = self.bot.gp(ctx)
        try:
            await ctx.sendEmbed(description="**{}playrandom** used by <{}>\n**```{}```**"
                                .format(prefix, ctx.user, file))
            await ctx.message.delete()
        except discord.errors.Forbidden:
            pass

        await self.playAudio(ctx, vc, file_name)

    @playRandomCommand.error
    @wrapper_error(use_cooldown=True)
    async def playRandomCommandError(self, ctx, error):
        pass

    @wrapper_command(name="old_playrename")
    async def playRenameCommand(self, ctx, old_file, new_file):
        for char in "/\\*? ":
            if char in new_file:
                return await ctx.sendError(f"You cannot rename the file to include '{char}' characters!")

        files = self.getFileList()
        if len(files) == 0:
            return await ctx.sendError(f"There aren't files to play! Use **{self.bot.gp(ctx)}play** to add some.")

        if old_file not in files:
            return await ctx.sendError(f"That files doesn't seem to exist. Please try again.")

        os.rename(self.dir + old_file, self.dir + new_file)
        await ctx.send(newEmbed("Successfully renamed ```{}``` to ```{}```".format(old_file, new_file)))

    @wrapper_command(name="old_playdelete")
    async def playRenameCommand(self, ctx, file_name):
        for char in "/\\*? ":
            if char in file_name:
                return await ctx.sendError(f"You cannot delete files including the character '{char}'.")

        files = os.listdir(self.dir)
        if len(files) == 0:
            prefix = self.bot.gp(ctx)
            return await ctx.sendError(f"There are no files to delete! Consider using {prefix}play to add some.")

        if file_name not in files:
            return await ctx.sendError(f"That files doesn't seem to exist. Please try again.")

        try:
            os.remove(f"{self.dir}/{file_name}")
            await ctx.send(newEmbed(f"Successfully deleted ```{file_name}```"))
        except:
            return await ctx.sendError(f"Something went wrong. Idk lol")

    @wrapper_command(name="old_playsearch", cooldown=VOICE_SEARCH_CD)
    async def playSearchCommand(self, ctx, filename):
        files = self.getFileList()
        filename = filename.lower()
        files_lower = [i.lower() for i in files]

        found_list = []
        for n, file in enumerate(files_lower):
            if filename in file:
                found_list.append(files[n])

        if len(found_list) == 0:
            return await ctx.sendError(f"No files contain this string: \n``{filename}``")

        length = 10
        file_sections = [found_list[i:i + length] for i in range(0, len(found_list), length)]

        embeds = []
        page_len = len(file_sections)
        number = 1
        for index, section in enumerate(file_sections):
            real_section = []
            for sect in section:
                real_section.append([f"{number}.", sect])
                number += 1
            table = makeTable(real_section, code=[0, 1], direction=1)
            embed = newEmbed(title=f"Page {index + 1}/{page_len}", description=table)
            embeds.append(embed)

        menu = ButtonMenu(embeds, index=0, timeout=180)
        try:
            await menu.send(ctx)
        except discord.errors.Forbidden:
            await ctx.send("Something went wrong with the interaction.")

    @playSearchCommand.error
    @wrapper_error(use_cooldown=True)
    async def playSearchCommandError(self, ctx, error):
        if error == discord.ext.commands.errors.MissingRequiredArgument:
            return await ctx.sendError("You gotta search *something* silly!")

    @wrapper_command(name="old_playlist", cooldown=VOICE_PLAYLIST_COOLDOWN)
    async def playListCommand(self, ctx, length: str = None):

        length = int(length) if length is not None and length.isdigit() else 10
        length = max(10, min(length, 25))

        files = os.listdir(self.dir)

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
            embed = newEmbed(title=f"Page {index + 1}/{page_len}", description=table)
            embeds.append(embed)

        menu = ButtonMenu(embeds, index=0, timeout=180)
        try:
            await menu.send(ctx)
        except discord.errors.Forbidden:
            await ctx.send("Something went wrong with the interaction.")

    @playListCommand.error
    @wrapper_error(use_cooldown=True)
    async def playListCommandError(self, ctx, error):
        pass


async def setup(bot):
    await bot.add_cog(VoiceChatCog(bot))
