import asyncio
import re
import time
from collections import defaultdict
from discord.utils import get


async def find_user(ctx, username: str):
    member = get(ctx.guild.members, name=username)
    if member:
        return member.id
    return 0


class MudaeKeys:
    HOUR = 60 * 60
    DAY = HOUR * 24
    WEEK = DAY * 7
    MONTH = DAY * 30

    def __init__(self, database):
        self.database = database
        self.patterns = {}
        self.add_pattern("keys", r"<:(bronze|silver|gold|chaos)key:\d+> \(\*\*(\d+)\*\*\)")

    def add_pattern(self, key, pattern):
        self.patterns[key] = re.compile(pattern)

    async def add_message(self, ctx, user_name, message):
        timestamp = int(time.time())
        user_id = None
        rows = []

        for key, pattern in self.patterns.items():
            matches = pattern.findall(message)
            if not matches:
                continue

            if user_id is None:
                user_id = await find_user(ctx, user_name)
                if user_id == 0:
                    user_id = str(user_name)
                user_id = str(user_id)

            for match in matches:
                rarity = match[0] if isinstance(match, tuple) else match
                rows.append((user_id, str(key), str(rarity), timestamp))

        if not rows:
            return False

        await asyncio.to_thread(self.database.add_mudae_key_events, rows)
        return True

    async def count_occurrences(self, user_id, key, time_span):
        detailed = await self.count_detailed_matches(user_id, key, time_span)
        total = sum(detailed.values())
        return total, total

    async def count_detailed_matches(self, user_id, key, time_span):
        now = int(time.time())
        cutoff = now - self.MONTH
        await asyncio.to_thread(self.database.delete_old_mudae_keys, cutoff)

        counts = await asyncio.to_thread(
            self.database.count_mudae_keys,
            str(user_id),
            str(key),
            now - int(time_span),
        )
        return defaultdict(int, counts)
