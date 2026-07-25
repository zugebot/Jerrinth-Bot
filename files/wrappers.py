# Jerrin Shirks

# native imports
import asyncio
import functools
from typing import Dict, Any
from collections import OrderedDict
from discord.ext import commands
from discord.ext.commands import Context, BucketType

from files.discord_objects import newEmbed, is_jerrin
# custom imports
from files.support import *


async def send_redirect(self, ctx: CtxObject) -> bool:
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


ALL_ALIASES = None


def updateNameAndAlias(kwargs: Dict[str, Any]) -> Dict[str, Any]:
    global ALL_ALIASES

    if ALL_ALIASES is None:
        ALL_ALIASES = OrderedDict()

    # Step 1: ensure valid arguments
    _error = "@unified_wrapper: "
    # ensure valid name format
    _new_aliases = set()
    if "name" not in kwargs:
        raise ValueError(f"{_error}\"name\" kwarg not passed.")
    _name: str = kwargs["name"]
    if _name.lower() != _name:
        raise ValueError(f"{_error}\"name\" kwarg should be all lowercase ({_name}).")
    if _name in ALL_ALIASES:
        print(f"{_error}command name \"{_name}\" is already used by command "
              f"\"{ALL_ALIASES[_name]}\". All names must be unique.")
    else:
        ALL_ALIASES[_name] = _name
    _new_aliases.add(capitalize(_name))
    _new_aliases.add(_name.swapcase())
    _new_aliases.add(capitalize(_name).swapcase())

    # create kwargs["aliases"] if it does not exist
    if "aliases" not in kwargs:
        kwargs["aliases"] = []
    if not isinstance(kwargs["aliases"], list):
        raise ValueError(f"{_error}\"aliases\" kwarg be of type list.")
    # add aliases
    for _iter_alias in kwargs["aliases"]:
        if _iter_alias.lower() != _iter_alias:
            raise ValueError(f"{_error}\"aliases\" argument \"{_iter_alias}\" should be all lowercase.")
        elif _iter_alias in ALL_ALIASES:
            raise ValueError(f"{_error}alias \"{_iter_alias}\" is already used "
                             f"by the command \"{ALL_ALIASES[_iter_alias]}\". All names must be unique.")
        else:
            ALL_ALIASES[_iter_alias] = _name

        _new_aliases.add(capitalize(_iter_alias))
        _new_aliases.add(_iter_alias.swapcase())
        _new_aliases.add(capitalize(_iter_alias).swapcase())
    # update aliases kwarg
    kwargs["aliases"] = list(_new_aliases)

    return kwargs


def wrapper_command(*args, cooldown=None, var_types: Dict[int, str] = None,
                    user_req: int = 0, redirect: bool = False,
                    slash: bool = False, slash_description: str = None, slash_args: list[Dict[str, Any]] = None,
                    slash_user_ids: list[int] = None,
                    slash_channel_ids: list[int] = None,
                    slash_default_permissions: dict = None,
                    **kwargs):

    var_types = var_types or {}

    def decorator(func):
        nonlocal kwargs
        if not asyncio.iscoroutinefunction(func):
            raise TypeError("Callback must be a coroutine.")

        kwargs = updateNameAndAlias(kwargs)

        if slash_args is None:
            slash_args_local = []
        else:
            slash_args_local = slash_args
            for arg in slash_args_local:
                if "name" not in arg:
                    raise ValueError("@wrapper_command: slash_args items must include a 'name'.")

        slash_meta = {
            "enabled": slash,
            "description": slash_description or kwargs.get("description") or (func.__doc__ or "").strip() or "No description provided.",
            "args": slash_args_local,
            "var_types": var_types,
            "user_req": user_req,
            "user_ids": slash_user_ids or [],
            "channel_ids": slash_channel_ids or [],
            "default_permissions": slash_default_permissions,
        }

        @functools.wraps(func)
        async def wrapper(self, context, *inner_args, **inner_kwargs):
            context = CtxObject(context)

            if str(context.user) in self.bot.banned_users:
                return await context.sendError("My creator has specifically blacklisted you from using me lol.")

            if user_req == 2 and not is_jerrin(context.author.id):
                return
            elif user_req == 1 and not context.message.author.guild_permissions.administrator:
                return

            if redirect and await send_redirect(self, context):
                return

            arg_type_map = {
                "num": argParseInt,
                "number": argParseInt,
                "int": argParseInt,
                "ping": argParsePing
            }

            new_args = [
                arg_type_map.get(var_types.get(i), lambda x: x)(arg)
                for i, arg in enumerate(inner_args)
            ]

            return await func(self, context, *new_args, **inner_kwargs)

        wrapper._slash_meta = slash_meta
        func._slash_meta = slash_meta

        command = commands.command(*args, **kwargs)(wrapper)

        if cooldown is not None:
            _rate, _per, _type = cooldown
            command = commands.cooldown(_rate, _per, _type)(command)

        command._slash_meta = slash_meta
        command.callback._slash_meta = slash_meta
        command.extras["slash_meta"] = slash_meta

        return command

    return decorator


def wrapper_error(use_cooldown: bool = False):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(self, ctx, error, *args, **kwargs):
            ctx = CtxObject(ctx)

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

