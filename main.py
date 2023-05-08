# Jerrin Shirks
# native imports
from discord import Interaction
from discord.ext.commands import CommandNotFound, CommandOnCooldown
import datetime
import logging

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
        channel = Jerrinth.get_channel(970214072052240424)
        await channel.send(f"Welcome {member.mention}!"
                           f"\nTry using my **,ai** command! Ask me anything!"
                           f"\n"
                           f"\n")


@Jerrinth.event
async def on_raw_reaction_add(payload):
    async def addRole(emoji, role):
        if str(payload.emoji) == emoji:
            role = discord.utils.get(payload.member.guild.roles, name=role)
            await payload.member.add_roles(role)

    if payload.message_id == 1060741442240266330:
        await addRole("✅", "Daily Fact Enjoyer")
        await addRole("🤖", "Bot Update Enjoyer")
        await addRole("🚗", "Random Ping Enjoyer")
        await addRole("⏰", "Jerrin Video Enjoyer")


@Jerrinth.event
async def on_raw_reaction_remove(payload):
    async def removeRole(_guild, emoji, role):
        if payload.emoji.name == emoji:
            role = discord.utils.get(guild.roles, name=role)
            member = discord.utils.find(lambda m: m.id == payload.user_id, _guild.members)
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
    print(f"Server: {None}")
    print(f"User: {ctx.user}")
    print(f"User Message: '{ctx.message.content}'")
    raise error


# BOT STARTUP CODE
@Jerrinth.event
async def on_ready() -> None:
    """
    Loads all cogs, and prints startup message to console.
    Prepares the Imgur library.
    """
    # await Jerrinth.imgur.loadRandomImages()

    for filename in os.listdir(Jerrinth.directory + "cogs"):
        if filename.endswith(".py"):
            await Jerrinth.load_extension(f"cogs.{filename[:-3]}")
            print(f"loaded cogs.{filename[:-3]}")
    print("\nStart up successful!")


Jerrinth.begin()
