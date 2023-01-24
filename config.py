
from discord.ext import commands

DEBUG = True
DIRECT_MESSAGES = False
MAINTENANCE = False


AI_COOLDOWN = (1, 3, commands.BucketType.user)
SOLVE_COOLDOWN = (1, 2, commands.BucketType.user)
FINDIMG_COOLDOWN = (1, 2, commands.BucketType.guild)
FINDSEED_COOLDOWN = (2, 45, commands.BucketType.user)
SOMEONE_COOLDOWN = (1, 90, commands.BucketType.guild)
LEADERBOARD_COOLDOWN = (1, 60, commands.BucketType.guild)
