# Jerrin Shirks
import asyncio
import atexit
import signal
import sys
import threading

# native imports

# custom imports
from files.support import *



class DataManager:
    def __init__(self, filename, version=0):
        self.data_file = filename
        self.data_version = version
        self.data = read_json(self.data_file)

        self.lock = threading.Lock()
        self.is_saving = False
        self.shutdown_requested = False
        signal.signal(signal.SIGINT, self.signal_handler)



    # save function
    """
    def saveData(self, data: dict = None) -> bool:
        if data is None:
            data = self.data
        return save_json(self.data_file, data)
    """

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
                print(f"Error saving data: {e}")
                return False
            finally:
                self.is_saving = False
                if self.shutdown_requested:
                    self.shutdown_now()

    def signal_handler(self, signum, frame):
        print("SIGINT received. Preparing to shutdown...")
        self.shutdown_requested = True
        if not self.is_saving:
            self.shutdown_now()

    def shutdown_now(self):
        print("Shutting down...")
        sys.exit(0)

    # ensure functions
    def ensureServerExists(self, ctx: ctxObject or str or int, name=None) -> bool:
        if isinstance(ctx, int):
            ctx = str(ctx)

        if self.getServer(ctx) is not None:
            return True

        if isinstance(ctx, ctxObject):
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

    def ensureChannelExists(self, ctx: ctxObject) -> bool:
        if self.getChannel(ctx) is not None:
            return False
        self.data["servers"][ctx.server]["channels"][ctx.channel] = EMPTY_CHANNEL.copy()
        self.saveData()
        return True

    def ensureUserExists(self, ctx: ctxObject) -> bool:
        if self.getUser(ctx) is not None:
            return False
        self.data["servers"][ctx.server]["users"][ctx.user] = EMPTY_USER.copy()
        if ctx.userInt == ctx.super.message.author.id:
            self.getUser(ctx)["name"] = ctx.message.author.name
        self.saveData()
        return True


    # get functions
    def getServer(self, ctx: ctxObject or str or int) -> dict or None:
        if isinstance(ctx, int):
            ctx = str(ctx)

        if isinstance(ctx, ctxObject):
            return self.data["servers"].get(ctx.server, None)
        elif isinstance(ctx, str):
            return self.data["servers"].get(ctx, None)
        else:
            raise Exception(f"Wrong ctx type for server {type(ctx)}")

    def getChannel(self, ctx: int | ctxObject) -> dict or None:
        if isinstance(ctx, int):
            channel = str(ctx)
        elif isinstance(ctx, ctxObject):
            channel = ctx.channel
        else:
            raise Exception(f"Invalid ctx type '{type(ctx)}'")
        return self.data["servers"][ctx.server]["channels"].get(channel, None)

    def getUser(self, ctx: ctxObject) -> dict or None:
        if isinstance(ctx, int):
            user = str(ctx)
        elif isinstance(ctx, ctxObject):
            user = ctx.user
        else:
            raise Exception(f"Invalid ctx type '{type(ctx)}'")
        return self.data["servers"][ctx.server]["users"].get(user, None)


    # bool functions
    def serverExists(self, ctx: ctxObject) -> bool:
        return ctx.server in self.data["servers"]

    def channelExists(self, ctx: ctxObject) -> bool:
        return ctx.channel in self.data["servers"][ctx.server]["channels"]

    def userExists(self, ctx: ctxObject) -> bool:
        return ctx.user in self.data["servers"][ctx.server]["users"]


    # delete functions
    def deleteServer(self, ctx: ctxObject) -> bool:
        if self.getServer(ctx) is not None:
            del self.data["servers"][ctx.server]
            self.saveData()
            return True
        return False

    def deleteChannel(self, ctx: ctxObject) -> bool:
        if self.getChannel(ctx) is not None:
            del self.data["servers"][ctx.server]["channels"][ctx.channel]
            self.saveData()
            return True
        return False

    def deleteUser(self, ctx: ctxObject) -> bool:
        if self.getUser(ctx) is not None:
            del self.data["servers"][ctx.server]["users"][ctx.user]
            self.saveData()
            return True
        return False


    # dict functions | getServerDict is unnecessary
    def getChannelDict(self, ctx: ctxObject) -> dict:
        return self.data["servers"][ctx.server]["channels"]

    def getUserDict(self, ctx: ctxObject) -> dict:
        return self.data["servers"][ctx.server]["users"]


    # random functions
    def getUserEngine(self, ctx: ctxObject, num: int = 0) -> int:
        try:
            return self.getUser(ctx)["ai"].get("engine", num)
        except:
            return num
