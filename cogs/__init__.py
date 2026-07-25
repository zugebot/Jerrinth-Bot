import importlib

async def setup(bot):
    cogs = [
        "cogs.main.cog_8ball",
        "cogs.main.cog_admin",
        "cogs.main.cog_channels",
        "cogs.main.cog_findblock",
        "cogs.main.cog_findseed",
        "cogs.main.cog_mobs",
        "cogs.main.cog_help",
        "cogs.main.cog_imgur",
        "cogs.main.cog_leaderboards",
        "cogs.main.cog_math",
        "cogs.main.cog_mudaestats",
        "cogs.main.cog_serverinfo",
        "cogs.main.cog_someone",
        "cogs.main.cog_userinfo",
        "cogs.main.cog_voicechat",
    ]

    for cog in cogs:
        try:
            module = importlib.import_module(cog)  # Dynamically import the cog module
            await module.setup(bot)  # Call the setup function of the cog
        except Exception as e:
            print(f"Failed to load cog {cog}: {e}")