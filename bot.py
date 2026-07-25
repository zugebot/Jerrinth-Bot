# Jerrin Shirks
# native imports
import asyncio
from asyncio import WindowsSelectorEventLoopPolicy

import discord
from discord import Interaction, app_commands
from discord.ext.commands import CommandNotFound, CommandOnCooldown
from discord.ext import tasks
from discord.ext import commands
import datetime
import random
import logging
from inspect import Signature, Parameter
from files.wrappers import *
from files.discord_objects import is_jerrin

# custom imports
from files.jerrinth import JerrinthBot
from funcs.handle_dms import *
from files.support import *
from files.config import *

logging.basicConfig(level=logging.CRITICAL)

Jerrinth = JerrinthBot(data_version=1,
                       debug=DEBUG,
                       maintenance=MAINTENANCE,
                       direct_message=DIRECT_MESSAGES)


def _slash_type_from_meta(type_value):
    if isinstance(type_value, type):
        return type_value
    if type_value is None:
        return str

    type_key = str(type_value).lower()
    return {
        "num": int,
        "number": int,
        "int": int,
        "float": float,
        "double": float,
        "str": str,
        "string": str,
        "text": str,
        "bool": bool,
        "boolean": bool,
        "member": discord.Member,
        "user": discord.User,
        "ping": discord.Member,
        "role": discord.Role,
        "channel": discord.TextChannel,
        "attachment": discord.Attachment,
    }.get(type_key, str)


def _normalize_slash_choices(choices_value):
    if choices_value is None:
        return None

    if isinstance(choices_value, dict):
        return [app_commands.Choice(name=str(name), value=value) for name, value in choices_value.items()]

    if isinstance(choices_value, (list, tuple)):
        output = []
        for item in choices_value:
            if isinstance(item, (list, tuple)) and len(item) == 2:
                name, value = item
                output.append(app_commands.Choice(name=str(name), value=value))
            else:
                output.append(app_commands.Choice(name=str(item), value=item))
        return output

    return None

def _clean_slash_description(value):
    value = " ".join(str(value or "No description provided.").split())

    if not value:
        value = "No description provided."

    if len(value) > 100:
        value = value[:97] + "..."

    return value

def _clean_slash_name(value, fallback="arg"):
    value = str(value or fallback).strip().lower()

    cleaned = ""

    for char in value:
        if char.isalnum() or char in ["_", "-"]:
            cleaned += char
        else:
            cleaned += "_"

    cleaned = cleaned.strip("_-")

    if not cleaned:
        cleaned = fallback

    cleaned = cleaned[:32].strip("_-")

    if not cleaned:
        cleaned = fallback

    return cleaned

async def _deny_slash(interaction: Interaction, message: str):
    if interaction.response.is_done():
        return await interaction.followup.send(message, ephemeral=True)

    return await interaction.response.send_message(message, ephemeral=True)


def _normalize_default_permissions(value):
    if value is None:
        return None

    if isinstance(value, dict):
        return value

    if isinstance(value, discord.Permissions):
        return {
            name: enabled
            for name, enabled in value
            if enabled
        }

    raise TypeError("slash_default_permissions must be a dict or discord.Permissions.")

