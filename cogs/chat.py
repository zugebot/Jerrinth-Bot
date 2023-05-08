# Jerrin Shirks

# native imports
from copy import deepcopy
import time
import io

# custom imports
from files.jerrinth import JerrinthBot
from files.wrappers import *
from files.support import *
from cogs.help import HelpCog
# from cogs.chat import ChatCog
from files.config import *

from funcs.moderation import testModeration


class ChatCog(commands.Cog):
    def __init__(self, bot):
        self.bot: JerrinthBot = bot

    def ensureUserAIExists(self, ctx):
        self.bot.ensureUserExists(ctx)
        if self.bot.getUser(ctx).get("ai", None) is None:
            self.bot.getUser(ctx)["ai"] = EMPTY_AI.copy()

    @commands.command(name="chat")
    @discord.ext.commands.cooldown(*CHAT_COOLDOWN)
    @ctx_wrapper
    @channel_redirect
    async def chatCommand(self, ctx):

        self.ensureUserAIExists(ctx)
        self.bot.ensureChannelExists(ctx)

        """PARSES INPUT TEXT"""
        user_input = removeFirstWord(ctx.message.content)

        if ctx.message.attachments:
            for attachment in ctx.message.attachments:
                if attachment.content_type == "text/plain; charset=utf-8":
                    max_size = self.bot.settings["max-text-file-size"]
                    if attachment.size > max_size:
                        return await ctx.send(f"File size exceeds the maximum allowed size of {max_size} letters.")
                    text_file = io.StringIO(str(await attachment.read()))
                    user_input += f"\n\nFilename:{attachment.filename}\n{text_file.getvalue().strip()}"

        args = user_input.split()

        if len(args) == 0:
            return await HelpCog.displayHelpCommand(self, ctx, page=4)
        if args[0] == "help":
            return await HelpCog.displayHelpCommand(self, ctx, page=4)

        if args[0] == "forget":
            amount = 1 if len(args) == 1 else args[1]
            return await self.forgetChatHistory(ctx, amount)
        if args[0] == "clear":
            return await self.chatResetHistory(ctx)
        if args[0] == "history":
            return await self.chatViewHistory(ctx)
        elif args[0] == "prompt":
            return await self.chatShowPrompt(ctx)
        elif f"{args[0]}.txt" in self.bot.ai_prompts:
            self._setPersonChatPrompt(ctx, args[0])
            embed = newEmbed(f"Activated ***{args[0].capitalize()} Mode!***")
            return await ctx.send(embed)
        elif args[0] == "resetprompt":
            await self.chatResetSystemMessage(ctx)
            return await self.chatResetHistory(ctx)
        elif args[0] == "setprompt":
            if len(args) > 1:
                await self.chatSetSystemMessage(ctx, ' '.join(args[1:]))
                return await self.chatResetHistory(ctx)
        self.bot.saveData()

        prefix = self.bot.getPrefix(ctx)
        if ctx.super.message.content.lower().strip() == f"{prefix}chat":
            pass

        """PARSES INPUT TEXT"""
        logging.info("parses text")
        # appends syntax to end of message, determines if it is a question
        if self.bot.getUser(ctx)["ai"].get("autocomplete", True):
            user_input = addSyntax(user_input)

        """SEND DEBUGGING INPUT"""
        logging.info("debug text")
        if self.bot.getUser(ctx).get("debug", False):
            message = f"```\nENGINE: {'chat-3.5-turbo'}" \
                      f"\nTEXT  : {filterGarbage(user_input)[:25]}...```"
            message = removePings(message, allowed=ctx.user)
            await ctx.send(message)

        """LIMIT USER INPUT SIZE"""
        user_input = f"<@{ctx.user}>: {user_input[:4050]}"

        """SHOW THE BOT TYPING WHILE DOING THE BELOW"""
        async with ctx.super.channel.typing():

            """HERE WE CONSTRUCT THE DATA"""
            logging.info("parses data for memory")
            temp_data = deepcopy(self._getChatHistory(ctx))
            temp_data.append({"role": "user", "content": user_input})
            temp_data = self.handleResizingMemory(ctx, temp_data)

            """GET FORMATTED RESPONSE"""
            logging.info("getting chat message!!!!")
            status, response_dict = await self.bot.ai.getChat(temp_data)
            try:
                response = response_dict['choices'][0]['message']['content']
            except Exception as e:
                embed = errorEmbed(
                    f"Something went wrong, Jerrin is working on a fix!\nError: {e}\n{str(response_dict)}")
                return await ctx.send(embed)

            response = filterGarbage(response)

            """UPDATE USERDATA"""
            logging.info("update user data")
            try:
                user = self.bot.getUser(ctx)["ai"]
                user["total_uses"] += 1
                user["last_use"] = time.time()
                user["prompt_tokens"] += response_dict["usage"]["prompt_tokens"]
                user["completion_tokens"] += response_dict["usage"]["completion_tokens"]
                user["total_tokens"] += response_dict["usage"]["total_tokens"]
            except:
                print("Error updating user data")
                embed = errorEmbed("Please try again!\nAn unknown error occurred.")
                return await ctx.send(embed)
            self.bot.saveData()

            """CODE THAT DEALS WITH CENSORING THE INPUT/OUTPUT"""
            logging.info("censorship")
            status = await testModeration(self, ctx, user_input, response)
            if status:
                return

            """UPDATES MESSAGE HISTORY OF CHATTING, IF THEY ARE USING THAT"""
            self._addChatUser(ctx, user_input)
            self._addChatAssistant(ctx, response)
            self.bot.saveData()
            self.handleResizingMemory(ctx)

            """SEND THE RESULTS"""
            logging.info("sending results")
            segments = splitStringIntoSegments(response)
            for n, segment in enumerate(segments):
                segment = removePings(segment, allowed=ctx.user)
                await ctx.send(segment, reference=(n == 0))

    @chatCommand.error
    @ctx_wrapper
    @cool_down_error
    async def ChatCommandError(self, ctx, error):
        pass

    def _countTokens(self, text):
        return len(self.bot.ai.encoding.encode(text))

    def _getChatPrompt(self, ctx):
        # gcode
        return self.bot.getChannel(ctx).get("chatgpt-system-message",
                                            "You are a helpful discord chatbot, named Alex. You are not "
                                            "allowed to refer to yourself as a machine learning model, or as a AI "
                                            "language model. If you are tempted to, just don't write that sentence "
                                            "involving stating it. "
                                            "\n"
                                            "Every message I send will start like this: 'USER: MESSAGE', where USER is "
                                            "the discord username of the person who sent the message. Whenever the "
                                            "user talks about themselves, I want you to relate that information to "
                                            "their name. Feel free to mention them in every message. The way you do "
                                            "this, is by sending '<@NUMBER> '. "
                                            "\n"
                                            "If your messages involve answering general questions, but is not related "
                                            "to math/coding, I want you to add emojis to your response; they should "
                                            "relate to the content of your message. Try to not use the same emojis "
                                            "every message."
                                            "\n"
                                            "Whenever a user asks you to write code, I want you to surround code in "
                                            "your response with symbols that look like this:"
                                            "\n"
                                            "```LANGUAGE\nCODE``` "
                                            "\n"
                                            "where 'CODE' is the code you plan to send, and 'LANGUAGE' is a "
                                            "lowercase string that is the language of the code you are responding "
                                            "with. Do not assume they want you to write code unless they explicitly "
                                            "ask for it."
                                            "\n"
                                            "If you are asked something involving solving "
                                            "mathematics, you must "
                                            "go step by step, and explain each step, and format any line of math, "
                                            "denoted as MATH, to look like this:"
                                            "\n1. add '```gcode'"
                                            "\n2. add MATH"
                                            "\n3. add '```'"
                                            "\nwhich looks like this: ```gcode\nMATH```. "
                                            "You should always add the 'gcode' to the content, regardless of how the "
                                            "user formats their message. There cannot be a space between "
                                            "'```' and 'gcode'."
                                            "where 'MATH' is the math that you planned to say in that step. ")

    def _setPersonChatPrompt(self, ctx, name):
        with open(f"data/prompts/{name}.txt", "r", encoding='utf-8') as f:
            self.bot.getChannel(ctx)["chatgpt-system-message"] = f.read()

    def _getChatHistory(self, ctx) -> list:
        data = self.bot.getChannel(ctx).get("chatgpt-content", [None])
        data[0] = {"role": "system", "content": self._getChatPrompt(ctx)}
        return data

    def _addChatUser(self, ctx, content):
        data = self._getChatHistory(ctx)
        data.append({"role": "user", "content": content})
        self.bot.getChannel(ctx)["chatgpt-content"] = data

    def _addChatAssistant(self, ctx, content):
        data = self._getChatHistory(ctx)
        data.append({"role": "assistant", "content": content})
        self.bot.getChannel(ctx)["chatgpt-content"] = data

    def _getHistoryTokenSize(self, ctx, data=None):
        if data is None:
            data = self._getChatHistory(ctx)
        token_count = [0] * len(data)

        for index, content in enumerate(data):
            token_count[index] = self._countTokens(content["content"])

        total = sum(token_count)
        print("History Tokens:", total, token_count)

        return total

    def _resetChatHistory(self, ctx):
        if "chatgpt-content" in self.bot.getChannel(ctx):
            del self.bot.getChannel(ctx)["chatgpt-content"]

    async def forgetChatHistory(self, ctx, amount: int = 1):
        history = self.bot.getChannel(ctx).get("chatgpt-content", [])

        if len(history) < 2:
            embed = errorEmbed("There is nothing to forget silly!")
            return await ctx.send(embed)

        amount = int(amount)
        for a in range(amount):
            if len(history) < 2:
                break
            history.pop(-1)
        self.bot.getChannel(ctx)["chatgpt-content"] = history

        embed = newEmbed(f"Removed {amount} messages from my memory of this channel!")
        await ctx.send(embed)

    def handleResizingMemory(self, ctx, temp_data=None):
        if temp_data is None:
            data = self._getChatHistory(ctx)
        else:
            data = temp_data

        token_count = [0] * len(data)
        for index, content in enumerate(data):
            token_count[index] = self._countTokens(content["content"])

        to_remove = 0
        while sum(token_count) > 3900:
            to_remove += 1
            token_count.pop(0)

        while to_remove > 0:
            to_remove -= 1
            data.pop(1)

        if temp_data is None:
            self.bot.getChannel(ctx)["chatgpt-content"] = data
            self.bot.saveData()
        else:
            return data

    async def chatViewHistory(self, ctx):
        data = self._getChatHistory(ctx)

        if len(data) > 1:
            content = f"Prompt: {data[0]['content']}\n\n"
            for message in data[1:]:
                content += f"{message['role'].ljust(9)} # {message['content']}\n"

            with open("data/message_history.txt", "w") as file:
                file.write(content)

            with open("data/message_history.txt", "rb") as file:
                await ctx.super.send("**Message History:**", file=discord.File(file, "data/message_history.txt"))

        else:
            embed = errorEmbed("There is no prior message history in this channel.")
            return await ctx.send(embed)

        # embed.description = desc
        # await ctx.send(embed)

    async def chatResetHistory(self, ctx):
        self._resetChatHistory(ctx)
        self.bot.saveData()
        embed = newEmbed("I have cleared my history!")
        await ctx.send(embed)

    async def chatResetSystemMessage(self, ctx):
        if "chatgpt-system-message" in self.bot.getChannel(ctx):
            del self.bot.getChannel(ctx)["chatgpt-system-message"]
            await ctx.send(newEmbed(f"I have reset the system prompt to:\n**{self._getChatPrompt(ctx)}**"))
        else:
            return await ctx.send(errorEmbed(f"My prompt is already:\n**{self._getChatPrompt(ctx)}**"))

    async def chatSetSystemMessage(self, ctx, content):
        if not content:
            embed = errorEmbed("Cannot set the system prompt to an empty message!")
            return await ctx.send(embed)

        self.bot.getChannel(ctx)["chatgpt-system-message"] = content
        embed = newEmbed(f"Set system prompt to: \n**{content}**")
        await ctx.send(embed)

    @channel_redirect
    async def chatShowPrompt(self, ctx):
        embed = newEmbed(title="Current Prompt")
        embed.description = self._getChatPrompt(ctx)
        await ctx.send(embed)

    @commands.command(name="chattokens")
    @ctx_wrapper
    @channel_redirect
    async def chatShowTokens(self, ctx):
        token_count = self._getHistoryTokenSize(ctx)
        embed = newEmbed(f"**Current Token Size:** {token_count}")
        await ctx.send(embed)


async def setup(bot):
    await bot.add_cog(ChatCog(bot))
