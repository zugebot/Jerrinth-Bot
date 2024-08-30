# Jerrin Shirks

# native imports
import threading
import time

# custom imports
from files.support import *
from files.config import *


class DataManager:
    def __init__(self, filename, version=0):
        self.data_file = filename
        self.data_version = version
        self.data = read_json(self.data_file)
        if self.data == {}:
            self.data = {"users": {}, "servers": {}}

        self.lock = threading.Lock()
        self.is_saving = False
        self.shutdown_requested = False


    def saveData(self, data: dict = None) -> bool:
        with self.lock:
            self.is_saving = True
            if self.shutdown_requested:
                # Handle the case where shutdown is requested while saveData is about to start
                return False

            if data is None:
                data = self.data

            try:
                with open(self.data_file, 'w') as file:
                    json.dump(data, file)
                return True
            except Exception as e:
                print_red(f"Error saving data: {e}")
                return False
            finally:
                self.is_saving = False



    # ensure functions
    def ensureServerExists(self, ctx: CtxObject or str or int, name=None) -> bool:

        if isinstance(ctx, int):
            ctx = str(ctx)

        if self.getServer(ctx) is not None:
            return True

        if isinstance(ctx, CtxObject):
            self.data["servers"][ctx.server] = EMPTY_SERVER.copy()
            self.data["servers"][ctx.server]["name"] = ctx.super.guild.name
            self.saveData()
            return True

        elif isinstance(ctx, str):
            self.data["servers"][ctx] = EMPTY_SERVER.copy()
            self.data["servers"][ctx]["name"] = name
            self.saveData()
            return True

        return False

    def ensureChannelExists(self, ctx: CtxObject) -> bool:
        if self.getChannel(ctx) is not None:
            return False
        self.data["servers"][ctx.server]["channels"][ctx.channel] = EMPTY_CHANNEL.copy()
        self.saveData()
        return True

    def ensureUserExists(self, ctx: CtxObject) -> bool:
        if self.getUser(ctx) is not None:
            return False
        self.data["users"][ctx.user] = EMPTY_USER.copy()
        if ctx.userInt == ctx.super.message.author.id:
            self.getUser(ctx)["name"] = ctx.message.author.name
        self.saveData()
        return True

    # get functions
    def getServer(self, ctx: CtxObject or str or int) -> dict or None:
        if isinstance(ctx, int):
            ctx = str(ctx)

        if isinstance(ctx, CtxObject):
            return self.data["servers"].get(ctx.server, None)
        elif isinstance(ctx, str):
            return self.data["servers"].get(ctx, None)
        else:
            raise Exception(f"Wrong ctx type for server {type(ctx)}")

    def getChannel(self, ctx: int | CtxObject) -> dict or None:
        if isinstance(ctx, int):
            channel = str(ctx)
        elif isinstance(ctx, CtxObject):
            channel = ctx.channel
        else:
            raise Exception(f"Invalid ctx type '{type(ctx)}'")
        return self.data["servers"][ctx.server]["channels"].get(channel, None)

    def getUser(self, ctx: CtxObject) -> dict or None:
        if isinstance(ctx, int):
            user = str(ctx)
        elif isinstance(ctx, CtxObject):
            user = ctx.user
        else:
            raise Exception(f"Invalid ctx type '{type(ctx)}'")
        return self.data["users"].get(user, None)

    # bool functions
    def serverExists(self, ctx: CtxObject) -> bool:
        return ctx.server in self.data["servers"]

    def channelExists(self, ctx: CtxObject) -> bool:
        return ctx.channel in self.data["servers"][ctx.server]["channels"]

    def userExists(self, ctx: CtxObject) -> bool:
        return ctx.user in self.data["users"]

    # delete functions
    def deleteServer(self, ctx: CtxObject) -> bool:
        if self.getServer(ctx) is not None:
            del self.data["servers"][ctx.server]
            self.saveData()
            return True
        return False

    def deleteChannel(self, ctx: CtxObject) -> bool:
        if self.getChannel(ctx) is not None:
            del self.data["servers"][ctx.server]["channels"][ctx.channel]
            self.saveData()
            return True
        return False

    def deleteUser(self, ctx: CtxObject) -> bool:
        if self.getUser(ctx) is not None:
            del self.data["users"][ctx.user]
            self.saveData()
            return True
        return False

    # dict functions | getServerDict is unnecessary
    def getChannelDict(self, ctx: CtxObject) -> dict:
        return self.data["servers"][ctx.server]["channels"]

    def getUserDict(self, ctx: CtxObject) -> dict:
        return self.data["users"]
