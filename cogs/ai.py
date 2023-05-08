# Jerrin Shirks

# native imports
from pyparsing import ParseException  # for ,solve
import time
import io

# custom imports
from files.jerrinth import JerrinthBot
from files.wrappers import *
from files.support import *
from files.config import *

from funcs.memory import Memory

from cogs.help import HelpCog
from cogs.chat import ChatCog

from funcs.moderation import testModeration


class AICog(commands.Cog, Memory):
    def __init__(self, bot):
        super().__init__(bot)
        self.bot: JerrinthBot = bot

    def ensureUserAIExists(self, ctx):
        self.bot.ensureUserExists(ctx)
        if self.bot.getUser(ctx).get("ai", None) is None:
            self.bot.getUser(ctx)["ai"] = EMPTY_AI.copy()

    @commands.command(name="ai", aliases=['AI', 'Ai', "aI"])
    @discord.ext.commands.cooldown(*AI_COOLDOWN)
    @ctx_wrapper
    @channel_redirect
    async def AICommand(self, ctx):

        """PARSES INPUT TEXT"""
        TEXT = removeFirstWord(ctx.message.content)

        if ctx.message.attachments:
            for attachment in ctx.message.attachments:
                if attachment.content_type == "text/plain; charset=utf-8":
                    max_size = self.bot.settings["max-text-file-size"]
                    if attachment.size > max_size:
                        return await ctx.send(f"File size exceeds the maximum allowed size of {max_size} letters.")
                    text_file = io.StringIO(str(await attachment.read()))
                    TEXT += f"\n\nFile:\n{text_file.getvalue().strip()}"

        """IF IT IS AN EMPTY MESSAGE BRING UP HELP DIALOG"""
        prefix = self.bot.getPrefix(ctx)
        if ctx.super.message.content.lower().strip() in [f"{prefix}ai", f"{prefix}ai help"]:
            return await HelpCog.displayAIHelpCommand(self, ctx)

        self.ensureUserAIExists(ctx)
        self.bot.ensureChannelExists(ctx)

        """PARSES ENGINE TYPE"""
        engines = self.bot.ai.engines
        forced_engine = self.bot.getChannel(ctx).get("forced_engine", None)
        if forced_engine is None:  # get the user engine
            ENGINE = self.bot.getUserEngine(ctx, 0)
        else:  # if the channel has a forced engine, use that one instead
            ENGINE = forced_engine

        """DOES CHATTING INSTEAD OF AI'ING OR SOMETHING"""
        if self.bot.ai.engines[ENGINE] == "gpt-3.5-turbo":
            return await ChatCog.chatCommand(None, ctx)
            # return await self.chatCommand(ctx)

        """PARSES RANDOM TYPE"""
        # gets "r=0", "r=1", "r=0.N"
        search = re.search(r"r=[01]\.?[0-9]? ", TEXT)
        if search:
            re_rand = re.search(r"[0-9](\.[0-9])? ", search.group(0))
            rand = float(re_rand.group(0))
            RANDOM = rand if 0.0 < rand < 1.0 else 1.0
            TEXT = TEXT.replace(search.group(0), "", 1)
        elif "random" in TEXT:
            RANDOM = 1
        else:
            RANDOM = 0

        """PARSES FORMAT TYPE"""
        # gets "f=e", "f=t", "f=c"
        search = re.search(r"f=[etcETC]", TEXT)
        if search:
            re_format = re.search(r"(e)|(t)|(c)|(E)|(T)|(C)", search.group(0))
            FORMAT = re_format.group(0).upper()
            TEXT = TEXT.replace(search.group(0), "", 1)
        else:
            FORMAT = "E"

        """PARSES INPUT TEXT"""
        # appends syntax to end of message, determines if it is a question
        if self.bot.getUser(ctx)["ai"].get("autocomplete", True):
            TEXT = addSyntax(TEXT)

        """SEND DEBUGGING INPUT"""
        if self.bot.getUser(ctx).get("debug", False):
            channel_override: str = "" if forced_engine is None else "(Override)"
            random_num: str = "" if RANDOM == 0 else f"({RANDOM})"
            message = f"\n```FORMAT: '{FORMAT}'" \
                      f"\nRANDOM: {bool(RANDOM)} {random_num}" \
                      f"\nENGINE: {engines[ENGINE]} {channel_override}" \
                      f"\nTEXT  : {filterGarbage(TEXT)[:25]}...```"
            message = removePings(message, allowed=ctx.user)
            await ctx.send(message)

        """SHOW THE BOT TYPING WHILE DOING THE BELOW"""
        async with ctx.super.channel.typing():

            status, response_dict = await self.bot.ai.getResponse(ENGINE, TEXT, RANDOM)

            response = response_dict['choices'][0]['text']
            response = filterGarbage(response)

            """UPDATE USERDATA"""
            try:
                user = self.bot.getUser(ctx)["ai"]
                user["total_uses"] += 1
                user["last_use"] = time.time()
                user["prompt_tokens"] += response_dict["usage"]["prompt_tokens"]
                user["completion_tokens"] += response_dict["usage"]["completion_tokens"]
                user["total_tokens"] += response_dict["usage"]["total_tokens"]
            except:
                print("Error updating user data")
                return await ctx.sendError("Please try again!\nAn unknown error occurred.")
            self.bot.saveData()

            # 10%
            # censor the response
            # put code right here to cross-check output
            """CODE THAT DEALS WITH CENSORING THE INPUT/OUTPUT"""
            status = await testModeration(self, ctx, TEXT, response)
            if status:
                return

            """UPDATES MESSAGE HISTORY OF CHATTING, IF THEY ARE USING THAT"""
            # code here
            self.add_chat_user(ctx, TEXT)
            self.add_chat_assistant(ctx, response)
            self.bot.saveData()

            """SEND THE RESULTS"""
            if FORMAT in ["T", "C"]:
                segments = splitStringIntoSegments(response)
                for n, segment in enumerate(segments):
                    segment = removePings(segment)
                    await ctx.send(segment, reference=(n == 0))

            elif FORMAT == "E":
                engine_type, engine_name, engine_int = engines[ENGINE].split("-")
                engine_footer = f"Engine: {cap(engine_type)} {cap(engine_name)} {engine_int}"

                segments = splitResponse(response, 2000)
                for n, segment in enumerate(segments):
                    embed = newEmbed(description=segment)

                    if n == len(segments) - 1:
                        if self.bot.getUser(ctx)["ai"].get("show_footer", False):
                            embed.set_footer(text=engine_footer)

                    await ctx.send(embed, reference=(n == 0))

    @AICommand.error
    @ctx_wrapper
    async def AICommandError(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            if self.bot.getServer(ctx).get("show_time_left", True):
                text = f"Try again in **{error.retry_after:.3f}**s."
                await ctx.send(text)
            else:
                await ctx.super.message.add_reaction(convertDecimalToClock(error.retry_after / AI_COOLDOWN[1]))

    # need to rewrite for admin
    @commands.command(name="engine", aliases=['e', 'engines', 'setengine'])
    @ctx_wrapper
    @channel_redirect
    async def engineCommand(self, ctx, new_engine: str = None, user: str = None):
        new_engine = argParseInt(new_engine, offset=-1)
        user = argParsePing(user)

        ctx.updateUser(user if await testAdmin(ctx) else None)
        self.ensureUserAIExists(ctx)

        engines = self.bot.ai.engines
        prefix = self.bot.getPrefix(ctx)

        if new_engine is not None:
            length = len(engines)
            if 0 <= new_engine < length:
                self.bot.getUser(ctx)["ai"]["engine"] = new_engine
                self.bot.saveData()
                await ctx.sendEmbed(f"Successfully set engine to **{engines[new_engine]}**")
            else:
                await ctx.sendError(f"That is an invalid engine! Please choose a number between 1 and {length}.")
            return

        embed = newEmbed()

        forced_engine = self.bot.getChannel(ctx).get("forced_engine", None)
        if forced_engine is not None:
            embed.add_field(name="``🔒``Channel Engine Override``🔒``",
                            inline=False,
                            value=f"You are forced to use **``{engines[forced_engine]}``** in this channel.\n"
                                  f"Admins can change this by using **{prefix}channelengine del**")
        else:
            num = self.bot.getUserEngine(ctx)
            embed.add_field(name="User Engine",
                            inline=False,
                            value=f"``{num + 1}. {engines[num]}``")

            if self.bot.getUser(ctx)["ai"].get("show_engine_help", True):
                embed.add_field(name="How to Use",
                                inline=False,
                                value=f"To change engines, use **,engine N**\n"
                                      f"Where N is the index of the engine list.\n"
                                      f"[Learn more about engine choices here!]("
                                      f"https://beta.openai.com/docs/models/overview)\n"
                                      f"_Turn this off by using **{prefix}toggleenginehelp**_")

            embed.add_field(name="Engine List",
                            inline=False,
                            value=makeTable(
                                data=[e.split("-") for e in self.bot.ai.engines],
                                code=[0, 1, 2],
                                show_index=True,
                                direction="center"
                            ))

        await ctx.send(embed)

    @commands.command(name="solve", aliases=["s"])
    @discord.ext.commands.cooldown(*SOLVE_COOLDOWN)
    @ctx_wrapper
    @channel_redirect
    async def solveEquationCommand(self, ctx, *args):
        expression = " ".join(args)

        # print(f"\"{expression}\"")

        # SHOW THE BOT TYPING WHILE DOING THE BELOW
        async with ctx.super.channel.typing():

            if args == ():
                await ctx.sendError("You must give me something to solve!")

            try:
                if expression.replace(" ", "") in ["9+10", "9+(10)", "(9)+10"]:
                    embed = newEmbed(f"**21**")
                    return await ctx.send(embed, reference=True)

                # allows discord code blocks to work
                expression = expression.replace("`", "")
                # makes "()" become "(0)"
                expression = expression.replace("()", "(0)")
                # adds 0's hanging "."'s to make syntax easier
                expression = insert_zero(expression)
                # convert 2(2) to 2*(2)
                expression = insert_star(expression)
                # piggywink exclusive
                expression = expression.replace("•", "*")

                print(expression)

                answer = self.bot.nsp.eval(expression)

                if "." not in expression and str(answer).endswith(".0"):
                    answer = int(answer)

                await ctx.sendEmbed(f"**{answer}**")

            except OverflowError:
                await ctx.sendError("Not much to say here.", title="Overflow Error")

            except ParseException as e:
                embed = errorEmbed(title="Parsing Error")
                print(e.pstr, e.loc)
                segment = e.pstr[e.loc - 5:e.loc + 9]
                if len(segment) > 10:
                    segment += " ..."

                embed.description = f"```{segment}\n^```"
                await ctx.send(embed)

            except ZeroDivisionError:
                await ctx.sendError("Ya can't do that!", title="Zero Division Error")

            except Exception as e:
                embed = trophyEmbed(str(e), title="The answer is definitely 42.")
                await ctx.send(embed)

    @solveEquationCommand.error
    @ctx_wrapper
    @cool_down_error
    async def solveEquationCommandError(self, ctx, error):
        pass

    @commands.command(name="autocomplete", aliases=["toggleautocomplete", "tac"])
    @ctx_wrapper
    @channel_redirect
    async def autoCompleteCommand(self, ctx, user=None):
        user = argParsePing(user)
        ctx.updateUser(argParsePing(user) if await testAdmin(ctx) else None)
        self.ensureUserAIExists(ctx)

        value = toggleDictBool(self.bot.getUser(ctx)["ai"], "autocomplete", False)
        self.bot.saveData()

        await ctx.sendEmbed(f"Set Autocomplete Mode for <@{ctx.user}> to **{not value}**!")

    @commands.command(name="aifooter", aliases=["af"])
    @ctx_wrapper
    @channel_redirect
    async def setFooterCommand(self, ctx, user=None):
        user = argParsePing(user)
        ctx.updateUser(user if await testAdmin(ctx) else None)
        self.ensureUserAIExists(ctx)

        value = toggleDictBool(self.bot.getUser(ctx)["ai"], "show_footer", False)
        self.bot.saveData()

        await ctx.sendEmbed(f"The AI Embed Footer for <@{ctx.user}> has been toggled to **{not value}**!")

    @commands.command(name="toggleenginehelp", aliases=["teh"])
    @ctx_wrapper
    @channel_redirect
    async def toggleEngineHelpCommand(self, ctx, user=None):
        user = argParsePing(user)
        ctx.updateUser(user if await testAdmin(ctx) else None)
        self.ensureUserAIExists(ctx)

        value = toggleDictBool(self.bot.getUser(ctx)["ai"], "show_engine_help", True)
        self.bot.saveData()

        await ctx.sendEmbed(f"Engine Help for <@{ctx.user}> has been toggled to **{not value}**!")


async def setup(bot):
    await bot.add_cog(AICog(bot))
