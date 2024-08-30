# Jerrin Shirks

# native imports
from pyparsing import ParseException

# custom imports
from files.jerrinth import JerrinthBot
from files.wrappers import *
from files.support import *
from files.config import *
from files.discord_objects import *
from funcs.nsp import NumericStringParser



def insert_zero(string):
    """for use of ,solve"""
    if "." not in string:
        return string
    result = ""
    for i in range(len(string)):
        if string[i] == "." and not string[i - 1].isdigit():
            result += "0" + string[i]
        elif i == 0 and string[i] == ".":
            result += "0" + string[i]
        else:
            result += string[i]

    return result


def insert_star(string):
    """for use of ,solve"""
    if "(" not in string:
        return string
    new_str = ""
    for i in range(len(string) - 1):
        if string[i].isdigit():
            if string[i + 1] == "(":
                new_str += string[i] + "*"
            else:
                new_str += string[i]
        else:
            new_str += string[i]
    return new_str + string[-1]


class MathCog(commands.Cog):
    def __init__(self, bot):
        self.bot: JerrinthBot = bot
        self.nsp = NumericStringParser()

    @wrapper_command(name="solve", aliases=["s"], cooldown=SOLVE_COOLDOWN)
    async def solveEquationCommand(self, ctx, *args):
        expression = " ".join(args)

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

                # print(expression)

                answer = self.nsp.eval(expression)

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
                await ctx.sendError("Divide by 0 lol.", title="Zero Division Error")

            except Exception as e:
                embed = trophyEmbed(str(e), title="The answer is definitely 42.")
                await ctx.send(embed)

    @solveEquationCommand.error
    @wrapper_error()
    async def solveEquationCommandError(self, ctx, error):
        pass


async def setup(bot):
    await bot.add_cog(MathCog(bot))
