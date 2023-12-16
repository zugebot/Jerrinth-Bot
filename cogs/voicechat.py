# Jerrin Shirks

# native imports
import asyncio
import time

import aiohttp
import discord.ext.commands.errors
import yt_dlp as youtube_dl

# custom imports
from files.jerrinth import JerrinthBot
from files.wrappers import *
from files.support import *
from files.config import *


async def download_file(url, file_name):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            with open(file_name, 'wb') as file:
                while True:
                    chunk = await response.content.read(1024)
                    if not chunk:
                        break
                    file.write(chunk)


class VoiceChatCog(commands.Cog):
    def __init__(self, bot):
        self.bot: JerrinthBot = bot
        self.dir: str = bot.directory + "data/mp3/"

        self.video_length_cap_seconds = 900
        self.downloading_urls = []

        if OS == "Linux":
            self.ffmpeg: str = bot.directory + "bin/ffmpeg-6.0-i686-static/ffmpeg"
        elif OS == "Windows":
            self.ffmpeg: str = bot.directory + "bin/ffmpeg.exe"
        else:
            self.ffmpeg: str = ""

    def ensureUserVCExists(self, ctx):
        self.bot.ensureUserExists(ctx)
        if self.bot.getUser(ctx).get("playrandom", None) is None:
            self.bot.getUser(ctx)["playrandom"] = EMPTY_PLAYRANDOM.copy()
        if self.bot.getUser(ctx).get("play", None) is None:
            self.bot.getUser(ctx)["play"] = EMPTY_OBJECT.copy()

    @staticmethod
    async def joinVC(ctx):
        if ctx.super.voice_client and ctx.super.voice_client.channel == ctx.super.author.voice.channel:
            vc = ctx.super.voice_client
        else:
            vc = await ctx.super.author.voice.channel.connect()
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

    @commands.command(name="join")
    @discord.ext.commands.cooldown(*VOICE_JOIN_COOLDOWN)
    @ctx_wrapper
    @channel_redirect
    async def joinCommand(self, ctx):
        try:
            await ctx.super.author.voice.channel.connect()
        except discord.ext.commands.errors.CommandInvokeError:
            return await ctx.sendError("I am already being used in a different channel!")

    @joinCommand.error
    @ctx_wrapper
    @cool_down_error
    async def joinCommandError(self, ctx, error):
        pass

    @commands.command(name="leaveall")
    @ctx_wrapper
    @is_jerrin
    async def leaveAllCommand(self, ctx):
        [await vc.disconnect(True) for vc in self.bot.voice_clients if not vc.is_playing()]

    @leaveAllCommand.error
    @ctx_wrapper
    async def leaveAllCommandError(self, ctx, error):
        pass

    @commands.command(name="leave")
    @discord.ext.commands.cooldown(*VOICE_LEAVE_COOLDOWN)
    @ctx_wrapper
    @channel_redirect
    async def leaveCommand(self, ctx):
        await ctx.super.voice_client.disconnect()

    @leaveCommand.error
    @ctx_wrapper
    @cool_down_error
    async def leaveCommandError(self, ctx, error):
        pass

    @commands.command(name="stop")
    @discord.ext.commands.cooldown(*VOICE_LEAVE_COOLDOWN)
    @ctx_wrapper
    @channel_redirect
    async def stopCommand(self, ctx):
        vc = await self.joinVC(ctx)
        if vc.is_playing():
            vc.stop()

    @stopCommand.error
    @ctx_wrapper
    @cool_down_error
    async def stopCommandError(self, ctx, error):
        pass

    @commands.command(name="meow")
    @discord.ext.commands.cooldown(*VOICE_QUICK_COOLDOWN)
    @ctx_wrapper
    @channel_redirect
    async def meowCommand(self, ctx):
        if not ctx.author.voice:
            return await ctx.send("You're not in a voice channel.")

        vc = await self.joinVC(ctx)
        if vc.is_playing():
            vc.stop()

        # Play the MP3 file
        audio = discord.FFmpegPCMAudio(executable=self.ffmpeg, source=f'{self.dir}meow.mp3')
        source = discord.PCMVolumeTransformer(audio)
        source.volume = 0.05
        vc.play(source)
        while vc.is_playing():
            await asyncio.sleep(1)

    @meowCommand.error
    @ctx_wrapper
    @cool_down_error
    async def meowCommandError(self, ctx, error):
        pass

    @commands.command(name="volume")
    @discord.ext.commands.cooldown(*VOICE_LEAVE_COOLDOWN)
    @ctx_wrapper
    @channel_redirect
    async def volumeCommand(self, ctx, new_volume=None):
        if not ctx.super.author.voice:
            return await ctx.send("You're not in a voice channel.")
        self.bot.ensureServerExists(ctx)

        if new_volume is None:
            prefix = self.bot.getPrefix(ctx)
            volume = self.getVolume(ctx)
            embed = newEmbed(f"Current Volume: **{'%.0f' % volume}%**"
                             f"\n"
                             f"\nChange the Volume with"
                             f"\n**{prefix}volume *NEW_VOLUME**")
            return await ctx.send(embed)

        if new_volume.isdigit():
            new_volume = int(new_volume)
            if not (0 <= new_volume <= 100):
                return await ctx.send("Volume must be between 0 and 100.")

            self.bot.getServer(ctx)["vc_volume"] = new_volume
            self.bot.saveData()
            await ctx.sendEmbed(f"Volume has been set to **{'%.0f' % new_volume}%**")

    @stopCommand.error
    @ctx_wrapper
    @cool_down_error
    async def volumeCommandError(self, ctx, error):
        pass

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

    def getYoutubeVideoOpts(self, url: str = ""):
        ydl_opts = {
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
        return ydl_opts

    def getYoutubeVideoFilenameNoExt(self, url: str = ""):
        ydl_opts = self.getYoutubeVideoOpts(url)
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            filename = ydl.prepare_filename(info_dict) + ".mp3"
            return filename.split("\\")[-1]

    def downloadYoutubeVideo(self, url: str = ""):
        ydl_opts = self.getYoutubeVideoOpts(url)
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

    @commands.command(name="play")
    @discord.ext.commands.cooldown(*VOICE_PLAY_COOLDOWN)
    @ctx_wrapper
    @channel_redirect
    async def playCommand(self, ctx, url: str = None):
        if not ctx.author.voice:
            return await ctx.send("You're not in a voice channel.")
        if url is None and not ctx.message.attachments:
            return await ctx.sendError("You must provide a URL.")

        files = os.listdir(self.dir)

        # get from discord file
        if ctx.message.attachments:
            _file = renameFileToLength(ctx.message.attachments[0].filename, 56)
            file_name = f"{self.dir}/{_file}"
            await ctx.message.attachments[0].save(file_name)
            description = f"Filename: ``{_file}``"

        # get from argument
        elif url is not None:

            # turns a YouTube link into a file if it already exists
            if url.startswith("http") and ("youtu" in url) and ("/" in url):
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
                            min = str(filename // 60).rjust(2, "0")
                            sec = str(int(filename % 60)).rjust(2, "0")
                            return await ctx.sendError(f"Video must be shorter than 30 minutes.\n"
                                                       f"**Video length:** ``{hours}:{min}:{sec}``")
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

            # if it is an index
            elif url.isdigit():
                url = int(url)
                if url > len(files):
                    return await ctx.sendError(f"Please specify a song index below {len(files)}")
                file_name = f"{self.dir}/{files[url]}"
                description = f"Played a file at index {url}.\n``{files[url]}``"

            # it is a filename
            elif url in files:
                _file = renameFileToLength(url, 56)
                file_name = f'{self.dir}{_file}'
                description = f"Played a file.\n``{_file}``"
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

        self.ensureUserVCExists(ctx)
        user = self.bot.getUser(ctx)["play"]
        user["total_uses"] += 1
        user["last_use"] = time.time()
        self.bot.saveData()

        prefix = self.bot.getPrefix(ctx)
        await ctx.sendEmbed(f"**{prefix}play** used by <@{ctx.user}>\n{description}")

        await self.playAudio(ctx, vc, file_name)

    @playCommand.error
    @ctx_wrapper
    @cool_down_error
    async def playCommandError(self, ctx, error):
        pass

    @commands.command(name="playrandom")
    @discord.ext.commands.cooldown(*VOICE_PLAY_COOLDOWN)
    @ctx_wrapper
    @channel_redirect
    async def playRandomCommand(self, ctx):
        if not ctx.author.voice:
            return await ctx.send("You're not in a voice channel.")

        vc = await self.joinVC(ctx)
        if vc.is_playing():
            vc.stop()

        # pick a random mp3
        files = os.listdir(self.dir)
        if len(files) == 0:
            prefix = self.bot.getPrefix(ctx)
            return await ctx.sendError(f"There are no files to play! Consider using {prefix}play to add some.")

        file = random.choice(files)
        file_name = f'{self.dir}{file}'

        self.ensureUserVCExists(ctx)
        user = self.bot.getUser(ctx)["playrandom"]
        user["total_uses"] += 1
        user["last_use"] = time.time()
        self.bot.saveData()

        prefix = self.bot.getPrefix(ctx)
        await ctx.sendEmbed(description=f"**{prefix}playrandom** used by <@{ctx.user}>\n"
                                        f"**```{file}```**")
        await ctx.message.delete()

        await self.playAudio(ctx, vc, file_name)

    @playRandomCommand.error
    @ctx_wrapper
    @cool_down_error
    @channel_redirect
    async def playRandomCommandError(self, ctx, error):
        pass

    @commands.command(name="playrename")
    @ctx_wrapper
    @channel_redirect
    async def playRenameCommand(self, ctx, old_file, new_file):
        for char in "/\\*? ":
            if char in new_file:
                return await ctx.sendError(f"You cannot rename the file to include '{char}' characters!")

        files = os.listdir(self.dir)
        if len(files) == 0:
            prefix = self.bot.getPrefix(ctx)
            return await ctx.sendError(f"There are no files to play! Consider using {prefix}play to add some.")

        if old_file not in files:
            print(old_file)
            return await ctx.sendError(f"That files doesn't seem to exist. Please try again.")

        os.rename(self.dir + old_file, self.dir + new_file)
        await ctx.send(newEmbed(f"Successfully renamed ```{old_file}``` to ```{new_file}```"))

    @commands.command(name="playsearch")
    @discord.ext.commands.cooldown(*VOICE_SEARCH_COOLDOWN)
    @ctx_wrapper
    @channel_redirect
    async def playSearchCommand(self, ctx, filename):
        files = os.listdir(self.dir)
        filename = filename.lower()
        files_lower = [i.lower() for i in files]

        found_list = []
        for n, file in enumerate(files_lower):
            if filename in file:
                found_list.append(files[n])

        # exceeds_amount = len(found_list) > 50
        # if exceeds_amount:
        #     found_list = found_list[:100]

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
            table = makeTable(real_section,
                              code=[0, 1],
                              direction=1
                              )
            embed = newEmbed(title=f"Page {index + 1}/{page_len}", description=table)
            embeds.append(embed)

        menu = ButtonMenu(embeds, index=0, timeout=180)
        try:
            await menu.send(ctx)
        except discord.errors.Forbidden:
            await ctx.send("Something went wrong with the interaction.")

    @playSearchCommand.error
    @ctx_wrapper
    @cool_down_error
    @channel_redirect
    async def playSearchCommandError(self, ctx, error):
        if error == discord.ext.commands.errors.MissingRequiredArgument:
            return await ctx.sendError("You gotta search *something* silly!")

    @commands.command(name="playping")
    @discord.ext.commands.cooldown(*VOICE_QUICK_COOLDOWN)
    @ctx_wrapper
    @channel_redirect
    async def playPingCommand(self, ctx):
        if not ctx.author.voice:
            return await ctx.send("You're not in a voice channel.")

        vc = await self.joinVC(ctx)
        if vc.is_playing():
            vc.stop()

        # pick a random mp3
        file_name = f'{self.dir}ping.mp3'
        await self.playAudio(ctx, vc, file_name)

    @playPingCommand.error
    @ctx_wrapper
    @cool_down_error
    async def playPingCommandError(self, ctx, error):
        pass

    @commands.command(name="playlist")
    @discord.ext.commands.cooldown(*VOICE_PLAYLIST_COOLDOWN)
    @ctx_wrapper
    @channel_redirect
    async def playListCommand(self, ctx, length: str = None):
        if not ctx.author.voice:
            return await ctx.send("You're not in a voice channel.")

        if length is not None:
            if length.isdigit():
                length = int(length)
        if length is None:
            length = 10

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
            table = makeTable(real_section,
                              code=[0, 1],
                              direction=1
                              )
            embed = newEmbed(title=f"Page {index + 1}/{page_len}", description=table)
            embeds.append(embed)

        menu = ButtonMenu(embeds, index=0, timeout=180)
        try:
            await menu.send(ctx)
        except discord.errors.Forbidden:
            await ctx.send("Something went wrong with the interaction.")

    @playListCommand.error
    @ctx_wrapper
    @cool_down_error
    async def playListCommandError(self, ctx, error):
        pass


async def setup(bot):
    await bot.add_cog(VoiceChatCog(bot))
