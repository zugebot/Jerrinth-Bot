# Jerrin Shirks

# native imports
import functools
from discord.ext import commands

# custom imports
from files.support import *


def is_jerrin(func):
    discord_id = 611427346099994641 # jerrinth3glitch#6280

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        if args[1].author.id == discord_id:
            return await func(*args, **kwargs)
        await args[1].send(errorEmbed(description=f"Only <@{discord_id}> can use this."))
    return wrapper


def ctx_wrapper(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        args = list(args)
        if not isinstance(args[1], ctxObject):
            args[1] = ctxObject(args[1], **kwargs)
        args = tuple(args)

        if str(args[1].user) in args[0].bot.banned_users:
            embed = errorEmbed("My creator has specifically blacklisted you from using me lol.")
            return await args[1].send(embed)

        return await func(*args, **kwargs)
    return wrapper


def channel_redirect(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        # if it is a valid channel
        self, ctx = args[0], args[1]

        usable_everywhere = self.bot.getServer(ctx).get("usable_everywhere", False)

        if self.bot.channelExists(ctx) or usable_everywhere:
            return await func(*args, **kwargs)

        if self.bot.getServer(ctx).get("channel_redirect", True):

            self.bot.ensureServerExists(ctx)
            prefix = self.bot.data["servers"][ctx.server]["prefix"]
            channels = self.bot.getChannelDict(ctx)

            embed = newEmbed(title="Channel List")
            embed.description = "You cannot use that command in this channel.\n" \
                                "Please navigate to one of the below channels."


            field_title = "Channels" if channels else "Channels Usable (Empty!)"

            text = ""
            if channels:
                text = ", ".join([f"<#{channel}>" for channel in channels]) + "\n"
            text = f"{text}Admins can add a channel using **{prefix}addchannel\n**"
            text = f"{text}Admins can also add all channels using **{prefix}omni**"
            embed.add_field(name=field_title, inline=False, value=text)

            return await ctx.send(embed, reference=True)

        else:
            return None

    return wrapper


def cool_down_error(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        self, ctx, error = args[0], args[1], args[2]

        # cooldown error
        if isinstance(error, commands.CommandOnCooldown):
            if self.bot.getServer(ctx).get("show_time_left", True):
                text = f"Try again in **{error.retry_after:.3f}**s."
                return await ctx.send(text)
            else:
                return await ctx.super.message.add_reaction(convertDecimalToClock(error.retry_after / error.cooldown.per))

        return await func(*args, **kwargs)
    return wrapper
