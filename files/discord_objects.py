# Jerrin Shirks

import discord
from discord import ext, RawReactionActionEvent
from discord.ext import commands

from files import config


def is_jerrin(_id) -> bool:
    if isinstance(_id, str):
        if _id.isdigit():
            _id = int(_id)
        else:
            return False

    return _id in [
        611427346099994641,  # jerrinth
        1276092878304837632,  # secret gyatt
    ]

async def testAdmin(ctx) -> bool:
    if is_jerrin(ctx.message.author.id):  # jerrin's main account
        return True
    return bool(ctx.message.author.guild_permissions.administrator)


def newEmbed(text: str = "", color=discord.Color.purple(), **kwargs) -> discord.Embed:
    if text != "":
        kwargs["description"] = text
    return discord.Embed(**kwargs, color=color)


def errorEmbed(text: str = "", **kwargs) -> discord.Embed:
    if text != "":
        kwargs["description"] = text
    return discord.Embed(**kwargs, color=discord.Color.red())


def debugEmbed(text: str = "", **kwargs) -> discord.Embed:
    if text != "":
        kwargs["description"] = text
    return discord.Embed(**kwargs, color=discord.Color.blue())


def trophyEmbed(text: str = "", **kwargs) -> discord.Embed:
    if text != "":
        kwargs["description"] = text
    return discord.Embed(**kwargs, color=discord.Color.yellow())


class CtxObject:
    def __init__(self, ctx, **kwargs):
        if isinstance(ctx, CtxObject):
            raise Exception("CtxObject given to it's constructor! Bad!")

        self.super: discord.ext.commands.Context = ctx

        if isinstance(ctx, RawReactionActionEvent):
            self.channel = str(ctx.channel_id)
            self.channelInt = ctx.channel_id
            self.user = str(ctx.user_id)
            self.userInt = ctx.user_id
            self.author = ctx.user_id
            self.message = ctx
            self.server = str(ctx.guild_id)
            self.serverInt = ctx.guild_id
            return

        elif isinstance(ctx, discord.message.Message):
            self.channel = str(ctx.channel.id)
            self.channelInt = ctx.channel.id
            if ctx.guild is not None:
                self.server = str(ctx.guild.id)
                self.serverInt = ctx.guild.id
                if hasattr(ctx.channel, "nsfw_level"):
                    self.nsfw = ctx.channel.nsfw_level
                else:
                    self.nsfw = 0

            self.user = str(ctx.author.id)
            self.userInt = ctx.author.id
            self.author = ctx.author
            self.message = ctx
            return

        elif isinstance(ctx, discord.ext.commands.context.Context):
            self.channel = str(ctx.channel.id)
            self.channelInt = ctx.channel.id
            self.message = ctx.message

            if ctx.message.guild is not None:
                self.server = str(ctx.message.guild.id)
                self.serverInt = ctx.message.guild.id
                self.nsfw = ctx.channel.nsfw

            self.user = str(ctx.message.author.id)
            self.userInt = ctx.message.author.id

            self.author = ctx.message.author
            self.message = ctx.message
            return

        else:
            print("want to kill myself", type(ctx))

        for kwarg in kwargs:
            if kwarg == "server":
                server = kwargs["server"]
                if server is not None:
                    if server.isdigit():
                        self.server = server
                        self.serverInt = int(server)

            if kwarg == "channel":
                channel = kwargs["channel"]
                if channel is not None:
                    if isinstance(channel, str):
                        if channel.isdigit():
                            self.channel = channel
                            self.channelInt = int(channel)
                    elif isinstance(channel, int):
                        self.channel = str(channel)
                        self.channelInt = channel

            if kwarg == "user":
                user = kwargs["user"]
                if user is not None:
                    if isinstance(user, str):
                        if user.isdigit():
                            self.user = user
                            self.userInt = int(user)
                    if isinstance(user, int):
                        self.user = str(user)
                        self.userInt = user

    def updateChannel(self, channel_id):
        if channel_id is not None:
            if isinstance(channel_id, int):
                self.channel = str(channel_id)
                self.channelInt = channel_id
            elif isinstance(channel_id, str):
                if channel_id.isdigit():
                    self.channel = channel_id
                    self.channelInt = int(channel_id)

    def updateUser(self, user_obj):
        if user_obj is not None:
            if isinstance(user_obj, discord.User):
                self.author = user_obj
                self.user = str(user_obj)
                self.userInt = user_obj
            elif isinstance(user_obj, str):
                if user_obj.isdigit():
                    self.user = user_obj
                    self.userInt = int(user_obj)
            elif isinstance(user_obj, int):
                self.user = str(user_obj)
                self.userInt = user_obj

    async def send(self, message, allowed_mentions=False, reference=False, **kwargs):

        if type(message) in [int, float]:
            kwargs["content"] = str(message)
        elif isinstance(message, str):
            kwargs["content"] = message
        elif isinstance(message, discord.Embed):
            kwargs["embed"] = message

        if not allowed_mentions:
            kwargs["allowed_mentions"] = discord.AllowedMentions(users=False)
        if reference:
            if allowed_mentions:
                return await self.super.reply(mention_author=True, **kwargs)
            else:
                return await self.super.reply(mention_author=False, **kwargs)
        return await self.super.send(**kwargs)

    async def sendError(self, *args, **kwargs):
        allowed_mentions = kwargs.get("allowed_mentions", False)
        if "allowed_mentions" in kwargs:
            kwargs.pop("allowed_mentions")
        reference = kwargs.get("reference", None)
        if "reference" in kwargs:
            kwargs.pop("reference")

        embed = errorEmbed(*args, **kwargs)
        return await self.send(embed, allowed_mentions, reference)

    async def sendDebug(self, *args, **kwargs):
        if config.DEBUG:
            allowed_mentions = kwargs.get("allowed_mentions", False)
            if "allowed_mentions" in kwargs:
                kwargs.pop("allowed_mentions")
            reference = kwargs.get("reference", None)
            if "reference" in kwargs:
                kwargs.pop("reference")

            embed = debugEmbed(*args, **kwargs)
            return await self.send(embed, allowed_mentions, reference)

    async def sendEmbed(self, *args, **kwargs):
        allowed_mentions = kwargs.get("allowed_mentions", False)
        if "allowed_mentions" in kwargs:
            kwargs.pop("allowed_mentions")
        reference = kwargs.get("reference", None)
        if "reference" in kwargs:
            kwargs.pop("reference")

        embed = newEmbed(*args, **kwargs)
        return await self.send(embed, allowed_mentions, reference)
