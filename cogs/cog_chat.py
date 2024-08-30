# Jerrin Shirks

# native imports
import time
import io
from copy import deepcopy

# custom imports
from files.jerrinth import JerrinthBot
from files.wrappers import *
from files.support import *
from cogs.cog_help import makeHelpMenu
from files.buttonMenu import ButtonMenu
from files.discord_objects import *

from files.config import *

from funcs.chatai import Memory, CHATAI


# from funcs.memory import Memory
# from old_code.moderation import testModeration


class ChatCog(commands.Cog):
    def __init__(self, bot):
        super().__init__()
        self.bot: JerrinthBot = bot
        self.chatai = CHATAI()
        self.MAX_TEXT_FILE_SIZE = 12288

        prompt = self.bot.ai_prompt_dict.get("default", None)
        if prompt is not None:
            Memory.DEFAULT_PROMPT = prompt
        else:
            Memory.DEFAULT_PROMPT = "You are a helpful assistant."

    def ensureUserAIExists(self, ctx):
        self.bot.ensureUserExists(ctx)
        if self.bot.getUser(ctx).get("chat", None) is None:
            self.bot.getUser(ctx)["chat"] = EMPTY_CHAT.copy()

    @wrapper_command(name="chat", aliases=["<@856411268633329684>"], cooldown=CHAT_COOLDOWN)
    async def chatCommand(self, ctx):

        self.ensureUserAIExists(ctx)
        self.bot.ensureChannelExists(ctx)

        if " " not in ctx.message.content:
            return await ctx.sendError("You gotta ask me something silly!")

        """PARSES INPUT TEXT"""
        user_input: str = removeFirstWord(ctx.message.content)

        if ctx.message.attachments:
            for attachment in ctx.message.attachments:
                print(attachment.content_type)
                content_types = attachment.content_type.split("; ")
                b1 = "text" in content_types[0]
                b2 = "application/json" == content_types[0]
                b3 = "charset=utf-8" == content_types[1]
                if (b1 or b2) and b3:
                    max_size = self.MAX_TEXT_FILE_SIZE
                    if attachment.size > max_size:
                        await ctx.sendError(f"File size exceeds the maximum allowed size of {max_size} characters."
                                            f"\nI will ignore `{attachment.filename}`.")
                        continue
                    text_file = io.StringIO(str(await attachment.read()))
                    user_input += f"\n\nFilename:{attachment.filename}\n{text_file.getvalue().strip()}"

        parse_args = user_input.split()

        if parse_args[0] == "load":
            return await self.loadChatHistory(ctx)

        if len(parse_args) == 0:
            return await makeHelpMenu(self, ctx.super, page=4)
        elif len(parse_args) == 1:
            if parse_args[0] == "help":
                return await makeHelpMenu(self, ctx.super, page=4)
            if parse_args[0] == "clear":
                return await self.resetChatHistory(ctx)
            if parse_args[0] == "prompt":
                prompt = self.getPrompt(ctx)
                segments = splitResponse(prompt, split_size=1000)

                pages = [newEmbed(text=segment, title=f"Current Prompt {n + 1}/{len(segments)}")
                         for n, segment in enumerate(segments)]
                menu = ButtonMenu(pages, index=0, timeout=180)
                try:
                    await ctx.super.send(embed=pages[0], view=menu)
                except discord.errors.Forbidden:
                    return

                return
            if parse_args[0] == "history":
                return await self.viewChatHistory(ctx)
            if parse_args[0] in ["token", "tokens"]:
                prompt = self.getPrompt(ctx)
                return await ctx.sendEmbed(
                    f"**Prompt Tokens:** {Memory.countTokens(Memory.DEFAULT_PROMPT if prompt == 'default' else prompt)}"
                    f"\n**Total Tokens:** {self.getMemory(ctx).getHistoryTokenSize()}"
                )
            if parse_args[0] == "resetprompt":
                reset = await self.chatResetSystemMessage(ctx)
                if reset:
                    return await self.resetChatHistory(ctx)
                return
            if f"{parse_args[0]}.txt" in self.bot.ai_prompts:
                self.setPersonChatPrompt(ctx, parse_args[0])
                return await ctx.sendEmbed(f"Activated ***{parse_args[0].capitalize()} Mode!***")
        else:
            if parse_args[0] == "help":  # TODO
                return await makeHelpMenu(self, ctx.super, page=4)
            if parse_args[0] == "forget":
                amount = 1 if len(parse_args) == 1 else parse_args[1]
                return await self.forgetChatHistory(ctx, amount)
            if parse_args[0] == "setprompt":
                if len(parse_args) > 1:
                    await self.chatSetSystemMessage(ctx, ' '.join(parse_args[1:]))
                    return await self.resetChatHistory(ctx)

        self.bot.saveData()

        prefix = self.bot.gp(ctx)
        if ctx.super.message.content.lower().strip() == f"{prefix}chat":
            pass

        """PARSES INPUT TEXT"""
        logging.info("parses text")
        # appends syntax to end of message, determines if it is a question
        if self.bot.getUser(ctx)["chat"].get("autocomplete", True):
            user_input = addSyntax(user_input)

        """SEND DEBUGGING INPUT"""
        logging.info("debug text")
        debug_message: discord.Message
        debug_text = ""
        if self.bot.getUser(ctx).get("debug", False):
            debug_text = f"\nTEXT: {filterGarbage(user_input)[:25]}...```"
            debug_text = removePings(debug_text, allowed=ctx.user)
            debug_message = await ctx.send("```" + debug_text)

        """SHOW THE BOT TYPING WHILE DOING THE BELOW"""
        async with ctx.super.channel.typing():

            """HERE WE CONSTRUCT THE DATA"""
            logging.info("parses data for memory")

            memory = self.getMemory(ctx)
            temp_mem = Memory(deepcopy(memory.getMessages()))

            prompt = self.getPrompt(ctx)
            if prompt == "default":
                temp_mem.addUser(f"<@{ctx.user}>", user_input)
            else:
                temp_mem.addUser("", user_input)

            temp_mem.resizeMemory()

            """GET FORMATTED RESPONSE"""
            logging.info("getting chat message!!!!")
            status, response = await self.chatai.getChat(temp_mem)
            response = response.replace("GPT-3.5:", "")

            if not status:
                if isinstance(response, str):
                    return await ctx.sendError(f"Error: {response[:2000]}")
                return await ctx.sendError(f"Error Type: RequestInfo\n{response}")

            # if debug_message is not None:
            #     try:
            #         await debug_message.edit(content=f"```{debug_text}")
            #     except:
            #         ""

            response = f"{filterGarbage(response)}"

            """UPDATE USERDATA"""
            logging.info("update user data")
            user = self.bot.getUser(ctx)["chat"]
            user["use_total"] += 1
            user["use_last"] = time.time()
            self.bot.saveData()

            """CODE THAT DEALS WITH CENSORING THE INPUT/OUTPUT"""
            logging.info("censorship")
            # status = await testModeration(self, ctx, user_input, response)
            # if status:
            #     return

            """UPDATES MESSAGE HISTORY OF CHATTING, IF THEY ARE USING THAT"""
            memory.addUser(f"{ctx.user}", user_input)
            memory.addAssistant(response)
            memory.resizeMemory()
            self.setMemory(ctx, memory)
            self.bot.saveData()

            """SEND THE RESULTS"""
            logging.info("sending results")
            segments = splitStringIntoSegments(response)
            for n, segment in enumerate(segments):
                segment = removePings(segment, allowed=ctx.user)
                await ctx.send(segment, reference=(n == 0))

    @chatCommand.error
    @wrapper_error()
    async def chatCommandError(self, ctx: CtxObject, error):
        if isinstance(error, commands.CommandOnCooldown):
            return await ctx.send(reference=True, message=errorEmbed(error.args[0]))

        await ctx.sendError("This command has been recently reworked."
                            "\nPlease report this bug and the following error to my DMs:"
                            f"\nError: {error.args}")

    def getPrompt(self, ctx):
        prompt = self.bot.getChannel(ctx).get("chatgpt-system-message", "default")
        return prompt

    def getMemory(self, ctx) -> Memory:
        return Memory(self.bot.getChannel(ctx).get("chatgpt-content", None))

    def setMemory(self, ctx, memory: Memory) -> None:
        self.bot.getChannel(ctx)["chatgpt-content"] = memory.getDict()

    def setPersonChatPrompt(self, ctx, name):
        with open(self.bot.directory + f"data/prompts/{name}.txt", "r", encoding='utf-8') as f:
            self.bot.getChannel(ctx)["chatgpt-system-message"] = f.read()

    async def forgetChatHistory(self, ctx, amount: int = 1):
        memory = Memory(self.bot.getChannel(ctx).get("chatgpt-content", None))

        if memory.getSize() < 2:
            return await ctx.sendError("There is nothing to forget silly!")

        amount = int(amount)
        for a in range(amount):
            if memory.getSize() < 2:
                break
            memory.removeLast()

        self.setMemory(ctx, memory)
        await ctx.sendEmbed(f"Removed **{amount}** messages from my memory of this channel!")

    # TODO: needs to be tested
    async def loadChatHistory(self, ctx):
        if not ctx.message.attachments:
            prefix = self.bot.gp(ctx)
            return await ctx.sendError("You need to send a file named 'message_history.json' obtained from the "
                                       f"**{prefix}chat history** command.")

        for attachment in ctx.message.attachments:
            filename = attachment.filename
            if filename != "message_history.json":
                continue
            text_file = io.BytesIO(await attachment.read())
            str_data = text_file.getvalue().decode('utf-8')
            json_data = json.loads(str_data)

            self.bot.getChannel(ctx)["chatgpt-content"] = json_data
            self.bot.saveData()
            await ctx.sendEmbed("Successfully loaded our previous conversation!")
            break
        else:
            prefix = self.bot.gp(ctx)
            await ctx.sendError(f"You didn't send any files called `message_history.json`."
                                f"\nYou can get this file by using `{prefix}chat history`.")

    # TODO: needs to be tested
    async def viewChatHistory(self, ctx):
        prompt = self.getPrompt(ctx)
        memory = self.getMemory(ctx).getDict()
        if len(memory) < 2:
            await ctx.sendError("There is no prior message history in this channel.")
            return

        memory[0]["content"] = prompt
        file = io.BytesIO(json.dumps(memory).encode('utf-8'))
        await ctx.send("This is my message history!", file=discord.File(file, "message_history.json"))

    async def resetChatHistory(self, ctx):
        if "chatgpt-content" in self.bot.getChannel(ctx):
            del self.bot.getChannel(ctx)["chatgpt-content"]
        self.bot.saveData()
        await ctx.sendEmbed("I have cleared my history!")

    # TODO: needs to be tested
    async def chatResetSystemMessage(self, ctx) -> bool:
        if "chatgpt-system-message" in self.bot.getChannel(ctx):
            del self.bot.getChannel(ctx)["chatgpt-system-message"]
            prompt = self.getPrompt(ctx)
            if prompt == "default":
                await ctx.send(newEmbed(f"I am already using my default prompt, so no need to reset it!"))
                return False
            else:
                await ctx.send(newEmbed(f"I have reset the system prompt back to it's default."))
                return True
        else:
            await ctx.send(newEmbed(f"I am already using my default prompt, so no need to reset it!"))
            return False

    async def chatSetSystemMessage(self, ctx, content):
        if not content:
            return await ctx.sendError("Cannot set the system prompt to an empty message!")

        self.bot.getChannel(ctx)["chatgpt-system-message"] = content
        await ctx.sendEmbed(f"Set system prompt to: \n**{content}**")


async def setup(bot):
    await bot.add_cog(ChatCog(bot))
