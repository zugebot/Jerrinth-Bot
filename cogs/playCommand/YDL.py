
import yt_dlp as youtube_dl
import asyncio
import re
from typing import Tuple


def extract_youtube_info(url):
    pattern = r'(?:https?://)?(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]{11})(?:&list=([a-zA-Z0-9_-]+))?'
    match = re.search(pattern, url)

    if match:
        video_id = match.group(1)
        if video_id is not None:
            video_id = f"https://youtu.be/{video_id}"
        playlist_id = match.group(2) if match.group(2) else None
        return True, video_id, playlist_id
    else:
        return False, None, None


def extract_spotify_info(url):
    return False, "", ""

    match = re.search(r'(?:https?://)?(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]{11})', url)
    if match:
        video_id = match.group(1)
        return True, "", f"https://youtu.be/{video_id}"
    else:
        return False, "", "",


def replace_spaces(string, replacement="_"):
    return "".join([i if i != " " else replacement for i in string])


class YDL:
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'verbose': False,
        'default_search': 'auto',
        'source_address': '0.0.0.0',  # Bind to ipv4 since ipv6 addresses suck
        'outtmpl': '%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'postprocessor_args': [
            '-ar', '44100'
        ],
        'prefer_ffmpeg': True,
        'keepvideo': False,
        'playlistend': 5,  # Limit to first 10 results, increase this for more results
    }

    @staticmethod
    async def getInfoDict(url) -> dict:
        loop = asyncio.get_event_loop()
        with youtube_dl.YoutubeDL(YDL.ydl_opts) as ydl:
            info_dict = await loop.run_in_executor(None, ydl.extract_info, url, False)
        return info_dict

    @staticmethod
    def getFileName(info_dict: dict):
        assert isinstance(info_dict, dict)
        with youtube_dl.YoutubeDL(YDL.ydl_opts) as ydl:
            filename = ydl.prepare_filename(info_dict)\
                .replace("/", "") \
                .replace("\\", "") \
                .replace("*", "") \
                .replace("?", "")
        filename = replace_spaces(filename)
        return filename

