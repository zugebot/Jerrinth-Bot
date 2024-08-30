# Jerrin Shirks

import discord


DEC_EMOJI = "⬅"
INC_EMOJI = "➡"

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
