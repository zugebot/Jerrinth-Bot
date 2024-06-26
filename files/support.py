# Jerrin Shirks

# native imports
import os
import json
import discord
from discord import ext, RawReactionActionEvent
from discord.ext import commands
import re
import random
import logging
from typing import List, Any, Union, Tuple

FORMAT = '%(asctime)s %(message)s'
logging.basicConfig(format=FORMAT, level=logging.WARNING)


def clear():
    os.system('cls')


def try_make_json(filename, override):
    if not os.path.exists(filename):
        with open(filename, 'w') as fp:
            if override is None:
                fp.write("{}")
            else:
                fp.write(override)


def read_json(filename, override=None):
    try_make_json(filename, override)
    with open(filename, "r") as file:
        return json.loads(file.read())


def save_json(filename, data):
    try:
        with open(filename, "w") as file:
            file.write(json.dumps(data, indent=4))
        return True
    except:
        return False


def find_nth(haystack, needle, n):
    start = haystack.find(needle)
    while start >= 0 and n > 1:
        start = haystack.find(needle, start + len(needle))
        n -= 1
    return start


def filterGarbage(string):
    # remove pings
    string = string.replace("@everyone", "@ everyone")
    string = string.replace("@here", "@ here")
    # remove unnecessary line breaks
    while "\n\n\n" in string:
        string = string.replace("\n\n\n", "\n\n")
    while "```\n\n" in string:
        string = string.replace("```\n\n", "```\n")
    while string.startswith(" "):
        string = string[1:]

    return string


def separate(word, symbol=" "):
    return symbol.join([i for i in word])


# no longer used

def loadBadWords(filename):
    try:
        with open(filename, "r+") as file:
            badwords_init = file.read().splitlines()
    except:
        return

    while "" in badwords_init:
        badwords_init.remove("")

    badwords = {}
    for badword in badwords_init:
        badwords[badword] = 0
        badwords[badword.capitalize()] = 0
        badwords[badword.upper()] = 0

        badwords[separate(badword, " ")] = 0
        badwords[separate(badword.capitalize(), " ")] = 0
        badwords[separate(badword.upper(), " ")] = 0

        badwords[separate(badword, "|")] = 0
        badwords[separate(badword.capitalize(), "|")] = 0
        badwords[separate(badword.upper(), "|")] = 0

        badwords[separate(badword, "-")] = 0
        badwords[separate(badword.capitalize(), "-")] = 0
        badwords[separate(badword.upper(), "-")] = 0

    return badwords


BADWORDS_FILE = "data/badwords.txt"
BADWORDS = loadBadWords(BADWORDS_FILE)


def removeBadWords(string):
    count = 0
    if string == "":
        return "I have no response."
    for i in BADWORDS:
        if i in string:
            count += string.count(i)
            string = string.replace(i, "#" * len(i))
    return string, count


def removeSymbols(string: str):
    output: str = ""
    last_space = 0
    for n, i in enumerate(string):
        if i == " ":
            if n - last_space > 2:
                output += i
                last_space = n
                continue

        if i.isalpha():
            output += i

    return output


def codeBlock(item):
    return f"```{item}```"


def newEmbed(text: str = "", color=discord.Color.purple(), **kwargs):
    if text != "":
        kwargs["description"] = text
    return discord.Embed(**kwargs, color=color)


def errorEmbed(text: str = "", **kwargs):
    if text != "":
        kwargs["description"] = text
    return discord.Embed(**kwargs, color=discord.Color.red())


def trophyEmbed(text: str = "", **kwargs):
    if text != "":
        kwargs["description"] = text
    return discord.Embed(**kwargs, color=discord.Color.yellow())


async def testAdmin(ctx) -> bool:
    if ctx.message.author.id == 611427346099994641:  # jerrin's main account
        return True
    return bool(ctx.message.author.guild_permissions.administrator)


