# Jerrin Shirks
# native imports
from discord import Interaction
from discord.ext import tasks
from discord.ext.commands import CommandNotFound, CommandOnCooldown
import datetime
import random
import logging
from files.wrappers import *

logging.basicConfig(level=logging.CRITICAL)

# custom imports
from files.jerrinth import JerrinthBot
from funcs.handle_dms import *
from files.support import *
from files.config import *

Jerrinth = JerrinthBot(data_version=1,
                       debug=DEBUG,
                       maintenance=MAINTENANCE,
                       direct_message=DIRECT_MESSAGES)


@Jerrinth.event
async def on_guild_join(guild: discord.Guild):
    private_log = Jerrinth.get_channel(Jerrinth.settings["channel_private"])
    Jerrinth.ensureServerExists(guild.id, guild.name)
    Jerrinth.getServer(guild.id).pop("presence", None)

    # if it is the first server, save the server to the settings
    if len(Jerrinth.guilds) == 1:
        Jerrinth.settings["server_main"] = guild.id
        Jerrinth.saveSettings()

    embed = newEmbed()
    if guild.icon is not None:
        embed.set_thumbnail(url=guild.icon.url)

    embed.add_field(name="Joined a server!",
                    inline=False,
                    value=f"Name: **{guild.name}**" \
                          f"\nMember Count: **{guild.member_count}**" \
                          f"\nChannel Count: **{len(guild.channels)}**" \
                          f"\nCreated On: <t:{int(datetime.datetime.timestamp(guild.created_at))}>"
                    )
    await private_log.send(embed=embed)


@Jerrinth.event
async def on_guild_remove(guild: discord.Guild):
    await Jerrinth.wait_until_ready()
    private_log = Jerrinth.get_channel(Jerrinth.settings["channel_private"])
    Jerrinth.ensureServerExists(guild.id, guild.name)
    Jerrinth.getServer(guild.id)["presence"] = False

    embed = newEmbed(color=discord.Color.blue())

    embed.add_field(name="I was removed from a server...",
                    inline=False,
                    value=f"Name: **{guild.name}**" \
                          f"\nMember Count: **{guild.member_count}**" \
                          f"\nChannel Count: **{len(guild.channels)}**"
                    )
    await private_log.send(embed=embed)


@Jerrinth.event
async def on_member_join(member) -> None:
    """If someone joins my main server, ping them and try to get them to stay lol"""
    if member.guild.id == Jerrinth.settings["server_main"]:
        return
        # channel = Jerrinth.get_channel(970214072052240424)
        # await channel.send(f"Welcome {member.mention}!"
        #                    f"\nTry using my **,ai** command! Ask me anything!"
        #                    f"\n"
        #                    f"\n")


EMOJIS_2048_RUNS = ["🤡", ":clown:"]
SERVER_2048_RUNS = 490493858401222656

@Jerrinth.event
async def on_raw_reaction_add(payload):
    if payload.guild_id is None:
        return

    async def addRole(emoji, role):
        if str(payload.emoji) == emoji:
            role = discord.utils.get(payload.member.guild.roles, name=role)
            await payload.member.add_roles(role)

    if payload.message_id == 1060741442240266330:
        await addRole("✅", "Daily Fact Enjoyer")
        await addRole("🤖", "Bot Update Enjoyer")
        await addRole("🚗", "Random Ping Enjoyer")
        await addRole("⏰", "Jerrin Video Enjoyer")

    if payload.guild_id == SERVER_2048_RUNS:
        if str(payload.emoji) in EMOJIS_2048_RUNS:
            channel = Jerrinth.get_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
            user = Jerrinth.get_user(payload.user_id)
            await message.remove_reaction(str(payload.emoji), user)


@Jerrinth.event
async def on_raw_reaction_remove(payload):
    async def removeRole(_guild, emoji, role):
        if payload.emoji.name == emoji:
            role = discord.utils.get(guild.roles, name=role)
            member = await discord.utils.find(lambda m: m.id == payload.user_id, _guild.members)
            if member is not None:
                await member.remove_roles(role)

    guild = discord.utils.find(lambda g: g.id == payload.guild_id, Jerrinth.guilds)
    if payload.message_id == 1060741442240266330:
        await removeRole(guild, "✅", "Daily Fact Enjoyer")
        await removeRole(guild, "🤖", "Bot Update Enjoyer")
        await removeRole(guild, "🚗", "Random Ping Enjoyer")
        await removeRole(guild, "⏰", "Jerrin Video Enjoyer")


