# Jerrin Shirks

# native imports
import functools
from typing import Dict

from discord.ext import commands
from discord.ext.commands import Context

# custom imports
from files.support import *


async def send_redirect(self, ctx: ctxObject) -> bool:
    usable_everywhere = self.bot.getServer(ctx).get("usable_everywhere", False)
    if self.bot.channelExists(ctx) or usable_everywhere:
        return False

    if not self.bot.getServer(ctx).get("channel_redirect", True):
        return False

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
    await ctx.send(embed, reference=True)
    return True


def ctx_wrapper(var_types: Dict[int, str] = None, user_req: int = 0, redirect: bool = False):
    """
    :param var_types: "ping", "num"
    :param user_req: 0: all, 1: admins, 2: jerrin
    :param redirect:
    :return:
    """
    if var_types is None:
        var_types = {}

    jerrin_id = 611427346099994641

    def decorator(func):
        @functools.wraps(func)
        async def wrapper(self, ctx, *args, **kwargs):

            # Reassign ctx
            ctx = ctxObject(ctx)

            # prevent banned accounts
            if str(ctx.user) in self.bot.banned_users:
                return await ctx.sendError("My creator has specifically blacklisted you from using me lol.")

            # check requirements
            if user_req != 0:
                can_use = False
                if user_req > 0:
                    can_use = bool(ctx.message.author.guild_permissions.administrator)
                if user_req > 1:
                    can_use = ctx.author.id == jerrin_id
                if not can_use:
                    return

            # shows redirect
            if redirect:
                status = await send_redirect(self, ctx)
                if status:
                    return

            # Process arguments based on argument_mapping
            new_args = list(args)
            for arg_index, arg_type in var_types.items():
                if arg_type == "num":
                    new_args[arg_index] = argParseInt(args[arg_index])
                if arg_type == "ping":
                    new_args[arg_index] = argParsePing(args[arg_index])

            return await func(self, ctx, *new_args, **kwargs)

        return wrapper

    return decorator


def error_wrapper(use_cooldown: bool = False):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(self, ctx, error, *args, **kwargs):
            ctx = ctxObject(ctx)

            # cooldown error
            if use_cooldown:
                if isinstance(error, commands.CommandOnCooldown):
                    if self.bot.getServer(ctx).get("show_time_left", True):
                        text = f"Try again in **{error.retry_after:.3f}**s."
                        return await ctx.send(text)
                    else:
                        return await ctx.super.message.add_reaction(
                            convertDecimalToClock(error.retry_after / error.cooldown.per))

            return await func(self, ctx, error, *args, **kwargs)

        return wrapper

    return decorator
