# Jerrin Shirks

# native imports
import functools

# custom imports
from support import *



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
        return await func(*args, **kwargs)
    return wrapper

def channel_redirect(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        # if it is a valid channel
        if not args[0].bot.channelExists(args[1]):
            if args[0].bot.getServer(args[1]).get("channel_redirect", True):

                args[0].bot.ensureServerExists(args[1])
                prefix = args[0].bot.data[args[1].server]["prefix"]
                channels = args[0].bot.getChannelDict(args[1])
                embed = newEmbed(title="Channel List")
                embed.description = "You cannot use that command in this channel.\nPlease navigate to one of the below channels."
                if channels:
                    items = ", ".join([f"<#{channel}>" for channel in channels])
                    embed.add_field(name="Channels", inline=False, value=items)
                else:
                    value = f"Have an admin add a channel using **{prefix}addchannel**"
                    embed.add_field(name="Channels Usable (Empty!)", inline=False, value=value)

                return await args[1].send(embed, reference=True)

            else:
                return None

        return await func(*args, **kwargs)
    return wrapper
