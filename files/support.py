# Jerrin Shirks

# native imports
import os
import json
import time

import discord
from discord import ext, RawReactionActionEvent
from discord.ext import commands
import re
import random
import logging
from typing import List, Any, Union, Tuple

from files.discord_objects import CtxObject


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
    except Exception:
        return False


def find_nth(haystack, needle, n):
    start = haystack.find(needle)
    while start >= 0 and n > 1:
        start = haystack.find(needle, start + len(needle))
        n -= 1
    return start


def capitalize(string: str) -> str:
    if string and string[0].isdigit():
        for i, char in enumerate(string):
            if char.isalpha():
                return string[:i] + char.upper() + string[i + 1:]
        return string
    else:
        return string.capitalize()


def print_red(text):
    print(f"\033[91m{text}\033[0m")


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
    except Exception:
        return

    while "" in badwords_init:
        badwords_init.remove("")

    badwords = {}
    for _bad_word in badwords_init:
        badwords[_bad_word] = 0
        badwords[_bad_word.capitalize()] = 0
        badwords[_bad_word.upper()] = 0

        badwords[separate(_bad_word, " ")] = 0
        badwords[separate(_bad_word.capitalize(), " ")] = 0
        badwords[separate(_bad_word.upper(), " ")] = 0

        badwords[separate(_bad_word, "|")] = 0
        badwords[separate(_bad_word.capitalize(), "|")] = 0
        badwords[separate(_bad_word.upper(), "|")] = 0

        badwords[separate(_bad_word, "-")] = 0
        badwords[separate(_bad_word.capitalize(), "-")] = 0
        badwords[separate(_bad_word.upper(), "-")] = 0

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


RED = "\u001b[31m"
RESET = "\u001b[0m"
NOT_ADMIN_MESSAGE = "You do not have admin privileges."
NOT_ADMIN_MESSAGE_1 = "You do not have permission to change this setting."

EMPTY_SETTINGS = {
    # not really necessary
    "data_version": None,  # int
    "last_update": None,  # int
    "channel_log_dm": None,  # channel id: int
    "channel_log_private": None,  # channel id: int
    "imgur_client_id": None,  # token: used for API's
    "discord_token": None,  # token
}


EMPTY_SERVER = {
    "name": None,
    "channels": {},
}

EMPTY_CHANNEL = {
}

EMPTY_USER = {
    "name": None,
    "use_total": 0,
    "use_last": None
}

EMPTY_CHAT = {
    "use_total": 0,
    "use_last": None,
}

EMPTY_PLAYRANDOM = {
    "use_total": 0,
    "use_last": None
}

EMPTY_IMGUR = {
    "use_total": 0,
    "use_last": None
}

EMPTY_FUN = {
    "use_total": 0,
    "use_last": None,
    "eye_count": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
}

EMPTY_SOMEONE = {
    "use_total": 0,
    "use_last": None
}

EMPTY_FINDBLOCK = {
    "use_total": 0,
    "use_last": None,
    "end_portal_count": 0,
}

EMPTY_OBJECT = {
    "use_total": 0,
    "use_last": None
}

EMPTY_ALL = {
    "ai": EMPTY_CHAT.copy(),
    "imgur": EMPTY_IMGUR.copy(),
    "findseed": EMPTY_FUN.copy(),
    "someone": EMPTY_SOMEONE.copy(),
    "playrandom": EMPTY_PLAYRANDOM.copy()
}

def updateUsage(obj: dict):
    obj["use_total"] += 1
    obj["use_last"] = time.time()

def cap(args: str or list or tuple) -> str or list or tuple:
    """capitalizes first letter of arg."""
    if isinstance(args, str):
        return args[0].upper() + args[1:]
    elif type(args) in [list, tuple]:
        return [arg[0].upper() + arg[1:] for arg in args]


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
    except ValueError:
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
    if not isinstance(allowed, list):
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

            # Add a triple backtick to the start of the next substring,
            # along with the previous word after the backticks if there was one
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
