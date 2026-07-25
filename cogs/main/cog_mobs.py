# Jerrin Shirks

# native imports
import time
import random

# custom imports
from files.jerrinth import JerrinthBot
from files.wrappers import *
from files.config import *


class MobCog(commands.Cog):
    def __init__(self, bot):
        print(f"loading '{self.__module__}'")

        self.bot: JerrinthBot = bot

        self.item_defs = {
            "blaze_rod": {
                "name": "blaze rod",
                "plural": "blaze rods",
                "emoji": "<:BlazeRod:1509302767116751028>",
            },
            "glowstone_dust": {
                "name": "glowstone",
                "plural": "glowstone",
                "emoji": "<:GlowstoneDust:1509302786259681310>",
            },
            "bone": {
                "name": "bone",
                "plural": "bones",
                "emoji": "<:Bone:1509316119180349681>",
            },
            "coal": {
                "name": "coal",
                "plural": "coal",
                "emoji": "<:Coal:1509316106203173205>",
            },
            "wither_skeleton_skull": {
                "name": "wither skeleton skull",
                "plural": "wither skeleton skulls",
                "emoji": "<:Wither_Skeleton_Skull:1509316084103381083>",
            },
            "stone_sword": {
                "name": "stone sword",
                "plural": "stone swords",
                "emoji": "<:Stone_Sword:1509316096648413184>",
            },
        }

        self.mob_defs = {
            "blaze": {
                "name": "blaze",
                "plural": "blazes",
                "command": "blaze",
                "emoji": "🔥",
                "stat_name": "Blazes Killed",
                "drops": ["blaze_rod", "glowstone_dust"],
            },
            "ws": {
                "name": "wither skeleton",
                "plural": "wither skeletons",
                "command": "ws",
                "emoji": "<:Wither_Skeleton_Skull:1509316084103381083>",
                "stat_name": "Wither Skeletons Killed",
                "drops": ["bone", "coal", "wither_skeleton_skull", "stone_sword"],
            },
        }

        self.bot.mob_item_defs = self.item_defs
        self.bot.mob_defs = self.mob_defs

    def ensureMobUserData(self, user, mob_key):
        if user.get("items", None) is None:
            user["items"] = {}

        if user.get("loot_bonus", None) is None:
            user["loot_bonus"] = 0

        if user.get(mob_key, None) is None:
            user[mob_key] = {
                "use_total": 0,
                "use_last": 0,
            }

        if "use_total" not in user[mob_key]:
            user[mob_key]["use_total"] = 0

        if "use_last" not in user[mob_key]:
            user[mob_key]["use_last"] = 0

    def getLootBonus(self, user):
        try:
            return max(0, int(user.get("loot_bonus", 0)))
        except:
            return 0

    def addItems(self, user, drops):
        for item_key, amount in drops.items():
            if amount <= 0:
                continue

            user["items"][item_key] = user["items"].get(item_key, 0) + amount

    def formatDropEmojis(self, drops):
        message = ""

        for item_key, amount in drops.items():
            if amount <= 0:
                continue

            message += self.item_defs[item_key]["emoji"] * amount

        if message == "":
            return "No drops."

        return message

    def formatDropText(self, drops):
        parts = []

        for item_key, amount in drops.items():
            if amount <= 0:
                continue

            item_def = self.item_defs[item_key]
            name = item_def["name"] if amount == 1 else item_def["plural"]
            parts.append(f"**{amount}** {name}")

        if not parts:
            return "nothing"

        if len(parts) == 1:
            return parts[0]

        return ", ".join(parts[:-1]) + f", and {parts[-1]}"

    def rollBlazeDrops(self, loot_bonus):
        drops = {
            "blaze_rod": 0,
            "glowstone_dust": 0,
        }
        
        chance = random.random()
        if chance <= 1 / 3:
            drops["glowstone_dust"] = random.randint(1, 2 + loot_bonus)
        
        if 1 / 3 < chance <= 2 / 3:
            drops["blaze_rod"] = random.randint(1, 1 + loot_bonus)
        
        return drops

    def rollWitherSkeletonDrops(self, loot_bonus):
        drops = {
            "bone": random.randint(0, 2 + loot_bonus),
            "coal": 0,
            "wither_skeleton_skull": 0,
            "stone_sword": 0,
        }

        if random.random() < (1 / 3):
            drops["coal"] = random.randint(1, 1 + loot_bonus)

        if random.random() < 0.025:
            drops["wither_skeleton_skull"] = 1

        if random.random() < 0.085:
            drops["stone_sword"] = 1

        return drops

    async def killMob(self, ctx, mob_key, drops):
        self.bot.ensureUserExists(ctx)
        user = self.bot.getUser(ctx)

        self.ensureMobUserData(user, mob_key)
        self.addItems(user, drops)

        user[mob_key]["use_total"] += 1
        user[mob_key]["use_last"] = time.time()

        self.bot.saveData()

        await ctx.send(
            f"{self.formatDropEmojis(drops)}\n"
            f"<@{ctx.author.id}> → you got {self.formatDropText(drops)}."
        )

    @wrapper_command(
        name='blaze',
        description='Fight a blaze and get drops.\n',
        slash=True,
        slash_description='Fight a blaze and get drops.',
        cooldown=MOB_COOLDOWN
    )
    async def blazeCommand(self, ctx):
        self.bot.ensureUserExists(ctx)
        user = self.bot.getUser(ctx)

        self.ensureMobUserData(user, "blaze")

        loot_bonus = self.getLootBonus(user)
        drops = self.rollBlazeDrops(loot_bonus)

        await self.killMob(ctx, "blaze", drops)

    @blazeCommand.error
    @wrapper_error(use_cooldown=True)
    async def blazeCommandError(self, ctx, error):
        pass

    @wrapper_command(
        name='ws',
        description='Fight a wither skeleton and get drops.\n',
        slash=True,
        slash_description='Fight a wither skeleton and get drops.',
        cooldown=MOB_COOLDOWN
    )
    async def witherSkeletonCommand(self, ctx):
        self.bot.ensureUserExists(ctx)
        user = self.bot.getUser(ctx)

        self.ensureMobUserData(user, "ws")

        loot_bonus = self.getLootBonus(user)
        drops = self.rollWitherSkeletonDrops(loot_bonus)

        await self.killMob(ctx, "ws", drops)

    @witherSkeletonCommand.error
    @wrapper_error(use_cooldown=True)
    async def witherSkeletonCommandError(self, ctx, error):
        pass


async def setup(bot):
    await bot.add_cog(MobCog(bot))