def makeTable(data,
              boldRow: int or list[int] = None,
              boldCol: int or list[int] = None,
              code: int or list[int] = None,
              sep: int or dict = None,
              show_index: bool = False,
              direction: int or str = 0,
              debug: bool = False) -> str:
    """
    :param data: a list of objects, lists, or other data.
    :param boldRow: real
    :param boldCol: real
    :param code: horizontal indexes of items that should be surrounded by ``.
    :param sep: dict of horizontal indexes with str's to separate args.
    :param show_index: a bool that adds an index to the first item if true.
    :param direction: justifies or centers text in code blocks this direction.
    :param debug: prints stuff to terminal
    :return: A table of all represented data parsed with above arguments.
    """

    # parsing data
    if data is []:
        return None
    if not isinstance(data, list):
        data = [data]

    # parsing boldRow
    if boldRow is None:
        boldRow = []
    if isinstance(boldRow, int):
        boldRow = [boldRow]

    # parsing boldCol
    if boldCol is None:
        boldCol = []
    if isinstance(boldCol, int):
        boldCol = [boldCol]

    # parsing code
    if code is None:
        code = []
    if isinstance(code, int):
        code = [code]

    # parsing sep arg
    if sep is None:
        sep = {}
    if isinstance(sep, int):
        sep = [sep]

    # 0: right, 1: left, 2: center
    # parsing direction arg
    if isinstance(direction, str):
        if direction.lower() in ["r", "right"]:
            direction = 0
        elif direction.lower() in ["l", "left"]:
            direction = 1
        elif direction.lower() in ["c", "center"]:
            direction = 2
    elif not isinstance(direction, int):
        direction = 0

    # step 1
    # make sure that every item in the data is a list
    # also get the longest list in data
    max_size = 0
    for index, item in enumerate(data):
        if type(item) == tuple:
            item = list(item)

        if isinstance(item, list):
            size = len(item)
        else:
            item = [item]
            size = 0

        if size > max_size:
            max_size = size

        data[index] = item

    # step 2
    # make sure every item in data is the same length
    show_index_length = len(str(len(data)))
    if show_index:
        max_size += 1
        code = [i + 1 for i in code]
        code.insert(0, 0)

    for index, item in enumerate(data):
        if show_index:
            item.insert(0, f"{index + 1}.".rjust(show_index_length))

        if len(item) < max_size:
            to_add = max_size - len(item)
            data[index].extend([None] * to_add)

    # step 3
    # this gets the longest items per vertical index
    line_segments = len(data[0])
    max_length_list = []

    for index in range(line_segments):
        max_length = 0

        for item in range(len(data)):
            if data[item][index] is None:
                continue

            length: int = len(str(data[item][index]))
            if length > max_length:
                max_length = length

        max_length_list.append(max_length)

    # step 3.5
    if debug:
        for i in data:
            print(i)
        print("lengths", max_length_list)
        print("boxed", code)
        input()

    # final step 4
    final_string = []
    for index, item in enumerate(data, start=0):
        string: str = ""

        is_code_block = False

        # add each segment
        for seg_index in range(max_size):
            seg_part = ""

            segment = data[index][seg_index]

            if segment is None:
                segment = ""

            # if current is NOT block and last is block <3
            elif not is_code_block and seg_index in code:
                seg_part += "``"

            is_code_block = seg_index in code

            # add the main part of the string
            if direction == 0:  # right
                seg_part += f"{str(segment).rjust(max_length_list[seg_index])}"
            elif direction == 1:  # left
                seg_part += f"{str(segment).ljust(max_length_list[seg_index])}"
            elif direction == 2:  # center
                seg_part += f"{str(segment).center(max_length_list[seg_index])}"

            # add if this is code block but next isn't, finishing it
            if seg_index in code and seg_index + 1 not in code:
                seg_part += "``"

            # vertical bold
            if seg_index in boldCol:
                seg_part = f"**{seg_part}**"

            string += seg_part

            # add the spacer
            if seg_index < line_segments:

                if seg_index in sep:
                    if data[index][seg_index + 1] is None:
                        string += " " * len(sep[seg_index])
                    else:
                        string += f"{sep[seg_index]}"
                else:
                    string += " "

        if index in boldRow:
            string = f"**{string}**"

        final_string.append(string)

    text = "\n".join(final_string)
    return text


