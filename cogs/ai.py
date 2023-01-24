# Jerrin Shirks

# native imports
from discord.ext import commands
from pyparsing import ParseException # ,solve
import time

# custom imports
from jerrinth import JerrinthBot
from wrappers import *
from support import *
from cogs.help import HelpCog
from config import *


class AICog(commands.Cog):
    def __init__(self, bot):
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
        TEXT = ctx.message.content[5:]

        """IF IT IS AN EMPTY MESSAGE BRING UP HELP DIALOG"""
        prefix = self.bot.getPrefix(ctx)
        if ctx.super.message.content.lower().strip() == f"{prefix}ai":
            return await HelpCog.displayAIHelpCommand(self, ctx)
        self.ensureUserAIExists(ctx)

        """PARSES ENGINE TYPE"""
        engines = self.bot.ai.engines
        forced_engine = self.bot.getChannel(ctx).get("forced_engine", None)
        if forced_engine is None:  # get the user engine
            ENGINE = self.bot.getUserEngine(ctx, 0)
        else:  # if the channel has a forced engine, use that one instead
            ENGINE = forced_engine

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
        search = re.search(r"f=[etcETC] ", TEXT)
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
                user["last-use"] = time.time()
                user["prompt_tokens"] += response_dict["usage"]["prompt_tokens"]
                user["completion_tokens"] += response_dict["usage"]["completion_tokens"]
                user["total_tokens"] += response_dict["usage"]["total_tokens"]
            except:
                print("Error updating user data")

                embed = errorEmbed("Please try again!\nAn unknown error occurred.")
                return await ctx.send(embed)
            self.bot.saveData()


            # 10%
            # censor the response
            # put code right here to cross-check output
            """CODE THAT DEALS WITH CENSORING THE INPUT/OUTPUT"""
            censor = self.bot.data[ctx.server].get("censorship", True)
            if censor or (censor and not ctx.nsfw):
                temp_response = removeSymbols(response)
                data = f"{TEXT}\n{temp_response}"
                metrics = await self.bot.ai.getModeration(data)
                # pprint.pprint(metrics)
                categories = metrics["results"][0]["category_scores"]

                # hate/threatening
                if categories["hate"] > 0.1 or categories["hate/threatening"] > 0.1:
                    embed = newEmbed("I will not tolerate hate messages. Please do not ask this again.",
                                     color=discord.Color.from_rgb(0, 0, 0))
                    return await ctx.send(embed, reference=True)

                # self-harm
                if categories["self-harm"] > 0.1:
                    if not ctx.nsfw:
                        embed = newEmbed("Content related to self-harm can only be used in NSFW channels.",
                                         color=discord.Color.from_rgb(0, 0, 0))
                        return await ctx.send(embed, reference=True)

                # sexual
                if categories["sexual"] > 0.1:
                    if not ctx.nsfw:
                        embed = newEmbed("Sexual content is only allowed in NSFW channels.",
                                         color=discord.Color.from_rgb(0, 0, 0))
                        return await ctx.send(embed, reference=True)

                # sexual/minors
                if categories["sexual/minors"] > 0.1:
                    if not ctx.nsfw:
                        embed = newEmbed("Sexual content related to children will never be tolerated.\n"
                                         "Please do not ask this again",
                                         color=discord.Color.from_rgb(0, 0, 0))
                        return await ctx.send(embed, reference=True)

                # violence
                if categories["violence"] > 0.1 or categories["violence/graphic"] > 0.1:
                    if not ctx.nsfw:
                        embed = newEmbed("Violent content is only allowed in NSFW channels.",
                                         color=discord.Color.from_rgb(0, 0, 0))
                        return await ctx.send(embed, reference=True)

            """MAKE CODE ENGINES DISPLAY BETTER CODE BLOCKS"""
            if FORMAT == "C":
                languages = ["python", "c++", "java", "rust", "html", "javascript"]
                for language in languages:
                    if language in TEXT:
                        response = f"```{language}\n{response}```"
                        break
                else:
                    response = f"```{response}```"

            """SEND THE RESULTS"""
            if FORMAT in ["T", "C"]:
                segments = splitResponse(response, 2000)
                for n, segment in enumerate(segments):
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
                embed = newEmbed(f"Successfully set engine to **{engines[new_engine]}**")
            else:
                embed = errorEmbed(f"That is an invalid engine! Please choose a number between 1 and {length}.")
            return await ctx.send(embed)

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
                                      f"[Learn more about engine choices here!](https://beta.openai.com/docs/models/overview)\n"
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

        # SHOW THE BOT TYPING WHILE DOING THE BELOW
        async with ctx.super.channel.typing():

            if args == ():
                embed = errorEmbed("You must give me something to solve!")
                await ctx.send(embed)

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

                embed = newEmbed(f"**{answer}**")
                await ctx.send(embed)

            except OverflowError:
                embed = errorEmbed("Not much to say here.", title="Overflow Error")
                await ctx.send(embed)

            except ParseException as e:
                embed = errorEmbed(title="Parsing Error")
                print(e.pstr, e.loc)
                segment = e.pstr[e.loc - 5:e.loc + 9]
                if len(segment) > 10:
                    segment += " ..."

                embed.description = f"```{segment}\n^```"
                await ctx.send(embed)

            except ZeroDivisionError:
                embed = errorEmbed("Ya can't do that!", title="Zero Division Error")
                await ctx.send(embed)

            except Exception as e:
                embed = trophyEmbed(e, title="The answer is definitely 42.")
                await ctx.send(embed)

    @solveEquationCommand.error
    @ctx_wrapper
    async def solveEquationCommandError(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            if self.bot.getServer(ctx).get("show_time_left", True):
                text = f"Try again in **{error.retry_after:.3f}**s."
                await ctx.send(text)
            else:
                await ctx.super.message.add_reaction(convertDecimalToClock(error.retry_after/SOLVE_COOLDOWN[1]))




    @commands.command(name="autocomplete", aliases=["toggleautocomplete", "tac"])
    @ctx_wrapper
    @channel_redirect
    async def autoCompleteCommand(self, ctx, user=None):
        user = argParsePing(user)
        ctx.updateUser(argParsePing(user) if await testAdmin(ctx) else None)
        self.ensureUserAIExists(ctx)

        value = toggleDictBool(self.bot.getUser(ctx)["ai"], "autocomplete", False)
        self.bot.saveData()

        embed = newEmbed(f"Set Autocomplete Mode for <@{ctx.user}> to **{not value}**!")
        await ctx.send(embed)


    @commands.command(name="aifooter", aliases=["af"])
    @ctx_wrapper
    @channel_redirect
    async def setFooterCommand(self, ctx, user=None):
        user = argParsePing(user)
        ctx.updateUser(user if await testAdmin(ctx) else None)
        self.ensureUserAIExists(ctx)

        value = toggleDictBool(self.bot.getUser(ctx)["ai"], "show_footer", False)
        self.bot.saveData()

        embed = newEmbed(f"The AI Embed Footer for <@{ctx.user}> has been toggled to **{not value}**!")
        await ctx.send(embed)


    @commands.command(name="toggleenginehelp", aliases=["teh"])
    @ctx_wrapper
    @channel_redirect
    async def toggleEngineHelpCommand(self, ctx, user=None):
        user = argParsePing(user)
        ctx.updateUser(user if await testAdmin(ctx) else None)
        self.ensureUserAIExists(ctx)

        value = toggleDictBool(self.bot.getUser(ctx)["ai"], "show_engine_help", True)
        self.bot.saveData()

        embed = newEmbed(f"Engine Help for <@{ctx.user}> has been toggled to **{not value}**!")
        await ctx.send(embed)


async def setup(bot):
    await bot.add_cog(AICog(bot))
