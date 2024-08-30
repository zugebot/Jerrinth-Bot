# Jerrin Shirks

# native imports

# custom imports
from files.support import *
from files.discord_objects import *


async def handleDMs(Jerrinth, ctx):
    logChannel = Jerrinth.getLogChannel()
    # _time = int(datetime.timestamp(ctx.message.created_at.now()))
    main_embed = newEmbed(color=ctx.author.color,
                          description=f"**From** <@{ctx.author.id}>\n{ctx.message.content}")
    main_embed.set_author(name=f"{ctx.message.author.name}",
                          icon_url=ctx.message.author.avatar)

    await logChannel.send(embed=main_embed)

    for attachment in ctx.message.attachments:
        await logChannel.send(attachment)

    return


async def handleSendingDMs(Jerrinth, ctx, message, replacement=None):
    logChannel = Jerrinth.getLogChannel()
    if not message.content:
        return

    # let me reply to messages in #log-channel
    if message.reference is not None:
        if message.reference.channel_id == Jerrinth.getLogChannel().id:
            original = await logChannel.fetch_message(ctx.message.reference.message_id)

            if original.embeds is None:
                return await message.add_reaction("❓")

            try:

                # send to user
                if replacement is None:
                    user = Jerrinth.get_user(int(re.findall("[0-9]{15,20}", original.embeds[0].description)[0]))
                else:
                    user = Jerrinth.get_user(int(replacement))
                text = message.content
                # text = f"**From** <@{ctx.message.author.id}>\n\n{message.content}"
                # embed = newEmbed(color=ctx.message.author.accent_color, description=text)
                await user.send(message.content)

                # make log-channel better
                text = f"**To** <@{user.id}>\n{message.content}"
                embed = newEmbed(description=text)
                embed.set_author(name=f"{message.author.name}",
                                 icon_url=message.author.avatar)
                await logChannel.send(embed=embed)

                # delete old log-message
                await ctx.message.delete()
                return

            except Exception as e:
                return await logChannel.send(content=f"An error occurred.\n{e}")


    # lets me send messages by specifying id at start of message
    if len(message.content.split()) <= 1:
        return await message.add_reaction("❓")

    arg1 = message.content.split()[0]
    number = re.findall("[0-9]{15,20}", arg1)
    if len(number) > 0:
        user_id = int(number[0])

        user = Jerrinth.get_user(user_id)
        if user is None:
            return await message.add_reaction("❌")

        content_to_send = " ".join(ctx.message.content.split(" ")[1:])

        # send to user
        text = f"**From** <@{ctx.message.author.id}>\n\n{content_to_send}"
        embed = newEmbed(description=text)
        await user.send(embed=embed)

        # make log-channel better
        sender = Jerrinth.get_user(ctx.author.id)
        text = f"**To** <@{user_id}>\n\n{content_to_send}"
        embed = newEmbed(color=sender.accent_color, description=text)
        embed.set_author(name=f"{sender.name}",
                         icon_url=sender.avatar)

        await logChannel.send(embed=embed)
        await ctx.message.delete()
    else:
        return await message.add_reaction("❓")


async def setup(bot):
    pass