RED = "\u001b[31m"
RESET = "\u001b[0m"
NOT_ADMIN_MESSAGE = "You do not have admin privileges."
NOT_ADMIN_MESSAGE_1 = "You do not have permission to change this setting."

RESPONSES_8BALL = ["It is certain.",
                   "It is decidedly so.",
                   "Without a doubt.",
                   "Yes definitely.",
                   "You may rely on it.",
                   "As I see it, yes.",
                   "Most likely.",
                   "Outlook good.",
                   "Yes.",
                   "Signs point to yes.",
                   "Reply hazy, try again.",
                   "Ask again later.",
                   "Better not tell you now.",
                   "Cannot predict now.",
                   "Concentrate and ask again.",
                   "Don't count on it.",
                   "My reply is no.",
                   "My sources say no.",
                   "Outlook not so good.",
                   "Very doubtful."]

BAD_RESPONSES_8BALL = ["Do you participate in the contest of the most useless questions?",
                       "Please ask a real question please.",
                       "I do not understand."]

EMPTY_SETTINGS = {
    # not really necessary
    "data_version": None,  # int
    "last_update": None,  # int
    # used for yes
    "channel_log_dm": None,  # channel id: int
    "channel_log_private": None,  # channel id: int
    # used for api's
    "imgur_client_id": None,  # token
    "discord_token": None,  # token
}

EMPTY_SERVER = {
    "name": None,
    "prefix": ',',
    "channels": {},
    "users": {}
}

EMPTY_CHANNEL = {
}

EMPTY_USER = {
    "name": None,
}

EMPTY_AI = {
    "prompt_tokens": 0,
    "completion_tokens": 0,
    "total_tokens": 0,
    "total_uses": 0,
    "last_use": None
}

EMPTY_PLAYRANDOM = {
    "total_uses": 0,
    "last_use": None
}

EMPTY_IMGUR = {
    "total_uses": 0,
    "last_use": None
}

EMPTY_FUN = {
    "eye_count": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    "total_uses": 0,
    "last_use": None
}

EMPTY_SOMEONE = {
    "total_uses": 0,
    "last_use": None
}

EMPTY_OBJECT = {
    "total_uses": 0,
    "last_use": None
}

EMPTY_ALL = {
    "ai": EMPTY_AI.copy(),
    "imgur": EMPTY_IMGUR.copy(),
    "findseed": EMPTY_FUN.copy(),
    "@someone": EMPTY_SOMEONE.copy(),
    "playrandom": EMPTY_PLAYRANDOM.copy()
}

TIPS = [
    "I often give much better answers if you end your questions with the correct punctuation!",
    "I am not complete up to date to the times! My training ends somewhere in 2021.",
    "You can use me to cheat on your english essays!",
    "Different Engines are made for different questions. Try Changing it with the **,engine** command!",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
]

SHOW_SYNTAX = [
    "Add some syntax!",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
]

DEC_EMOJI = "⬅"
INC_EMOJI = "➡"


def cap(args: str or list or tuple) -> str or list or tuple:
    """capitalizes first letter of arg."""
    if isinstance(args, str):
        return args[0].upper() + args[1:]
    elif type(args) in [list, tuple]:
        return [arg[0].upper() + arg[1:] for arg in args]


class ctxObject:
    def __init__(self, ctx, **kwargs):
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
                try:
                    self.nsfw = ctx.channel.nsfw_level
                except:
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
        await self.send(embed, allowed_mentions, reference)

    async def sendEmbed(self, *args, **kwargs):
        allowed_mentions = kwargs.get("allowed_mentions", False)
        if "allowed_mentions" in kwargs:
            kwargs.pop("allowed_mentions")
        reference = kwargs.get("reference", None)
        if "reference" in kwargs:
            kwargs.pop("reference")

        embed = newEmbed(*args, **kwargs)
        await self.send(embed, allowed_mentions, reference)


