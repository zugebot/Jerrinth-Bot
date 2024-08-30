# Jerrin Shirks
# native imports
from asyncio import WindowsSelectorEventLoopPolicy

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
async def on_message(message: discord.Message) -> None:
    ctx: CtxObject = CtxObject(message)

    if ctx.message.author.bot:
        return

    # stops commands from being used when I am messing with the bot.
    if Jerrinth.maintenance:
        if ctx.server != "1048372362900410408":
            if message.content.startswith(","):
                return

    text = ctx.message.content.lower().replace(" ", "")

    try:
        func = Jerrinth.hooks_on_message.get(ctx.serverInt, None)
        if callable(func):
            await func(ctx)
    except Exception as e:
        print("Error: ", e)
        # print(e)
        # print(ctx.__dict__)

    # prevent collision with another bot
    if "heypeter" in text:
        return

    if Jerrinth.direct_message:
        # send dm-messages to log channel
        if isinstance(message.channel, discord.DMChannel):
            return await handleDMs(Jerrinth, ctx)
        # send log-messages to dms
        if message.channel.id == 1057516665992134777:
            replacement = None
            if message.content.split(" ")[0].isdigit():
                replacement, message.content = message.content.split(" ", 1)
            return await handleSendingDMs(Jerrinth, ctx, message, replacement)

    try:
        Jerrinth.ensureServerExists(ctx)
    except:
        print("ERROR calling Jerrinth.ensureServerExists(ctx)")
        print(str(ctx))
        return

    if Jerrinth.debug == (ctx.server != "1048372362900410408"):
        return

    if "bassproshop" in text:
        await ctx.message.add_reaction(random.choice(FISH))

    # for funny shenanigans (replying "real")
    found_real = False
    if Jerrinth.getServer(ctx).get("say_real", True):
        if "real" in text:
            found_real = True

    # for funny shenanigans (replying "true")
    found_true = False
    if Jerrinth.getServer(ctx).get("say_true", True):
        if "true" in text:
            found_true = True

    while True:
        if found_real and found_true and random.random() < 0.25:
            await message.channel.send(["real and true", "so true and too real!"][random.random() < 0.1])
            break
        elif found_real and random.random() < 0.25:
            chance = random.random()
            if chance < 5/30:
                msg = "fake"
            elif chance < 7/30:
                msg = "too real!"
            else:
                msg = "real"
            await message.channel.send(msg)
            break
        elif found_true and random.random() < 0.25:
            await message.channel.send(["true", "so true!"][random.random() < 0.1])
            break
        else:
            break


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


asyncio.set_event_loop_policy(WindowsSelectorEventLoopPolicy())
Jerrinth.begin()
