# Jerrin Shirks

# native imports

# custom imports
from support import *



class DataManager:
    def __init__(self, filename, version=0):
        self.data_file = filename
        self.data_version = version
        self.data = read_json(self.data_file)

    # save function
    def saveData(self, data: dict = None) -> bool:
        if data is None:
            data = self.data
        return save_json(self.data_file, data)


    # ensure functions
    def ensureServerExists(self, ctx: ctxObject or str or int, name=None) -> bool:
        if isinstance(ctx, int):
            ctx = str(ctx)

        if self.getServer(ctx) is not None:
            return True

        if isinstance(ctx, ctxObject):
            self.data[ctx.server] = EMPTY_SERVER.copy()
            self.data[ctx.server]["name"] = ctx.super.guild.name
            self.saveData()
            return True

        elif isinstance(ctx, str):
            self.data[ctx] = EMPTY_SERVER.copy()
            self.data[ctx]["name"] = name
            self.saveData()
            return True

        return False

    def ensureChannelExists(self, ctx: ctxObject) -> bool:
        if self.getChannel(ctx) is not None:
            return False
        self.data[ctx.server]["channels"][ctx.channel] = EMPTY_CHANNEL.copy()
        self.saveData()
        return True

    def ensureUserExists(self, ctx: ctxObject) -> bool:
        if self.getUser(ctx) is not None:
            return False
        self.data[ctx.server]["users"][ctx.user] = EMPTY_USER.copy()
        if ctx.userInt == ctx.super.message.author.id:
            self.getUser(ctx)["name"] = ctx.message.author.name
        self.saveData()
        return True


    # get functions
    def getServer(self, ctx: ctxObject or str or int) -> dict or None:
        if isinstance(ctx, int):
            ctx = str(ctx)

        if isinstance(ctx, ctxObject):
            return self.data.get(ctx.server, None)
        elif isinstance(ctx, str):
            return self.data.get(ctx, None)

    def getChannel(self, ctx: ctxObject) -> dict or None:
        return self.data[ctx.server]["channels"].get(ctx.channel, None)

    def getUser(self, ctx: ctxObject) -> dict or None:
        return self.data[ctx.server]["users"].get(ctx.user, None)


    # bool functions
    def serverExists(self, ctx: ctxObject) -> bool:
        return ctx.server in self.data

    def channelExists(self, ctx: ctxObject) -> bool:
        return ctx.channel in self.data[ctx.server]["channels"]

    def userExists(self, ctx: ctxObject) -> bool:
        return ctx.user in self.data[ctx.server]["users"]


    # delete functions
    def deleteServer(self, ctx: ctxObject) -> bool:
        if self.getServer(ctx) is not None:
            del self.data[ctx.server]
            self.saveData()
            return True
        return False

    def deleteChannel(self, ctx: ctxObject) -> bool:
        if self.getChannel(ctx) is not None:
            del self.data[ctx.server]["channels"][ctx.channel]
            self.saveData()
            return True
        return False

    def deleteUser(self, ctx: ctxObject) -> bool:
        if self.getUser(ctx) is not None:
            del self.data[ctx.server]["users"][ctx.user]
            self.saveData()
            return True
        return False


    # dict functions | getServerDict is unnecessary
    def getChannelDict(self, ctx: ctxObject) -> dict:
        return self.data[ctx.server]["channels"]

    def getUserDict(self, ctx: ctxObject) -> dict:
        return self.data[ctx.server]["users"]


    # random functions
    def getUserEngine(self, ctx: ctxObject, num: int = 0) -> int:
        try:
            return self.getUser(ctx)["ai"].get("engine", num)
        except:
            return num