@Jerrinth.event
async def on_message(message: discord.Message) -> None:
    ctx: ctxObject = ctxObject(message)

    # prevents bots from using the bot.
    if ctx.message.author.bot:
        return

    # stops commands from being used when I am messing with the bot.
    if Jerrinth.maintenance:
        if ctx.server != "1048372362900410408":
            if message.content.startswith(","):
                return

    text = ctx.message.content.lower().replace(" ", "")

    # remove clown emojis from 2048 server
    if ctx.server == SERVER_2048_RUNS:
        for emoji in EMOJIS_2048_RUNS:
            if emoji in text:
                await ctx.message.delete()

    # prevent collision with another bot
    if "heypeter" in text:
        return

    if Jerrinth.direct_message:
        # send dm-messages to log channel
        if isinstance(message.channel, discord.DMChannel):
            return await handleDMs(Jerrinth, ctx)
        # send log-messages to dms
        if message.channel.id == 1057516665992134777:
            return await handleSendingDMs(Jerrinth, ctx, message)

    Jerrinth.ensureServerExists(ctx)

    if Jerrinth.debug == (ctx.server != "1048372362900410408"):
        return

    if "bassproshop" in text:
        await ctx.message.add_reaction(random.choice(FISH))

    # for funny shenanigans (replying "real")
    if Jerrinth.getServer(ctx).get("say_real", True):
        if "real" in text:
            if random.random() < 0.25:
                if random.random() < 0.1:
                    await message.channel.send("too real!")
                else:
                    await message.channel.send("real")

    # for funny shenanigans (replying "true")
    if Jerrinth.getServer(ctx).get("say_true", True):
        if "true" in text:
            if random.random() < 0.25:
                if random.random() < 0.1:
                    await message.channel.send("so true!")
                else:
                    await message.channel.send("true")

    # process all commands
    await Jerrinth.process_commands(message)


# https://discord.com/developers/active-developer
@Jerrinth.tree.command()
async def ping(interaction: Interaction) -> None:
    """ Displays my ping! """
    await interaction.response.send_message("Pong! **{:.0f}**ms".format(Jerrinth.latency * 1000))


@Jerrinth.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        return
    if isinstance(error, CommandOnCooldown):
        return
    if isinstance(error, discord.errors.Forbidden):
        return
    # print(f"Server: {None}")
    # print(f"User: {ctx.user}")
    print(f"User Message: '{ctx.message.content}'")
    raise error


@tasks.loop(seconds=6)
async def randomTyping():
    channel_id = 751086615274979419
    channel = Jerrinth.get_channel(channel_id)

    kbps = channel.bitrate // 1000
    if kbps == 64 and channel.name == "General":
        return

    try:

        if kbps != 64:
            await channel.edit(bitrate=64000)
            cause = 0
        elif channel.name != "General":
            await channel.edit(name="General")
            cause = 1
        else:
            cause = 0

        links = [
            "https://tenor.com/view/ltg-low-tier-god-you-should-kill-yourself-now-gif-23487049",
            "https://tenor.com/view/black-man-meme-gif-26066047",
            "https://media.discordapp.net/attachments/736427919194456095/879818545364611082/image0.gif",
            "https://tenor.com/view/lmfao-laughing-gif-25145562",
            "https://media.discordapp.net/attachments/725960059368243250/1097970339901882388/speed-10.gif",
            "https://media.discordapp.net/attachments/853524224262012938/1137634226712354826/pointless.gif",
            "https://tenor.com/view/lol-troll-ratio-gif-24586516",
            "https://media.discordapp.net/attachments/812412624082829314/814435448101404672/image0.gif",
            "https://tenor.com/view/math-solve-gif-25965255",
            "https://media.discordapp.net/attachments/535451640812142602/1130553951578759168/ezgif.com-apng-to-gif.gif"
        ]

        link = random.choice(links)

        user_id = 362793094342770688
        user = Jerrinth.get_user(user_id)

        if cause == 0:
            await user.send(embed=newEmbed("KYS retard I immediately set it back to 64Kbps. Lol it can only be 64 now"))
        if cause == 1:
            await user.send(embed=newEmbed("KYS retard I immediately changed it back the General."))
        await user.send(content=link)
    except Exception as e:
        print(e)


@Jerrinth.event
async def on_ready() -> None:
    """
    Loads all cogs, and prints startup message to console.
    Prepares the Imgur library.
    """
    randomTyping.start()

    await Jerrinth.imgur.loadRandomImages()

    for filename in os.listdir(Jerrinth.directory + "cogs"):
        if filename.endswith(".py"):
            await Jerrinth.load_extension(f"cogs.{filename[:-3]}")
            print(f"loaded cogs.{filename[:-3]}")
    print("\nStart up successful!")


Jerrinth.begin()