class ButtonMenu(discord.ui.View):
    def __init__(self, pages, index=0, timeout=180, user=None):
        super().__init__(timeout=timeout)
        self.pages = pages
        self.user = user
        self.message = None

        self.index = index
        self.length = len(pages)

    async def send(self, ctx):
        content, embeds, files = await self.getPage()

        self.message = await ctx.super.send(
            content=content,
            embeds=embeds,
            view=self
        )

    async def on_timeout(self):
        if self.message:
            await self.message.delete()

        await super().on_timeout()

    async def getPage(self):
        page = self.pages[self.index]
        if isinstance(page, str):
            return page, [], []
        elif isinstance(page, discord.Embed):
            return None, [page], []
        elif isinstance(page, discord.File):
            return None, [], [page]
        elif isinstance(page, list):
            items = [None, [], []]
            for item in page:
                if isinstance(item, str):
                    items[0] = item
                elif isinstance(item, discord.Embed):
                    items[1].append(item)
                elif isinstance(item, discord.File):
                    items[2].append(item)
            """
            if all(isinstance(x, discord.Embed) for x in page):
                return None, page, []
            if all(isinstance(x, discord.File) for x in page):
                return None, [], page
            else:
                raise TypeError("Can't have alternative files")
            """
            return tuple(items)

    async def showPage(self, interaction: discord.Interaction):
        content, embeds, files = await self.getPage()

        await interaction.response.edit_message(
            content=content,
            embeds=embeds,
            attachments=files or [],
            view=self
        )

    @discord.ui.button(emoji=DEC_EMOJI, style=discord.ButtonStyle.grey)
    async def inc_page(self, interaction, button):
        self.index = (self.index - 1) % self.length
        await self.showPage(interaction)

    @discord.ui.button(emoji=INC_EMOJI, style=discord.ButtonStyle.grey)
    async def dec_page(self, interaction, button):
        self.index = (self.index + 1) % self.length
        await self.showPage(interaction)


def getLongest(values):
    largest = 0
    for arg in values:
        if isinstance(arg, list):
            for segment in arg:
                if isinstance(segment, int):
                    value = len(str(segment))
                    largest = value if value > largest else largest
        elif isinstance(arg, int):
            value = len(str(arg))
            largest = value if value > largest else largest
    return largest


def formatData(values, _length):
    for arg in values:
        yield [str(i).rjust(_length) for i in arg]


def argParsePing(arg, excluded: list[str] = None):
    if excluded is not None:
        if arg in excluded:
            return arg

    if arg is None:
        return None

    nums = re.findall("[0-9]{15,20}", arg)
    if nums:
        return int(nums[0])
    else:
        return None


def argParseInt(arg, offset: int = 0) -> int or None:
    if arg is None:
        return None
    try:
        return int(arg) + offset
    except:
        return None


def splitResponse(response, split_size):
    if len(response) < split_size:
        return [response]

    return [response[i:i + split_size] for i in range(0, len(response), split_size)]


def splitResponse2(response, split_size):
    segments = []

    while len(response) > split_size:
        segment = response[:split_size]

        index = segment[::-1].find("\n")
        if index == -1:
            index = segment[::-1].find(" ")
            if index == -1:
                index = 0

        segment = segment[:split_size - index]

        segments.append(segment)
        response = response[len(segment):]

    return segments


def addSyntax(text: str) -> str:
    """appends syntax to end of text, determines if it is a question"""
    if text[-1] not in "?.!":
        is_question = False
        lower_text = text.lower()
        for word in ["who", "what", "where", "why", "how", "will", "can", "top"]:
            if word in lower_text:
                is_question = True
        if is_question:
            text += "?"
        else:
            text += "."

    return text


