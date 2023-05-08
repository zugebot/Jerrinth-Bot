
from discord.ext import commands

DEBUG = False
DIRECT_MESSAGES = True
MAINTENANCE = False
OS = "Windows"

DAILY_REFRESH_GLOBAL_COOLDOWN = (1, 600, commands.BucketType.guild)

AI_COOLDOWN = (1, 2, commands.BucketType.user)
CHAT_COOLDOWN = (1, 2, commands.BucketType.user)
SOLVE_COOLDOWN = (1, 2, commands.BucketType.user)
WHISPER_COOLDOWN = (1, 10, commands.BucketType.user)
FINDIMG_COOLDOWN = (1, 2, commands.BucketType.guild)
FINDSEED_COOLDOWN = (1, 30, commands.BucketType.user)
SOMEONE_COOLDOWN = (1, 90, commands.BucketType.guild)
LEADERBOARD_COOLDOWN = (1, 30, commands.BucketType.guild)

VOICE_JOIN_COOLDOWN = (1, 2, commands.BucketType.guild)
VOICE_LEAVE_COOLDOWN = (1, 2, commands.BucketType.guild)
VOICE_PLAY_COOLDOWN = (1, 2, commands.BucketType.guild)
VOICE_QUICK_COOLDOWN = (1, 1, commands.BucketType.guild)
VOICE_PLAYLIST_COOLDOWN = (1, 15, commands.BucketType.guild)

WHISPER_MAX_FILE_SIZE = 25_000_000 # MB


