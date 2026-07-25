import asyncio
import discord
from typing import Literal, Optional, Union, List

DEC_EMOJI = "◀️"
INC_EMOJI = "▶️"
DEL_EMOJI = "✖️"
VIDEO_EXTS = (".mp4", ".webm", ".mov")

CloseMode = Literal["delete", "detach", "disable"]
PageType = Union[str, discord.Embed, discord.File, List[Union[str, discord.Embed, discord.File]]]

class ButtonMenu(discord.ui.View):
    def __init__(self, pages, index: int = 0, timeout: Optional[float] = 180,
                 user: Optional[discord.abc.User] = None, *,
                 close_mode: CloseMode = "disable",
                 delete_on_timeout: bool = False,
                 owner_only: bool = True,
                 hide_nav_for_single: bool = True):
        super().__init__(timeout=timeout)
        self.pages: List[PageType] = self._normalize_pages(pages)
        self.user = user
        self.message: Optional[discord.Message] = None

        self.index = max(0, min(index, len(self.pages) - 1))
        self.length = len(self.pages)

        self.close_mode = close_mode
        self.delete_on_timeout = delete_on_timeout
        self.owner_only = owner_only
        self.hide_nav_for_single = hide_nav_for_single

        self._build_items()

    # ---------- helpers ----------
    def _normalize_pages(self, pages):
        if isinstance(pages, list):
            return pages if pages else [""]
        return [pages]

    def _build_items(self):
        self.clear_items()
        show_nav = (self.length > 1) or (not self.hide_nav_for_single)
        if show_nav:
            prev_btn = discord.ui.Button(emoji=DEC_EMOJI, style=discord.ButtonStyle.grey)
            next_btn = discord.ui.Button(emoji=INC_EMOJI, style=discord.ButtonStyle.grey)
            prev_btn.callback = self._on_prev
            next_btn.callback = self._on_next
            self.add_item(prev_btn)
            self.add_item(next_btn)
        del_btn = discord.ui.Button(emoji=DEL_EMOJI, style=discord.ButtonStyle.red)
        del_btn.callback = self._on_delete
        self.add_item(del_btn)

    def _first_url(self, content: Optional[str]) -> Optional[str]:
        if not content: return None
        for token in content.split():
            if token.startswith("http://") or token.startswith("https://"):
                return token
        return None

    async def _force_unfurl_if_video(self, msg: discord.Message, content: Optional[str]):
        """Force Discord to (re)embed a video link after sends/edits, without downloading."""
        url = self._first_url(content)
        if not url or not url.lower().endswith(VIDEO_EXTS):
            return
        try:
            # 1) toggle suppression to retrigger preview
            await msg.edit(suppress=True)
            await asyncio.sleep(0)
            await msg.edit(suppress=False)
        except discord.HTTPException:
            pass

        # 2) fallback "nudge": tiny, invisible content flip to retrigger renderer
        try:
            await msg.edit(content=(content + "\n\u200B"))  # zero-width space on its own line
            await asyncio.sleep(0)
            await msg.edit(content=content)
        except discord.HTTPException:
            pass

    # ---------- public API ----------
    async def send(self, ctx):
        if self.user is None and hasattr(ctx, "author"):
            self.user = ctx.author

        content, embeds, files = await self.getPage()
        self.message = await ctx.super.send(content=content, embeds=embeds, view=self)

        # Kick the unfurler after initial send (if video URL)
        await self._force_unfurl_if_video(self.message, content)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if not self.owner_only: return True
        if self.user is None:
            self.user = interaction.user
            return True
        if interaction.user.id != self.user.id:
            await interaction.response.send_message(
                "Only the original requester can use these controls.", ephemeral=True
            )
            return False
        return True

    async def on_timeout(self):
        if self.message:
            try:
                if self.delete_on_timeout:
                    await self.message.delete()
                else:
                    await self._apply_close(target=self.message, mode="detach")
            except discord.HTTPException:
                pass
        await super().on_timeout()

    # ---------- page rendering ----------
    async def getPage(self):
        page = self.pages[self.index]
        if isinstance(page, str):
            return page, [], []
        if isinstance(page, discord.Embed):
            return None, [page], []
        if isinstance(page, discord.File):
            return None, [], [page]
        if isinstance(page, tuple):  # <-- NEW: mixed page via tuple
            items = [None, [], []]
            for item in page:
                if isinstance(item, str):
                    items[0] = item
                elif isinstance(item, discord.Embed):
                    items[1].append(item)
                elif isinstance(item, discord.File):
                    items[2].append(item)
            return tuple(items)
        if isinstance(page, list):  # list = list of pages (as before)
            items = [None, [], []]
            for item in page:
                if isinstance(item, str):
                    items[0] = item
                elif isinstance(item, discord.Embed):
                    items[1].append(item)
                elif isinstance(item, discord.File):
                    items[2].append(item)
            return tuple(items)
        return None, [], []

    async def showPage(self, interaction: discord.Interaction):
        content, embeds, files = await self.getPage()
        await interaction.response.edit_message(
            content=content, embeds=embeds, attachments=files or [], view=self
        )
        # Nudge preview after each page turn (non-blocking)
        try:
            await self._force_unfurl_if_video(interaction.message, content)
        except Exception:
            pass

    # ---------- callbacks ----------
    async def _on_prev(self, interaction: discord.Interaction):
        self.index = (self.index - 1) % self.length
        await self.showPage(interaction)

    async def _on_next(self, interaction: discord.Interaction):
        self.index = (self.index + 1) % self.length
        await self.showPage(interaction)

    async def _on_delete(self, interaction: discord.Interaction):
        await interaction.response.defer()
        target = self.message or interaction.message
        try:
            await self._apply_close(target=target, mode=self.close_mode)
        except discord.HTTPException:
            await interaction.followup.send("Couldn’t update the message.", ephemeral=True)
        finally:
            self.stop()

    async def _apply_close(self, *, target: discord.Message, mode: CloseMode):
        if mode == "delete":
            await target.delete()
        elif mode == "detach":
            await target.edit(view=None)
        elif mode == "disable":
            for child in self.children:
                child.disabled = True
            await target.edit(view=self)