def _build_slash_callback(command, meta):
    raw_args_meta = [dict(arg) for arg in meta.get("args", [])]
    var_types = meta.get("var_types", {})

    args_meta = []
    used_arg_names = set()

    for arg in raw_args_meta:
        original_name = arg["name"]
        clean_name = _clean_slash_name(original_name)

        base_name = clean_name
        counter = 2

        while clean_name in used_arg_names:
            suffix = f"_{counter}"
            clean_name = base_name[:32 - len(suffix)] + suffix
            counter += 1

        used_arg_names.add(clean_name)

        arg["original_name"] = original_name
        arg["name"] = clean_name

        args_meta.append(arg)

    async def slash_callback(interaction: Interaction, **params):
        allowed_user_ids = {
            int(user_id)
            for user_id in meta.get("user_ids", [])
        }

        allowed_channel_ids = {
            int(channel_id)
            for channel_id in meta.get("channel_ids", [])
        }

        if allowed_user_ids and interaction.user.id not in allowed_user_ids:
            return await _deny_slash(interaction, "You cannot use this command.")

        if allowed_channel_ids and interaction.channel_id not in allowed_channel_ids:
            return await _deny_slash(interaction, "You cannot use this command in this channel.")

        user_req = int(meta.get("user_req", 0))

        if user_req == 2 and not is_jerrin(interaction.user.id):
            return await _deny_slash(interaction, "You cannot use this command.")

        if user_req == 1:
            guild_permissions = getattr(interaction.user, "guild_permissions", None)

            if guild_permissions is None or not guild_permissions.administrator:
                return await _deny_slash(interaction, "Only admins can use this command.")

        ctx = await commands.Context.from_interaction(interaction)

        # Manually run the ext.commands cooldown bucket.
        # Slash commands call command.callback directly, so discord.py does not do this for us.
        try:
            command._prepare_cooldowns(ctx)

        except CommandOnCooldown as error:
            try:
                await command.dispatch_error(ctx, error)
            except Exception:
                pass

            if not interaction.response.is_done():
                return await _deny_slash(
                    interaction,
                    f"Try again in **{error.retry_after:.3f}**s."
                )

            return

        ordered_args = []

        for arg in args_meta:
            arg_name = arg["name"]
            value = params.get(arg_name, None)

            if value is None and not arg.get("required", True):
                continue

            ordered_args.append(value)

        if command.cog is None:
            return await command.callback(ctx, *ordered_args)

        return await command.callback(command.cog, ctx, *ordered_args)

    desc_map = {}
    choices_map = {}

    for index, arg in enumerate(args_meta):
        arg_name = arg["name"]

        desc_map[arg_name] = _clean_slash_description(
            arg.get("description") or arg.get("original_name") or arg_name
        )

        choices = _normalize_slash_choices(arg.get("choices"))
        if choices:
            choices_map[arg_name] = choices

    if desc_map:
        slash_callback = app_commands.describe(**desc_map)(slash_callback)

    if choices_map:
        slash_callback = app_commands.choices(**choices_map)(slash_callback)

    default_permissions = meta.get("default_permissions")

    if default_permissions is None and int(meta.get("user_req", 0)) in [1, 2]:
        default_permissions = {
            "administrator": True
        }

    default_permissions = _normalize_default_permissions(default_permissions)

    if default_permissions:
        slash_callback = app_commands.default_permissions(**default_permissions)(slash_callback)

    params = [
        Parameter(
            "interaction",
            Parameter.POSITIONAL_OR_KEYWORD,
            annotation=Interaction
        )
    ]

    for index, arg in enumerate(args_meta):
        arg_name = arg["name"]
        arg_type = arg.get("type")

        if arg_type is None and index in var_types:
            arg_type = var_types[index]

        arg_type = _slash_type_from_meta(arg_type)

        required = arg.get("required", True)
        default = Parameter.empty if required else None

        params.append(
            Parameter(
                arg_name,
                Parameter.KEYWORD_ONLY,
                annotation=arg_type,
                default=default
            )
        )

    slash_callback.__signature__ = Signature(params)
    slash_callback.__name__ = f"slash_{_clean_slash_name(command.name, 'command')}"

    return slash_callback

def _get_slash_meta(command):
    try:
        meta = command.extras.get("slash_meta", None)
        if meta is not None:
            return meta
    except Exception:
        pass

    meta = getattr(command, "_slash_meta", None)

    if meta is not None:
        return meta

    meta = getattr(command.callback, "_slash_meta", None)

    if meta is not None:
        return meta

    wrapped = getattr(command.callback, "__wrapped__", None)

    if wrapped is not None:
        return getattr(wrapped, "_slash_meta", None)

    return None

async def _build_local_slash_tree(bot: JerrinthBot):
    registered = []

    print("Prefix commands found:")

    for command in bot.walk_commands():
        print(f"  {command.name}")

        meta = _get_slash_meta(command)

        if not meta or not meta.get("enabled"):
            continue

        description = _clean_slash_description(
            meta.get("description") or "No description provided."
        )

        slash_callback = _build_slash_callback(command, meta)

        command_name = _clean_slash_name(command.name, "command")

        slash_command = app_commands.Command(
            name=command_name,
            description=description,
            callback=slash_callback,
        )

        existing = bot.tree.get_command(command_name)
        if existing is not None:
            bot.tree.remove_command(command_name)

        bot.tree.add_command(slash_command)
        registered.append(command_name)

    print("Wrapper slash commands registered:")
    for name in registered:
        print(f"  /{name}")

    return registered


async def _sync_slash_global(bot: JerrinthBot):
    synced = await bot.tree.sync(guild=None)

    print(f"Synced {len(synced)} global slash commands.")
    for cmd in synced:
        print(f"  /{cmd.name}")

    return {
        "scope": "global",
        "synced_count": len(synced),
        "synced_commands": [cmd.name for cmd in synced],
    }


async def _sync_slash_guild(bot: JerrinthBot, guild: discord.Guild):
    guild_obj = discord.Object(id=guild.id)

    bot.tree.clear_commands(guild=guild_obj)
    bot.tree.copy_global_to(guild=guild_obj)

    synced = await bot.tree.sync(guild=guild_obj)

    print(f"Synced {len(synced)} slash commands to {guild.name} ({guild.id}).")

    return {
        "guild_name": guild.name,
        "guild_id": guild.id,
        "synced_count": len(synced),
        "synced_commands": [cmd.name for cmd in synced],
    }


