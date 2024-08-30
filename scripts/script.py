# Jerrin Shirks
import pprint

from files.makeTable import makeTable
from files.support import *


def move_servers_to_section():
    data = read_json("../data/data.json")

    new_data = {
        "users": {},
        "servers": {}
    }
    for _server in data:
        new_data["servers"][_server] = data[_server]

    save_json("data/data_new.json", new_data)


def add_global_user_data():
    keys = ["findseed", "ai", "imgur", "@someone", "playrandom", "whisper", "play"]

    data_old = read_json("data/data_backup.json")
    del data_old["users"]
    data_old["users"] = {}

    for _ in (SERVERS := data_old["servers"]):
        if SERVERS[_].get("prefix", None) == ",":
            del SERVERS[_]["prefix"]
        if "presence" in SERVERS[_]:
            del SERVERS[_]["presence"]
        if "@someone" in SERVERS[_]:
            SERVERS[_]["someone"] = SERVERS[_]["@someone"]
            del SERVERS[_]["@someone"]

        for user in (OLD_USERS := SERVERS[_]["users"]):
            OLD_USER = OLD_USERS[user]

            # adds the user if they do not exist
            if user not in data_old["users"]:
                data_old["users"][user] = {
                    "name": OLD_USER["name"],
                    "use_last": 0,
                    "use_total": 0
                }
            NEW_USER = data_old["users"][user]

            # add all the attributes
            for old_key in keys:
                new_key = old_key
                if old_key == "ai":
                    new_key = "chat"
                if old_key == "@someone":
                    new_key = "someone"

                if old_key not in OLD_USER:
                    continue

                # add the key if it is not there
                if new_key not in NEW_USER:
                    NEW_USER[new_key] = {
                        "use_total": 0,
                        "use_last": 0
                    }

                # adds total uses
                NEW_USER[new_key]["use_total"] += OLD_USER[old_key]["total_uses"]
                NEW_USER["use_total"] += OLD_USER[old_key]["total_uses"]

                # updates command last use
                last_used = OLD_USER[old_key]["last_use"]
                if last_used is None:
                    continue

                if last_used > NEW_USER[new_key]["use_last"]:
                    NEW_USER[new_key]["use_last"] = last_used

                # updates user last use
                if last_used > NEW_USER["use_last"]:
                    NEW_USER["use_last"] = last_used

            if "findseed" in OLD_USER:
                if "eye_count" not in NEW_USER["findseed"]:
                    NEW_USER["findseed"]["eye_count"] = [0]

                for n in range(len(OLD_USER["findseed"]["eye_count"]) - 1):
                    if len(NEW_USER["findseed"]["eye_count"]) <= n + 1:
                        NEW_USER["findseed"]["eye_count"].append(0)
                    NEW_USER["findseed"]["eye_count"][n] += OLD_USER["findseed"]["eye_count"][n]

        del SERVERS[_]["users"]

        to_delete = []
        for channel in (CHANNELS := SERVERS[_]["channels"]):
            if "chatgpt-content" in CHANNELS[channel]:
                del CHANNELS[channel]["chatgpt-content"]
            if "forced_engine" in CHANNELS[channel]:
                del CHANNELS[channel]["forced_engine"]
            if CHANNELS[channel] == {}:
                to_delete.append(channel)

        for channel in to_delete:
            del CHANNELS[channel]

    save_json("../data/data_debug.json", data_old)
    pprint.pprint(data_old)


add_global_user_data()



def get_global_leaderboard(dict_key="chat", maximum_users=100):
    data = read_json("../data/data.json")

    items = [i for i in data["users"].items() if dict_key in i[1]]
    users = sorted(items,
                   key=lambda x: x[1][dict_key]["total_uses"],
                   reverse=True)
    table = []
    for n, (key, value) in enumerate(users):
        if n >= maximum_users or value[dict_key]["total_uses"] == 0:
            break
        table.append([value[dict_key]["total_uses"], f"<@{key}>"])
    leaderboard = makeTable(table, show_index=True, code=[0])
    return leaderboard



"""
move_servers_to_section()
board = get_global_leaderboard("ai")
print(board)
"""














