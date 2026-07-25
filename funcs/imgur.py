# Jerrin Shirks

# native imports
import aiohttp
import ssl

# custom imports
from files.support import *
from files.discord_objects import *


# None


class Imgur:
    def __init__(self, bot):
        self.bot = bot
        self.client_id = self.bot.settings["imgur_client_id"]

        self.valid_id = self.client_id is not None

        self.header = "https://api.imgur.com/"

        self.data = {
            "random": [],
            "gallery": {}
        }

        self.random_link = f"{self.header}/post/v1/posts?client_id={self.client_id}&filter[section]=eq:random"
        self.gallery_link = "{}3/gallery/{}/{}/{}/1?client_id={}&page={}&showViral={}&mature={}&album_previews=true"
        self.album_link = "https://api.imgur.com/3/gallery/album/{}?client_id=" + self.client_id
        self.image_link = "https://api.imgur.com/3/image/{}?client_id=" + self.client_id

    # for ,findimg
    async def loadRandomImages(self):
        if not self.valid_id:
            return
        if len(self.data["random"]) < 3:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.random_link) as response:
                    self.data["random"] = await response.json()

    # for ,findimg
    def getRandomImage(self, ctx) -> str or None:
        if not self.valid_id:
            return None

        while len(self.data["random"]) > 2:
            image = self.data["random"].pop(0)
            if image["is_ad"] or ((not ctx.nsfw) and image["is_mature"]):
                continue
            return image
        return None

    async def __getAlbumDetails(self, album_id: str) -> dict:
        link = self.album_link.format(album_id)
        async with aiohttp.ClientSession() as session:
            async with session.get(link) as response:
                return await response.json()

    async def __getImageDetails(self, image_id: str) -> dict:
        link = self.image_link.format(image_id)
        async with aiohttp.ClientSession() as session:
            async with session.get(link) as response:
                return await response.json()

    # •
    async def createMessage(self, data: dict):
        def trim(txt, n=100):
            if not txt: return None
            txt = txt.strip()
            return txt if len(txt) <= n else txt[:n] + "\n**...**"

        if not data["is_album"]:
            data = (await self.__getImageDetails(image_id=data["id"]))["data"]
            title = (data.get("title") or "").strip()
            desc = trim(data.get("description"))
            typ = data.get("type")

            # ---- MP4: content URL (for player) + a small embed for text ----
            if typ == "video/mp4":
                emb = newEmbed()
                if desc: emb.description = desc
                if title: emb.set_author(name=title, url=data["link"])
                # Some Imgur payloads also have mp4-specific URL fields; prefer them if present
                url = data.get("mp4") or data["link"]
                return [url, emb]

            # GIFs
            if typ == "image/gif":
                emb = newEmbed()
                if desc: emb.description = desc
                if title: emb.set_author(name=title, url=data["link"])
                emb.set_image(url=(data.get("gifv") or data["link"]).replace(".gifv", "gif"))
                return emb

            # Static images
            if typ in ["image/png", "image/jpg", "image/jpeg", "image/webp"]:
                emb = newEmbed()
                if desc: emb.description = desc
                if title: emb.set_author(name=title, url=data["link"])
                emb.set_image(url=data["link"])
                return emb

            # Fallback
            return f"{title + '\\n' if title else ''}{data['link']}"

        # -------- Album --------
        data = (await self.__getAlbumDetails(album_id=data["id"]))["data"]
        items = data["images"];
        length = len(items);
        pages = []
        album_title = (data.get("title") or "").strip()

        for idx, item in enumerate(items, start=1):
            typ = item.get("type");
            link = item.get("link")
            emb = newEmbed()

            if item.get("description"):
                d = trim(item["description"])
                if d: emb.description = d

            head = []
            if data.get("images_count", length) > 1: head.append(f"[{idx}/{length}]")
            if album_title: head.append(album_title)
            title = " ".join(head).strip()
            if title: emb.set_author(name=title, url=data.get("link"))

            if typ in ["image/png", "image/jpg", "image/jpeg", "image/webp"]:
                emb.set_image(url=link)
                pages.append(emb)
            elif typ == "image/gif":
                emb.set_image(url=(item.get("gifv") or link).replace(".gifv", "gif"));
                pages.append(emb)
            elif typ == "video/mp4":
                url = item.get("mp4") or link
                pages.append(url)
            else:
                pages.append(link)

        return pages[0] if len(pages) == 1 else pages

    """
    @staticmethod
    def gallery_args(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            kwargs = dict(kwargs)
            print(kwargs)
            if kwargs["section"] not in ["hot", "top"]:
                kwargs["section"] = "hot"
            if kwargs["sort"] not in ["viral", "top", "time", "rising"]:
                kwargs["sort"] = "viral"
            if kwargs["window"] not in ["day", "week", "month", "year", "all"]:
                kwargs["window"] = "day"
            kwargs["showViral"] = str(bool(kwargs["showViral"])).lower()
            kwargs["mature"] = str(bool(kwargs["mature"])).lower()
            if "page" in kwargs:
                if isinstance(kwargs["page"], int):
                    kwargs["page"] = str(kwargs["page"])
            return await func(*args, **kwargs)
        return wrapper
    """

    async def loadGallery(self,
                          section="hot",
                          sort="viral",
                          window="day",
                          showViral="true",
                          mature="true",
                          page=1):
        link = self.gallery_link.format(self.header,
                                        section,
                                        sort,
                                        window,
                                        self.client_id,
                                        page,
                                        showViral,
                                        mature)

        key = "{}-{}-{}-{}-{}".format(section,
                                      sort,
                                      window,
                                      showViral,
                                      mature)

        if len(self.data["gallery"].get(key, [])) < 2:
            async with aiohttp.ClientSession() as session:
                async with session.get(link) as response:
                    data = await response.json()
                    self.data["gallery"][key] = data["data"]

    def getGalleryImage(self,
                        ctx,
                        section="hot",
                        sort="viral",
                        window="day",
                        showViral="true",
                        mature="true"):

        key = "{}-{}-{}-{}-{}".format(section,
                                      sort,
                                      window,
                                      showViral,
                                      mature)

        # save_json("gallery", self.data["gallery"])
        # pprint.pprint(self.data["gallery"])
        # input("waiting")

        while len(self.data["gallery"][key]) > 2:
            # item = random.choice(self.data["gallery"][key].keys())
            image = self.data["gallery"][key].pop(0)
            # image = self.data["gallery"][key].pop(item, None)
            if image["is_ad"] or ((not ctx.nsfw) and mature == "true"):
                continue

            return image
        return None
