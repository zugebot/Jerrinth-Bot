# Jerrin Shirks

# native imports

# custom imports
from files.jerrinth import JerrinthBot
from files.mudaeKeys import MudaeKeys
from files.wrappers import *
from files.config import *
from files.support import *
from files.makeTable import makeTable
from discord.utils import get
from enum import Enum
import asyncio
import re


class MudaeMessage(Enum):
    TEXT = 1
    EMBED_LIST = 2
    EMBED_ROLL = 3
    EMBED_ROLL_KEY = 4


class MudaeStatsCog(commands.Cog):
    def __init__(self, bot):
        print(f"loading '{self.__module__}'")

        self.bot: JerrinthBot = bot

        self.bot.hooks_on_message[847402389698641940] = self.on_message
        self.bot.hooks_on_bot_edit_message[847402389698641940] = self.on_message_edit

        self.timespans = {
            "hour": MudaeKeys.HOUR,
            "day": MudaeKeys.DAY,
            "week": MudaeKeys.WEEK,
            "month": MudaeKeys.MONTH
        }

        self.keys = MudaeKeys(self.bot)

        self.key_emojis = {
            "bronze": "<:BronzeSoulKey:1509278500949987369>",
            "silver": "<:SilverSoulKey:1509278517823803542>",
            "gold": "<:GoldSoulKey:1509278530293203094>",
            "chaos": "<:ChaosSoulKey:1509278554456723487>",
        }
        
        """self.kakera_emojis = {
            'kakerap': '<:KakeraP:1509267312442736743>',
            'kakera' : '<:Kakera:1509267285108592770>',
            'kakerat': '<:KakeraT:1509267260135702558>',
            'kakerag': '<:KakeraG:1509267239218581504>',
            'kakeray': '<:KakeraY:1509267218016239717>',
            'kakerao': '<:KakeraO:1509267195652472932>',
            'kakerar': '<:KakeraR:1509267169819492352>',
            'kakeraw': '<:KakeraW:1509267148256579654>',
            'kakeral': '<:KakeraL:1509267124630192268>',
            'kakerad': '<:KakeraD:1509267051095654473>',
            'kakerac': '<:KakeraC:1509267333388964054>',
        }"""

        self.kakera_emojis = {
            'kakerap': '🟪',
            'kakera' : '🔷',
            'kakerat': '🟦',
            'kakerag': '🟩',
            'kakeray': '🟨',
            'kakerao': '🟧',
            'kakerar': '🟥',
            'kakeraw': '⏹️',
            'kakeral': '⬜',
            'kakerad': '⬛',
            'kakerac': '🔳',
        }

        self.low_value_kakera_keys = {
            "kakerap",
            "kakera",
            "kakerat",
            "kakerag",
            "kakeray",
        }

        self.kakera_display_to_key = {
            value: key for key, value in self.kakera_emojis.items()
        }

        self.id_jerrin = 611427346099994641
        self.id_frik = 145244703397380096
        self.id_mudae = 432610292342587392
        soulmate_data = self.bot.load_soulmates()
        self.soulmates_jerrin = set(soulmate_data.get("jerrin", []))
        self.soulmates_frik = set(soulmate_data.get("frik", []))

        self.index_pattern = pattern = re.compile(r"\d+\s*/\s*\d+")
        self.waifu_missing = self.bot.load_waifus()


    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        """
        if before.author.id != self.id_mudae:
            print("Not mudae?")
            return

        await before.channel.send(content="Mudae edited their message lol???")
        """

    async def on_message(self, ctx: CtxObject) -> None:
        if ctx.userInt != self.id_mudae:
            return

        is_roll = True
        belongs_to = False

        if not len(ctx.message.embeds):
            return
        else:
            embed = ctx.message.embeds[0]
            footer = embed.footer.text

            if footer is not None:
                if self.index_pattern.search(footer):
                    is_roll = False
                if "Belongs to" in footer:
                    belongs_to = True

        if is_roll and belongs_to:
            embed = ctx.message.embeds[0]
            text = embed.description
            footer = embed.footer.text
            username = footer.split("Belongs to ")[-1]

            await self.sendSoulmateWarning(ctx)

            await self.keys.add_message(ctx.super, username, text)

        if is_roll and not belongs_to:
            waifu = embed.author.name
            entry = self.waifu_missing.get(waifu, None)
            if entry is not None:
                key_count = entry[1]

                emojis = [":brown_square:", ":white_large_square:", ":yellow_square:", ":purple_square:"]
                if key_count < 3:
                    emoji = emojis[0]
                elif key_count < 6:
                    emoji = emojis[1]
                elif key_count < 10:
                    emoji = emojis[2]
                else:
                    emoji = emojis[3]

                if key_count < 10:
                    await ctx.send(f"# {emoji} {key_count} {emoji}, one of jerrin's!",
                                   reference=True)
                else:
                    await ctx.send(f"# {emoji} {key_count} {emoji} <@{self.id_jerrin}> claim your missing soulmate!",
                                   reference=True)

    def cleanKakeraEmojiName(self, emoji) -> str:
        emoji_name = getattr(emoji, "name", None)

        if emoji_name is None:
            emoji_name = str(emoji)

        emoji_name = str(emoji_name).strip()

        # Handles strings like ":kakeraY:"
        if emoji_name.startswith(":") and emoji_name.endswith(":"):
            emoji_name = emoji_name[1:-1]

        # Handles strings like "<:kakeraY:123456789>"
        match = re.match(r"<?a?:?([A-Za-z0-9_]+):(?:\d+)?>?", emoji_name)
        if match:
            emoji_name = match.group(1)

        return emoji_name.lower()

    def getKakeraButtonItems(self, message: discord.Message):
        items = []

        for row in getattr(message, "components", []):
            for button in getattr(row, "children", []):
                emoji = getattr(button, "emoji", None)

                if emoji is None:
                    continue

                raw_text = str(emoji).strip()
                clean_key = self.cleanKakeraEmojiName(emoji)

                if clean_key in self.kakera_emojis:
                    items.append((clean_key, self.kakera_emojis[clean_key]))

                elif raw_text in self.kakera_display_to_key:
                    real_key = self.kakera_display_to_key[raw_text]
                    items.append((real_key, raw_text))

                else:
                    # Unknown emoji. Show it, but do not treat it as low value.
                    items.append((None, raw_text))

        return items

    def getButtonText(self, message: discord.Message) -> str:
        button_items = self.getKakeraButtonItems(message)
        return ", ".join(display for _, display in button_items)

    def allKakeraButtonsYellowOrLower(self, button_items) -> bool:
        if not button_items:
            return False

        return all(
            clean_key in self.low_value_kakera_keys
            for clean_key, _ in button_items
        )

    def isStarwishEmbed(self, embed: discord.Embed) -> bool:
        footer = getattr(getattr(embed, "footer", None), "text", "") or ""

        # Mudae footer checkmark means starwish.
        return "☑" in footer or "✅" in footer

    def getKeyCountFromEmbed(self, embed: discord.Embed) -> int:
        footer = getattr(getattr(embed, "footer", None), "text", "") or ""
        description = getattr(embed, "description", "") or ""

        # Normal footer examples:
        # (🔑 5)
        # (🔑 27)
        # Starwish footer example:
        # (⭐ 50)
        footer_match = re.search(r"(?:🔑|🗝️|🗝|⭐)\s*(\d+)", footer)
        if footer_match:
            return int(footer_match.group(1))

        # Fallback for description lines like:
        # (48) +5% kakera value
        description_matches = re.findall(
            r"\((\d+)\)\s*\+?\d+(?:\.\d+)?%\s+kakera value",
            description,
            flags=re.IGNORECASE
        )

        if description_matches:
            return max(int(value) for value in description_matches)

        return 0

    def getKakeraPowerPercent(self, key_count: int, button_count: int, is_soulmate: bool = False):
        if button_count <= 0:
            return None

        power = 30

        # Soulmate halves it again.
        if is_soulmate:
            power /= 2

        # 4+ kakera buttons halves it again.
        if button_count >= 4:
            power /= 2

        return power

    def formatPercent(self, value) -> str:
        return f"{value:g}"

    async def sendSoulmateWarning(self, ctx):
        if not len(ctx.message.embeds):
            return

        embed = ctx.message.embeds[0]
        author = embed.author.name

        author = author.lower() \
            .strip() \
            .strip("\n") \
            .replace("\n", " ")

        while "   " in author:
            author = author.replace("  ", " ")

        user_id = None

        if author in self.soulmates_jerrin:
            user_id = self.id_jerrin

        elif author in self.soulmates_frik:
            user_id = self.id_frik

        if user_id is None:
            return

        button_items = self.getKakeraButtonItems(ctx.message)
        button_text = ", ".join(display for _, display in button_items)

        key_count = self.getKeyCountFromEmbed(embed)
        power_percent = self.getKakeraPowerPercent(
            key_count,
            len(button_items),
            is_soulmate=True
        )

        is_starwish = self.isStarwishEmbed(embed)
        suppress_mentions = self.allKakeraButtonsYellowOrLower(button_items)

        label = "Starwish" if is_starwish else "Soulmate"

        message = f"<@{user_id}> {label}! Click The Kakera!"

        if power_percent is not None:
            message += f" ({self.formatPercent(power_percent)}% each)"

        if button_text:
            message += f"\nButtons: {button_text}"

        send_kwargs = {
            "reference": ctx.message
        }

        if suppress_mentions:
            send_kwargs["allowed_mentions"] = discord.AllowedMentions.none()

        await ctx.message.channel.send(
            message,
            **send_kwargs
        )

    @wrapper_command(
        name="keys",
        description="Show key gains over a time span.\n",
        slash=True,
        slash_description="Show key gains over a time span.",
        slash_user_ids=[
            611427346099994641, 
            145244703397380096,
            1031058250512220161,
            1185376303256436742,
            720111245327466517,
            1185375479742595220,
        ],
        slash_channel_ids=[
            1025203045748973639
        ],
        slash_args=[
            {
                "name": "timespan",
                "description": "Span like hour/day/week/month or number of hours.",
                "type": "string",
                "required": False
            },
            {
                "name": "user",
                "description": "User to check (optional).",
                "type": "user",
                "required": False
            }
        ]
    )
    async def testInSet(self, ctx: CtxObject, timespan=None, user_id=None):
        if user_id is not None:
            ctx.updateUser(user_id)

        footer_time = "last day"
        duration_seconds = MudaeKeys.DAY

        if timespan is not None:
            timespan = str(timespan).lower().strip()

            if timespan in self.timespans:
                duration_seconds = self.timespans[timespan]
                footer_time = f"last {timespan}"

            elif timespan.isdigit():
                hours = int(timespan)
                duration_seconds = hours * MudaeKeys.HOUR

                if hours == 1:
                    footer_time = "last hour"
                else:
                    footer_time = f"last {hours} hours"

            else:
                duration_seconds = MudaeKeys.DAY
                footer_time = "last day"

        matches = await self.keys.count_detailed_matches(ctx.user, "keys", duration_seconds)

        table = makeTable(data=[
            [self.key_emojis["bronze"], matches.get("bronze", 0)],
            [self.key_emojis["silver"], matches.get("silver", 0)],
            [self.key_emojis["gold"], matches.get("gold", 0)],
            [self.key_emojis["chaos"], matches.get("chaos", 0)],
        ],
            bold_col=[1],
            sep={0: " - "}
        )

        embed = discord.Embed(description=table)
        user_obj = await self.bot.fetch_user(ctx.user)
        embed.set_footer(text=f"{user_obj.name}'s keys gained {footer_time}")
        await ctx.send(embed)

    def parseSoulmateItems(self, text: str):
        if text is None:
            return []

        text = str(text).strip()

        if text == "":
            return []

        items = re.split(r"\s*\$\s*", text)

        cleaned = []
        seen = set()

        for item in items:
            item = re.sub(r"\s+", " ", item).strip().lower()

            if item == "":
                continue

            if item not in seen:
                cleaned.append(item)
                seen.add(item)

        return cleaned

    def getSoulmateCommandText(self, ctx: CtxObject, command_name: str, items=None) -> str:
        content = getattr(getattr(ctx, "message", None), "content", None)

        if content is not None:
            content = str(content).strip()
            prefix = self.bot.gp(ctx)
            raw_command = f"{prefix}{command_name}"

            content_lower = content.lower()
            raw_command_lower = raw_command.lower()

            if content_lower == raw_command_lower:
                return ""

            if content_lower.startswith(raw_command_lower + " "):
                return content[len(raw_command):].strip()

        if items is None:
            return ""

        return str(items).strip()

    async def saveSoulmatesForUser(self, user_id: int, items):
        items = sorted(set(items))

        if user_id == self.id_frik:
            owner_key = "frik"
        elif user_id == self.id_jerrin:
            owner_key = "jerrin"
        else:
            return False

        await asyncio.to_thread(self.bot.replace_soulmates, owner_key, items)

        if owner_key == "frik":
            self.soulmates_frik = set(items)
        else:
            self.soulmates_jerrin = set(items)
        return True

    def getSoulmatesForUser(self, user_id: int):
        if user_id == self.id_frik:
            return self.soulmates_frik

        if user_id == self.id_jerrin:
            return self.soulmates_jerrin

        return None

    @wrapper_command(
        name='ssml',
        description="Set your soulmate list.\n",
        slash=True,
        slash_description="Set your soulmate list.",
        slash_args=[
            {
                "name": "items",
                "description": "Items separated by '$'.",
                "type": "string",
                "required": True
            }
        ],
        slash_user_ids=[
            611427346099994641,
            145244703397380096,
            1031058250512220161,
            1185376303256436742,
            720111245327466517,
            1185375479742595220,
        ],
        slash_channel_ids=[
            1025203045748973639
        ],
        
    )
    async def setSoulMates(self, ctx: CtxObject, items=None):
        if ctx.userInt not in [self.id_jerrin, self.id_frik]:
            return await ctx.send("Non VIP users must pay to use this command.")

        text = self.getSoulmateCommandText(ctx, "ssml", items)
        items = self.parseSoulmateItems(text)

        if len(items) == 0:
            return await ctx.send("Cannot set soulmate list to nothing. Use csml if you want to clear it.")

        await self.saveSoulmatesForUser(ctx.userInt, items)

        await ctx.send("Set: " + " $ ".join(items))
        await ctx.message.add_reaction("✅")

    @wrapper_command(
        name='asml',
        description="Add items to your soulmate list.\n",
        slash=True,
        slash_description="Add items to your soulmate list.",
        slash_args=[
            {
                "name": "items",
                "description": "Items separated by '$'.",
                "type": "string",
                "required": True
            }
        ],
        slash_user_ids=[
            611427346099994641,
            145244703397380096,
            1031058250512220161,
            1185376303256436742,
            720111245327466517,
            1185375479742595220,
        ],
        slash_channel_ids=[
            1025203045748973639
        ],
    )
    async def addSoulMates(self, ctx: CtxObject, items=None):
        if ctx.userInt not in [self.id_jerrin, self.id_frik]:
            return await ctx.send("Non VIP users must pay to use this command.")

        text = self.getSoulmateCommandText(ctx, "asml", items)
        items = self.parseSoulmateItems(text)

        if len(items) == 0:
            return await ctx.send("Must give at least one character to add.")

        soulmates = self.getSoulmatesForUser(ctx.userInt)

        if soulmates is None:
            return await ctx.send("Could not find your soulmate list.")

        added = []
        already_had = []

        for item in items:
            if item in soulmates:
                already_had.append(item)
            else:
                soulmates.add(item)
                added.append(item)

        await self.saveSoulmatesForUser(ctx.userInt, soulmates)

        message = ""

        if len(added):
            message += "Added: " + " $ ".join(added)

        if len(already_had):
            if message:
                message += "\n"
            message += "Already had: " + " $ ".join(already_had)

        await ctx.send(message)
        await ctx.message.add_reaction("✅")

    @wrapper_command(
        name='csml',
        description="Clear your soulmate list.\n",
        slash=True,
        slash_description="Clear your soulmate list.",
        slash_user_ids=[
            611427346099994641,
            145244703397380096,
            1031058250512220161,
            1185376303256436742,
            720111245327466517,
            1185375479742595220,
        ],
        slash_channel_ids=[
            1025203045748973639
        ],
    )
    async def clearSoulMates(self, ctx: CtxObject):
        if ctx.userInt not in [self.id_jerrin, self.id_frik]:
            return await ctx.send("Non VIP users must pay to use this command.")

        await self.saveSoulmatesForUser(ctx.userInt, [])

        await ctx.send("Soulmate list cleared.")
        await ctx.message.add_reaction("✅")

    @wrapper_command(
        name="vsml",
        description="View your soulmate list.\n",
        slash=True,
        slash_description="View your soulmate list.",
        slash_user_ids=[
            611427346099994641,
            145244703397380096,
            1031058250512220161,
            1185376303256436742,
            720111245327466517,
            1185375479742595220,
        ],
        slash_channel_ids=[
            1025203045748973639
        ],
    )
    async def viewSoulMates(self, ctx: CtxObject):
        if ctx.userInt not in [self.id_jerrin, self.id_frik]:
            return await ctx.send("Non VIP users must pay to use this command.")

        soulmates = self.getSoulmatesForUser(ctx.userInt)

        if soulmates is None or len(soulmates) == 0:
            return await ctx.send("Soulmate list is empty.")
        
        text =" $ ".join(sorted(list(soulmates)))
        print("MESSAGE_LENGTH:", len(text))
        chunks = splitResponse2(text, 1900)
        for chunk in chunks:
            await ctx.send(chunk)
            await asyncio.sleep(0.5)
        
    @wrapper_command(
        name='rsml',
        description="Remove items from your soulmate list.\n",
        slash=True,
        slash_description="Remove items from your soulmate list.",
        slash_args=[
            {
                "name": "items",
                "description": "Items separated by '$'.",
                "type": "string",
                "required": True
            }
        ],
        slash_user_ids=[
            611427346099994641,
            145244703397380096,
            1031058250512220161,
            1185376303256436742,
            720111245327466517,
            1185375479742595220,
        ],
        slash_channel_ids=[
            1025203045748973639
        ],
    )
    async def removeSoulMates(self, ctx: CtxObject, items=None):
        if ctx.userInt not in [self.id_jerrin, self.id_frik]:
            return await ctx.send("Non VIP users must pay to use this command.")

        text = self.getSoulmateCommandText(ctx, "rsml", items)
        items = self.parseSoulmateItems(text)

        if len(items) == 0:
            return await ctx.send("Must give at least one character to remove.")

        soulmates = self.getSoulmatesForUser(ctx.userInt)

        if soulmates is None:
            return await ctx.send("Could not find your soulmate list.")

        removed = []
        missing = []

        for item in items:
            if item in soulmates:
                soulmates.remove(item)
                removed.append(item)
            else:
                missing.append(item)

        await self.saveSoulmatesForUser(ctx.userInt, soulmates)

        message = ""

        if len(removed):
            message += "Removed: " + " $ ".join(removed)

        if len(missing):
            if message:
                message += "\n"
            message += "Not in list: " + " $ ".join(missing)

        await ctx.send(message)
        await ctx.message.add_reaction("✅")

    @wrapper_command(
        name='isml',
        description="Check if characters are in your soulmate list.\n",
        slash=True,
        slash_description="Check if characters are in your soulmate list.",
        slash_args=[
            {
                "name": "items",
                "description": "Characters separated by '$'.",
                "type": "string",
                "required": True
            }
        ],
        slash_user_ids=[
            611427346099994641,
            145244703397380096,
            1031058250512220161,
            1185376303256436742,
            720111245327466517,
            1185375479742595220,
        ],
        slash_channel_ids=[
            1025203045748973639
        ],
    )
    async def checkSoulMates(self, ctx: CtxObject, items=None):
        if ctx.userInt not in [self.id_jerrin, self.id_frik]:
            return await ctx.send("Non VIP users must pay to use this command.")

        text = self.getSoulmateCommandText(ctx, "isml", items)
        items = self.parseSoulmateItems(text)

        if len(items) == 0:
            return await ctx.send("Must give at least one character to check.")

        soulmates = self.getSoulmatesForUser(ctx.userInt)

        if soulmates is None:
            return await ctx.send("Could not find your soulmate list.")

        found = []
        missing = []

        for item in items:
            if item in soulmates:
                found.append(item)
            else:
                missing.append(item)

        message = ""

        if len(found):
            message += "In list: " + " $ ".join(found)

        if len(missing):
            if message:
                message += "\n"
            message += "Not in list: " + " $ ".join(missing)

        await ctx.send(message)
        

    @wrapper_command(
        name="pin",
        aliases=["pins"],
        description="Show pins from a message.\n",
        slash=True,
        slash_description="Show pins from a message.",
        slash_args=[
            {
                "name": "message_id",
                "description": "Message ID to scan (optional).",
                "type": "string",
                "required": False
            }
        ],
        slash_user_ids=[
            611427346099994641,
            145244703397380096,
            1031058250512220161,
            1185376303256436742,
            720111245327466517,
            1185375479742595220,
        ],
        slash_channel_ids=[
            1025203045748973639
        ],
    )
    async def viewPins(self, ctx: CtxObject, message_id=None):
        try:

            if message_id is not None and isinstance(message_id, str) and message_id.isdigit():
                message_id = int(message_id)

            if message_id is not None:
                message = await ctx.message.channel.fetch_message(message_id)
            else:
                message = await ctx.message.channel.fetch_message(ctx.message.reference.message_id)

            matches = re.findall(r'\b\w*?pin\d+\b', message.content)
            sorted_matches = sorted(matches, key=lambda x: int(re.search(r'\d+$', x).group()))

            base = 10
            items_list = []
            for n, i in enumerate(sorted_matches):
                if n < base:
                    items_list.append([i + " $"])
                else:
                    items_list[n % base].append(i + " $")

            for i in items_list:
                i[-1] = i[-1].removesuffix(" $ ")

            table = makeTable(data=items_list, direction=0)
            try:
                await ctx.message.delete()
            except:
                ""
            ctx.super.message.id = ctx.message.reference.message_id
            return await ctx.sendEmbed(f"```{table}```", reference=True)
        except:
            try:
                await ctx.message.delete()
            except:
                ""
            return await ctx.send("Must reply to a message with pins, or an error occured.")


async def setup(bot):
    await bot.add_cog(MudaeStatsCog(bot))
