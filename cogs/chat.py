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

from files.config import *

from funcs.memory import Memory
from funcs.moderation import testModeration


class ChatCog(commands.Cog, Memory):
    def __init__(self, bot):
        super().__init__(bot)
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
                print(attachment.content_type)
                content_types = attachment.content_type.split("; ")
                b1 = "text" in content_types[0]
                b2 = "application/json" == content_types[0]
                b3 = "charset=utf-8" == content_types[1]
                if (b1 or b2) and b3:
                    max_size = self.bot.settings["max-text-file-size"]
                    if attachment.size > max_size:
                        await ctx.sendError(f"File size exceeds the maximum allowed size of {max_size} characters."
                                            f"\nI will ignore `{attachment.filename}`.")
                        continue
                    text_file = io.StringIO(str(await attachment.read()))
                    user_input += f"\n\nFilename:{attachment.filename}\n{text_file.getvalue().strip()}"
                # else:
                    # print(attachment.content_type)
        # else:
            # print("no attachments")

        args = user_input.split()

        if len(args) == 0:
            return await HelpCog.displayHelpCommand(self, ctx, page=4)
        if args[0] == "help":
            return await HelpCog.displayHelpCommand(self, ctx, page=4)

        if args[0] == "load":
            return await self.loadChatHistory(ctx)
        if args[0] == "forget":
            amount = 1 if len(args) == 1 else args[1]
            return await self.forgetChatHistory(ctx, amount + 1)
        if args[0] == "clear":
            return await self.resetChatHistory(ctx)
        if args[0] == "history":
            return await self.viewChatHistory(ctx)
        if args[0] in ["token", "tokens"]:
            return await ctx.sendEmbed(f"**Current Token Size:** {self.get_history_token_size(ctx)}")
        elif args[0] == "prompt":
            return await ctx.sendEmbed(self.get_chat_prompt(ctx), title="Current Prompt")
        elif f"{args[0]}.txt" in self.bot.ai_prompts:
            self.set_person_chat_prompt(ctx, args[0])
            return await ctx.sendEmbed(f"Activated ***{args[0].capitalize()} Mode!***")
        elif args[0] == "resetprompt":
            await self.chatResetSystemMessage(ctx)
            return await self.resetChatHistory(ctx)
        elif args[0] == "setprompt":
            if len(args) > 1:
                await self.chatSetSystemMessage(ctx, ' '.join(args[1:]))
                return await self.resetChatHistory(ctx)
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
            temp_data = deepcopy(self.get_chat_history(ctx))
            temp_data.append({"role": "user", "content": user_input})
            temp_data = self.handle_resizing_memory(ctx, temp_data)

            """GET FORMATTED RESPONSE"""
            logging.info("getting chat message!!!!")
            status, response_dict = await self.bot.ai.getChat(temp_data)
            try:
                response = response_dict['choices'][0]['message']['content']
            except Exception as e:
                return await ctx.sendError(f"Something went wrong, Jerrin is working on a fix!\n"
                                           f"Error: {e}\n{str(response_dict)}")

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
            except Exception as e:
                print("Error updating user data")
                return await ctx.sendError(f"Please try again!\nAn unknown error occurred.\nError: {e}")
            self.bot.saveData()

            """CODE THAT DEALS WITH CENSORING THE INPUT/OUTPUT"""
            logging.info("censorship")
            status = await testModeration(self, ctx, user_input, response)
            if status:
                return

            """UPDATES MESSAGE HISTORY OF CHATTING, IF THEY ARE USING THAT"""
            self.add_chat_user(ctx, user_input)
            self.add_chat_assistant(ctx, response)
            self.bot.saveData()
            self.handle_resizing_memory(ctx)

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

    async def forgetChatHistory(self, ctx, amount: int = 1):
        history = self.bot.getChannel(ctx).get("chatgpt-content", [])

        if len(history) < 2:
            return await ctx.sendError("There is nothing to forget silly!")

        amount = int(amount)
        for a in range(amount):
            if len(history) < 2:
                break
            history.pop(-1)
        self.bot.getChannel(ctx)["chatgpt-content"] = history

        await ctx.sendEmbed(f"Removed {amount} messages from my memory of this channel!")

    async def loadChatHistory(self, ctx):
        if not ctx.message.attachments:
            return await ctx.sendError("BLANK")

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
            prefix = self.bot.getPrefix(ctx)
            await ctx.sendError(f"You didn't send any files called `message_history.json`."
                                f"\nYou can get this file by using `{prefix}chat history`.")


    async def viewChatHistory(self, ctx):
        data = self.get_chat_history(ctx)
        if len(data) > 1:
            file = io.BytesIO(json.dumps(data).encode('utf-8'))
            await ctx.send("This is my message history!", file=discord.File(file, "message_history.json"))
        else:
            await ctx.sendError("There is no prior message history in this channel.")

    async def resetChatHistory(self, ctx):
        self.reset_chat_history(ctx)
        self.bot.saveData()
        await ctx.sendEmbed("I have cleared my history!")

    async def chatResetSystemMessage(self, ctx):
        if "chatgpt-system-message" in self.bot.getChannel(ctx):
            del self.bot.getChannel(ctx)["chatgpt-system-message"]
            await ctx.send(newEmbed(f"I have reset the system prompt to:\n**{self.get_chat_prompt(ctx)}**"))
        else:
            return await ctx.sendError(f"My prompt is already:\n**{self.get_chat_prompt(ctx)}**")

    async def chatSetSystemMessage(self, ctx, content):
        if not content:
            return await ctx.sendError("Cannot set the system prompt to an empty message!")

        content = self.bot.getChannel(ctx).get("chatgpt-system-message", None)
        await ctx.sendEmbed(f"Set system prompt to: \n**{content}**")




async def setup(bot):
    await bot.add_cog(ChatCog(bot))