def toggleDictBool(dictionary: dict, tag: str, default=True) -> bool:
    """toggles a bool value in a dictionary by deleting it if it is the default value, as to save space."""
    value = dictionary.get(tag, default)
    if value == default:
        dictionary[tag] = not default
    else:
        dictionary.pop(tag, None)
    return value


FISH = [fish for fish in "🐠🐟🦐🦞🦀🦑🐙🐬🐳🦈🎣🐡"]


def convertDecimalToClock(decimal: float = None) -> str:
    clocks = "🕛🕚🕙🕘🕗🕖🕕🕔🕓🕒🕑🕐"
    if decimal is None:
        decimal = random.random()
    index = int(decimal * 12)
    return clocks[index]


def removePings(string: str, allowed: List[str] = None) -> str:
    if allowed is None:
        allowed = []
    elif not isinstance(allowed, list):
        allowed = list(allowed)

    result = ''
    i = 0
    while i < len(string):
        if string[i] == '@':
            matched_allowed = None
            for allowed_item in allowed:
                if string.startswith(allowed_item, i + 1):
                    matched_allowed = allowed_item
                    break

            if matched_allowed:
                result += string[i:i + len(matched_allowed) + 1]
                i += len(matched_allowed) + 1
                continue
            else:
                result += '@ '
                i += 1
                continue
        result += string[i]
        i += 1
    return result


def tryConvertToCodeBlock(content):
    languages = ["python", "c++", "java", "rust", "html", "javascript", "node",
                 "c#", "go", "dart", "haskell", "kotlin", "lua", "perl"]
    for language in languages:
        if language in content:
            content = f"```{language}\n{content}```"
            break
    else:
        content = f"```{content}```"
    return content


def anti_markdown(content):
    pass


def removeFirstWord(string):
    index = 0
    while index < len(string):
        if string[index] == " ":
            break
        index += 1
    if index != len(string):
        string = string[index:]
    return string


def renameFileToLength(filename, length):
    if "." not in filename:
        return filename[:length]
    file_pieces = filename.split(".")
    first = ".".join(file_pieces[:-1])
    last = file_pieces[-1]
    first = first[:length - min(len(last), 4)]
    last = last[:4]
    return f"{first}.{last}"


def splitStringIntoSegments(input_string: str,
                            split_size: int = 1980,
                            block: str = "```"):
    """
    First splits by '\n', then if none are found, split by ' '.
    It might split code blocks correctly.
    :param block:
    :type block:
    :param split_size:
    :type split_size:
    :param input_string:
    :type input_string:
    :return:
    :rtype:
    """

    fallback_index = 0
    result = []
    while len(input_string) > split_size:
        index = split_size
        found_newline = False
        while index > 0:
            if input_string[index] == '\n':
                found_newline = True
                break
            elif not found_newline and input_string[index] == ' ':
                fallback_index = index
            index -= 1
        if not found_newline:
            index = fallback_index

        # Check if the substring contains an odd number of triple backticks
        triple_backticks_count = input_string[:index].count(block)
        if triple_backticks_count % 2 != 0:

            # Find the word directly after the first triple backtick
            triple_backtick_index = input_string[:index].rfind(block)
            word_after_backticks = input_string[triple_backtick_index + 3:].split("\n")[0]
            if not (len(word_after_backticks.strip()) > 2):
                word_after_backticks = None

            # Add a triple backtick to the end of the current substring
            result.append(input_string[:index] + "```")

            # Add a triple backtick to the start of the next substring, along with the previous word after the backticks if there was one
            if word_after_backticks:
                input_string = f"{block}{word_after_backticks}\n" + input_string[index:]
            else:
                input_string = block + input_string[index:]

        else:

            # Add the substring to the list of strings
            result.append(input_string[:index])
            input_string = input_string[index:]

    # Add the remaining string to the list
    result.append(input_string)
    return result
