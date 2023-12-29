# Jerrin Shirks

# native imports
from discord.ext import commands, tasks

# custom imports
from files.jerrinth import JerrinthBot
from files.support import ctxObject
from files.wrappers import *

SERVER_ID = 490493858401222656


class ServerMainCog(commands.Cog):
    def __init__(self, bot):
        self.bot: JerrinthBot = bot
        self.SERVER_ID = 847402389698641940

        self.bot.hooks_on_raw_reaction_add[self.SERVER_ID] = self.on_raw_reaction_add
        self.bot.hooks_on_raw_reaction_remove[self.SERVER_ID] = self.on_raw_reaction_remove
        self.bot.hooks_on_member_join[self.SERVER_ID] = self.on_member_join

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

    async def on_member_join(self, member):
        channel = self.bot.get_channel(970214072052240424)
        await channel.send(f"Welcome {member.mention}!"
                           f"\nTry using my **,chat** command! Ask me anything!"
                           f"\n"
                           f"\n")

async def setup(bot):
    await bot.add_cog(ServerMainCog(bot))






















