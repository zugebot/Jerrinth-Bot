# Jerrin Shirks

import os

if __name__ == "__main__":
    files = [
        "cogs/admin.py",
        "cogs/ai.py",
        "cogs/channels.py",
        "cogs/cog_utils.py",
        "cogs/fun.py",
        "cogs/handle_dms.py",
        "cogs/help.py",
        "cogs/imgur.py_",
        "cogs/leaderboards.py",
        "cogs/serverinfo.py",
        "cogs/userinfo.py",
        "cogs/voicechat.py",
        "cogs/whisper.py",

        "funcs/ai.py",
        "funcs/handle_dms.py",
        "funcs/imgur.py",
        "funcs/nsp.py",
        "funcs/moderation.py",

        "files/data_manager.py",
        "files/jerrinth.py",
        "main.py",
        "files/support.py",
        "files/wrappers.py",
    ]

    lines = 0
    size = 0
    directory = ("\\".join(__file__.split("\\")[:-2]) + "\\").replace("\\", "/")
    for file in files:
        file = directory + file
        lines_to_add = [i for i in open(file, "r", encoding="utf-8").readlines() if i != "\n"]
        lines += len(lines_to_add)
        size += os.path.getsize(file)

    print(f"line count: {lines}")
    print(f"file bytes: {size}")
    input()
