# Jerrin Shirks

# native imports
import aiohttp
import random
import functools
import pprint
import asyncio
import discord

# custom imports
from support import *
# None




class Imgur:
    def __init__(self, bot):
        self.bot = bot
        self.client_id = self.bot.settings["imgur_client_id"]
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
        if len(self.data["random"]) < 3:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.random_link) as response:
                    self.data["random"] = await response.json()

    # for ,findimg
    def getRandomImage(self, ctx) -> str | None:
        while len(self.data["random"]) > 2:
            image = self.data["random"].pop(0)
            if image["is_ad"] or ((not ctx.nsfw) and image["is_mature"]):
                continue
            return image
        return None


    async def getAlbumDetails(self, album_id: str) -> dict:
        link = self.album_link.format(album_id)
        async with aiohttp.ClientSession() as session:
            async with session.get(link) as response:
                return await response.json()



    async def getImageDetails(self, image_id: str) -> dict:
        link = self.image_link.format(image_id)
        async with aiohttp.ClientSession() as session:
            async with session.get(link) as response:
                return await response.json()



    # •
    async def createMessage(self, data: dict):
        if not data["is_album"]:
            data = await self.getImageDetails(image_id=data["id"])
            data = data["data"]

            # pprint.pprint(data)

            message = ""

            if data["title"]:
                message += f"{data['title']}\n"
            message += f"{data['link']}"

            return message

        else:

            data = await self.getAlbumDetails(album_id=data["id"])
            data = data["data"]

            # print("#"*50)
            # pprint.pprint(data)




            items = data["images"]
            length = len(items)
            pages = []
            for n, item in enumerate(items):
                message = ""
                title = ""
                embed = newEmbed()

                if item["description"]:
                    embed.description = item["description"]
                    # message += item["description"]

                if data["images_count"] > 1:
                    title += f"[{n+1}/{length}] "

                if data["title"]:
                    title += data['title']
                    embed.set_author(name=title, url=data['link'])

                if item["type"] in ["image/png", "image/jpg", "image/jpeg"]:
                    embed.set_image(url=item['link'])
                    pages.append(embed)

                if item["type"] == "image/gif":
                    embed.set_image(url=item['gifv'])
                    pages.append(embed)

                if item["type"] == "video/mp4":
                    text = ""
                    if data["images_count"] != 1:
                        text = f"**[{n+1}/{length}]** "
                    if data["title"]:
                        text += f"**{data['title']}**\n"
                    text += item['link']
                    pages.append(text) # [link, embed])

            if data["images_count"] == 1:
                return pages[0]
            return pages











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




