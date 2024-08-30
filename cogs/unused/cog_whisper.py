# Jerrin Shirks

# native imports
from typing import Tuple
import asyncio
import time
import uuid

# custom imports
from files.jerrinth import JerrinthBot
from files.wrappers import *
from files.support import *
from files.config import *
from files.discord_objects import *
from funcs.chatai import CHATAI, Memory


class WhisperCog(commands.Cog):
    def __init__(self, bot):
        self.bot: JerrinthBot = bot
        self.chatai = CHATAI()
        self.dir: str = bot.directory + "data/whisper/"
        self.fix_prompt: str = "Please format the following text/phrase/sentences to " \
                               "include appropriate line breaks and punctuation " \
                               "without modifying any words. If it seems like" \
                               "the text is music, group the lines in stanzas. " \
                               "If it doesn't need any formatting, do nothing " \
                               "to the text, and merely send the text/phrase/sentence " \
                               "back as your response. If you are unsure what to do or it " \
                               "is already formatted, just restate what I say. " \
                               "Here is the text:\n"

    def ensureUserWhisperExists(self, ctx):
        self.bot.ensureUserExists(ctx)
        if self.bot.getUser(ctx).get("whisper", None) is None:
            self.bot.getUser(ctx)["whisper"] = EMPTY_OBJECT.copy()

    @staticmethod
    async def delete_file(filename):
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, os.remove, filename)

    def isValidFile(self, ctx, attachment):
        valid_types = ("mp3", "mp4", "mpeg", "mpga", "m4a", "wav", "webm")
        if not attachment.content_type.endswith(valid_types):
            return False, f"File is not a valid type! " \
                          f"Use **{self.bot.gp(ctx)}help whisper** for more info."
        if attachment.size > WHISPER_MAX_FILE_SIZE:
            return False, "File is too large! It must be below 25MB."
        return True, ""

    async def transcribe_whisper(self, _filename: str) -> str:
        with open(_filename, "rb") as _f:
            result = await self.bot.openai.Audio.atranscribe("whisper-1", _f)
            return result["text"]

    async def fixFormatting(self, content: str) -> Tuple[bool, str]:
        memory = Memory(_prompt=self.fix_prompt)
        memory.addUser(_content=content)

        status, name, response = await self.chatai.getChat(memory)

        # returns early if conversion fails
        if status is False:
            return False, content

        if not isinstance(content, str):
            return False, content

        return True, response

    @wrapper_command(name="whisper", cooldown=WHISPER_COOLDOWN)
    async def whisperCommand(self, ctx, var=""):
        if not ctx.message.attachments:
            return await ctx.sendError("You must send an audio file!")

        format_text, total_steps = [(True, 4), (False, 3)][var.lower() == "raw"]

        for attachment in ctx.message.attachments:
            status, reason = self.isValidFile(ctx, attachment)

            if not status:
                return await ctx.sendError(reason)

            else:
                step = 1
                embed = newEmbed(title=f"Step {step}/{total_steps}",
                                 text="Saving file to my servers...",
                                 color=discord.Color.green())
                message = await ctx.super.send(embed=embed)

                # save the file to the pc temporarily
                extension = attachment.filename.split(".")[-1]
                filename = f"{self.dir}{uuid.uuid4()}.{extension}"

                await ctx.message.attachments[0].save(filename)
                file_saved = True

                step += 1
                embed = newEmbed(title=f"Step {step}/{total_steps}",
                                 text="Transcribing text file...",
                                 color=discord.Color.green())
                await message.edit(embed=embed)

                # send to whisper
                try:
                    text = await self.transcribe_whisper(filename)

                    if format_text:
                        step += 1
                        embed = newEmbed(title=f"Step {step}/{total_steps}",
                                         text="Fixing formatting...",
                                         color=discord.Color.green())
                        await message.edit(embed=embed)

                        status, new_text = await self.fixFormatting(text)
                        if status:
                            text = new_text

                    orig_filename = attachment.filename.replace(" ", "_").replace("_", "\\_")

                    if len(text) < 1950:
                        embed = newEmbed(title=f"{orig_filename}",
                                         description=text,
                                         color=discord.Color.green())
                        await message.edit(embed=embed)

                    else:

                        whisper_dir = self.bot.directory + "data/whisper/whisper.txt"
                        with open(whisper_dir, "w") as file:
                            file.write(text)

                        with open(whisper_dir, "rb") as file:
                            await ctx.super.send("**Whisper Text:**",
                                                 file=discord.File(file, whisper_dir))

                    self.ensureUserWhisperExists(ctx)
                    user = self.bot.getUser(ctx)["whisper"]
                    user["total_uses"] += 1
                    user["last-use"] = time.time()
                    self.bot.saveData()

                    await self.delete_file(filename)

                # fail code
                except Exception as e:
                    print(e)
                    await message.edit(embed=errorEmbed(f"Whisper failed! Reason:\n{e}"))
                    if file_saved:
                        await self.delete_file(filename)

    @whisperCommand.error
    @wrapper_error()
    async def whisperCommandError(self, ctx, error):
        pass


async def setup(bot):
    await bot.add_cog(WhisperCog(bot))