async def _sync_slash_debug_guild(bot: JerrinthBot):
    guild_id = 1048372362900410408
    guild = bot.get_guild(guild_id)

    if guild is None:
        guild_obj = discord.Object(id=guild_id)

        bot.tree.clear_commands(guild=guild_obj)
        bot.tree.copy_global_to(guild=guild_obj)

        synced = await bot.tree.sync(guild=guild_obj)

        print(f"Synced {len(synced)} slash commands to debug guild ({guild_id}).")
        for cmd in synced:
            print(f"  /{cmd.name}")

        return {
            "scope": "debug",
            "guild_name": "debug guild",
            "guild_id": guild_id,
            "synced_count": len(synced),
            "synced_commands": [cmd.name for cmd in synced],
        }

    result = await _sync_slash_guild(bot, guild)
    result["scope"] = "debug"
    return result


async def _sync_slash_all_guilds(bot: JerrinthBot):
    synced_guilds = []
    failed_guilds = []

    for guild in bot.guilds:
        try:
            result = await _sync_slash_guild(bot, guild)
            synced_guilds.append(result)

        except Exception as e:
            failed_guilds.append({
                "guild_name": guild.name,
                "guild_id": guild.id,
                "error": str(e),
            })

            print(f"FAILED to sync slash commands to {guild.name} ({guild.id}): {e}")

        await asyncio.sleep(0.25)

    return {
        "scope": "all",
        "synced_guilds": synced_guilds,
        "failed_guilds": failed_guilds,
    }


async def _register_slash_commands(
        bot: JerrinthBot,
        *,
        scope: str = None,
        guild: discord.Guild = None,
):
    registered = await _build_local_slash_tree(bot)

    if scope is None:
        scope = "debug" if DEBUG else "global"

    scope = scope.lower().strip()

    if scope in ["global"]:
        result = await _sync_slash_global(bot)

    elif scope in ["debug", "debug_guild"]:
        result = await _sync_slash_debug_guild(bot)

    elif scope in ["current", "current_guild", "guild", "server"]:
        if guild is None:
            raise ValueError("Current guild slash sync requires a guild.")

        result = await _sync_slash_guild(bot, guild)
        result["scope"] = "current"

    elif scope in ["all", "all_guilds", "servers"]:
        result = await _sync_slash_all_guilds(bot)

    else:
        raise ValueError(f"Unknown slash sync scope: {scope}")

    result["registered"] = registered
    return result


async def _refresh_slash_commands(scope: str = "current", guild: discord.Guild = None):
    return await _register_slash_commands(
        Jerrinth,
        scope=scope,
        guild=guild,
    )


async def _post_cog_load_hook():
    await _register_slash_commands(Jerrinth)


Jerrinth.refreshSlashCommands = _refresh_slash_commands
Jerrinth._post_cog_load_hook = _post_cog_load_hook


@Jerrinth.event
async def on_message(message: discord.Message) -> None:
    ctx: CtxObject = CtxObject(message)

    if ctx.message.author.bot:
        if ctx.userInt != 432610292342587392 or ctx.serverInt != 847402389698641940:
            return

    # stops commands from being used when I am messing with the bot.
    if Jerrinth.maintenance:
        if ctx.server != "1048372362900410408":
            if message.content.startswith(","):
                return

    text = ctx.message.content.lower().replace(" ", "")

    try:
        for func in Jerrinth.hooks_on_message.get("all", []):
            if callable(func):
                await func(ctx)
    except Exception as e:
        print("Error: ", e)

    try:
        func = Jerrinth.hooks_on_message.get(ctx.serverInt, None)
        if callable(func):
            await func(ctx)
    except Exception as e:
        print("Error: ", e)

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

    while ctx.userInt != 432610292342587392:
        if found_real and found_true and random.random() < 0.25:
            await message.channel.send(["real and true", "so true and too real!"][random.random() < 0.1])
            break
        elif (found_real and random.random() < 0.25) or (random.random() < (1 / 25000)):
            chance = random.random()
            if chance < 1/300:
                msg = "unfathomably fake..."
            elif chance < 7/300:
                msg = "that just isn't true bro"
            elif chance < 5/30:
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

logging.getLogger('discord.gateway').setLevel(logging.WARNING)
logging.getLogger('discord.voice_state').setLevel(logging.WARNING)
logging.getLogger('discord.player').setLevel(logging.WARNING)
asyncio.set_event_loop_policy(WindowsSelectorEventLoopPolicy())
Jerrinth.begin()
