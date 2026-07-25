# Jerrin Shirks
import discord.utils
# native imports
from discord.ext import commands, tasks

# custom imports
from files.jerrinth import JerrinthBot
from files.makeTable import makeTable
from files.support import CtxObject
from files.wrappers import *
import re

SERVER_ID = 490493858401222656


class ServerMainCog(commands.Cog):
    def __init__(self, bot):
        self.bot: JerrinthBot = bot
        self.SERVER_ID = 847402389698641940

        self.bot.hooks_on_raw_reaction_add[self.SERVER_ID] = self.on_raw_reaction_add
        self.bot.hooks_on_raw_reaction_remove[self.SERVER_ID] = self.on_raw_reaction_remove
        # self.bot.hooks_on_member_join[self.SERVER_ID] = self.on_member_join
        # self.bot.hooks_on_message[self.SERVER_ID] = self.on_message

        """
        self.id_jerrin = 611427346099994641
        self.id_frik = 145244703397380096
        self.sm_filepath = "data/sl.json"
        self.sm_data = read_json(self.sm_filepath)
        self.soulmates_jerrin = set(self.sm_data.get("jerrin", []))
        self.soulmates_frik = set(self.sm_data.get("frik", []))
    """

        """
    async def on_message(self, ctx: CtxObject) -> None:
        if ctx.userInt != 432610292342587392:
            return

        if len(ctx.message.embeds):
            embed = ctx.message.embeds[0]
            author = embed.author.name
            try:
                if "Belongs to" not in embed.footer.text:
                    return
            except:
                return

            author = author.lower() \
                .strip() \
                .strip("\n") \
                .replace("\n", " ")
            while "   " in author:
                author = author.replace("  ", " ")

            # await ctx.message.channel.send("Someone owns this")
            message = "<@{}> Soulmate! Click The Kakera!"
            if author in self.soulmates_jerrin:
                await ctx.message.channel.send(message.format(self.id_jerrin),
                                               reference=ctx.message)
            elif author in self.soulmates_frik:
                await ctx.message.channel.send(message.format(self.id_frik),
                                               reference=ctx.message)
        """




    async def on_raw_reaction_add(self, payload):
        async def addRole(emoji, role):
            if str(payload.emoji) == emoji:
                role = discord.utils.get(payload.member.guild.roles, name=role)
                await payload.member.add_roles(role)

        if payload.message_id == 1060741442240266330:
            await addRole("✅", "Daily Fact Enjoyer")
            await addRole("🤖", "Bot Update Enjoyer")
            await addRole("🚗", "Random Ping Enjoyer")
            await addRole("⏰", "Jerrin Video Enjoyer")

    async def on_raw_reaction_remove(self, payload):
        async def removeRole(_guild, emoji, role):
            if payload.emoji.name == emoji:
                role = discord.utils.get(guild.roles, name=role)
                member = await discord.utils.find(lambda m: m.id == payload.user_id, _guild.members)
                if member is not None:
                    await member.remove_roles(role)

        guild = discord.utils.find(lambda g: g.id == payload.guild_id, self.bot.guilds)
        if payload.message_id == 1060741442240266330:
            await removeRole(guild, "✅", "Daily Fact Enjoyer")
            await removeRole(guild, "🤖", "Bot Update Enjoyer")
            await removeRole(guild, "🚗", "Random Ping Enjoyer")
            await removeRole(guild, "⏰", "Jerrin Video Enjoyer")
    """
    async def on_member_join(self, member):
        channel = self.bot.get_channel(970214072052240424)
        await channel.send(f"Welcome {member.mention}!"
                           f"\nTry using my **,chat** command! Ask me anything!"
                           f"\n"
                           f"\n")
    """

async def setup(bot):
    await bot.add_cog(ServerMainCog(bot))
