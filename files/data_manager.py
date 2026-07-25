"""SQLite-backed persistence for JerrinthBot.

The bot historically exposed one mutable ``self.data`` dictionary to every cog.
This module keeps that public API compatible while making SQLite the source of
truth. Nested dictionaries and lists are tracked, so ``saveData()`` only writes
users and guilds that actually changed instead of rewriting the whole state.

Writes requested from Discord commands are debounced and executed in a worker
thread. This keeps the event loop responsive while preserving the existing cog
code during the database conversion.
"""

from __future__ import annotations

import asyncio
import copy
import json
import sqlite3
import threading
from collections.abc import Callable, Iterable, Mapping
from pathlib import Path
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from files.discord_objects import CtxObject


EMPTY_SERVER = {"name": None, "channels": {}}
EMPTY_CHANNEL: dict[str, Any] = {}
EMPTY_USER = {"name": None, "use_total": 0, "use_last": None}


def print_red(text: Any) -> None:
    print(f"\033[91m{text}\033[0m")


def _is_ctx(value: Any) -> bool:
    return hasattr(value, "server") and hasattr(value, "user")


_MISSING = object()


def _plain(value: Any) -> Any:
    """Return ordinary JSON-compatible containers from tracked containers."""
    if isinstance(value, dict):
        return {str(key): _plain(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_plain(item) for item in value]
    return copy.deepcopy(value)


def _json_loads_object(value: str | None) -> dict[str, Any]:
    if not value:
        return {}
    decoded = json.loads(value)
    return decoded if isinstance(decoded, dict) else {"__raw_value__": decoded}


def _compact_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )


def _as_int(value: Any, default: int = 0) -> int:
    if value is None:
        return default
    if isinstance(value, bool):
        return int(value)
    return int(value)


def _as_float_or_none(value: Any) -> float | None:
    if value is None:
        return None
    return float(value)


class TrackedDict(dict):
    """A dict that recursively reports mutations through one callback."""

    def __init__(self, initial: Mapping[Any, Any] | None, on_change: Callable[[], None]):
        self._on_change = on_change
        dict.__init__(self)
        if initial:
            for key, value in initial.items():
                dict.__setitem__(self, key, _track(value, on_change))

    def __setitem__(self, key: Any, value: Any) -> None:
        dict.__setitem__(self, key, _track(value, self._on_change))
        self._on_change()

    def __delitem__(self, key: Any) -> None:
        dict.__delitem__(self, key)
        self._on_change()

    def clear(self) -> None:
        if self:
            dict.clear(self)
            self._on_change()

    def pop(self, key: Any, default: Any = _MISSING) -> Any:
        if key in self:
            value = dict.pop(self, key)
            self._on_change()
            return value
        if default is _MISSING:
            raise KeyError(key)
        return default

    def popitem(self) -> tuple[Any, Any]:
        value = dict.popitem(self)
        self._on_change()
        return value

    def setdefault(self, key: Any, default: Any = None) -> Any:
        if key in self:
            return dict.__getitem__(self, key)
        wrapped = _track(default, self._on_change)
        dict.__setitem__(self, key, wrapped)
        self._on_change()
        return wrapped

    def update(self, *args: Any, **kwargs: Any) -> None:
        incoming = dict(*args, **kwargs)
        if not incoming:
            return
        for key, value in incoming.items():
            dict.__setitem__(self, key, _track(value, self._on_change))
        self._on_change()

    def __ior__(self, other: Mapping[Any, Any]):
        self.update(other)
        return self


class TrackedList(list):
    """A list that recursively reports mutations through one callback."""

    def __init__(self, initial: Iterable[Any] | None, on_change: Callable[[], None]):
        self._on_change = on_change
        list.__init__(self)
        if initial:
            list.extend(self, (_track(value, on_change) for value in initial))

    def __setitem__(self, index: Any, value: Any) -> None:
        if isinstance(index, slice):
            value = [_track(item, self._on_change) for item in value]
        else:
            value = _track(value, self._on_change)
        list.__setitem__(self, index, value)
        self._on_change()

    def __delitem__(self, index: Any) -> None:
        list.__delitem__(self, index)
        self._on_change()

    def append(self, value: Any) -> None:
        list.append(self, _track(value, self._on_change))
        self._on_change()

    def extend(self, values: Iterable[Any]) -> None:
        values = [_track(value, self._on_change) for value in values]
        if values:
            list.extend(self, values)
            self._on_change()

    def insert(self, index: int, value: Any) -> None:
        list.insert(self, index, _track(value, self._on_change))
        self._on_change()

    def pop(self, index: int = -1) -> Any:
        value = list.pop(self, index)
        self._on_change()
        return value

    def remove(self, value: Any) -> None:
        list.remove(self, value)
        self._on_change()

    def clear(self) -> None:
        if self:
            list.clear(self)
            self._on_change()

    def reverse(self) -> None:
        list.reverse(self)
        self._on_change()

    def sort(self, *args: Any, **kwargs: Any) -> None:
        list.sort(self, *args, **kwargs)
        self._on_change()

    def __iadd__(self, values: Iterable[Any]):
        self.extend(values)
        return self

    def __imul__(self, count: int):
        list.__imul__(self, count)
        self._on_change()
        return self


def _track(value: Any, on_change: Callable[[], None]) -> Any:
    if isinstance(value, TrackedDict):
        value = _plain(value)
    elif isinstance(value, TrackedList):
        value = _plain(value)

    if isinstance(value, dict):
        return TrackedDict(value, on_change)
    if isinstance(value, list):
        return TrackedList(value, on_change)
    return value


class EntityMap(dict):
    """Top-level mapping whose nested values dirty one entity ID."""

    def __init__(
        self,
        initial: Mapping[str, Any],
        mark_dirty: Callable[[str], None],
    ) -> None:
        self._mark_dirty = mark_dirty
        dict.__init__(self)
        for raw_entity_id, value in initial.items():
            entity_id = str(raw_entity_id)
            dict.__setitem__(
                self,
                entity_id,
                _track(value, lambda entity_id=entity_id: mark_dirty(entity_id)),
            )

    def __setitem__(self, raw_entity_id: Any, value: Any) -> None:
        entity_id = str(raw_entity_id)
        dict.__setitem__(
            self,
            entity_id,
            _track(value, lambda entity_id=entity_id: self._mark_dirty(entity_id)),
        )
        self._mark_dirty(entity_id)

    def __delitem__(self, raw_entity_id: Any) -> None:
        entity_id = str(raw_entity_id)
        dict.__delitem__(self, entity_id)
        self._mark_dirty(entity_id)

    def pop(self, raw_entity_id: Any, default: Any = _MISSING) -> Any:
        entity_id = str(raw_entity_id)
        if entity_id in self:
            value = dict.pop(self, entity_id)
            self._mark_dirty(entity_id)
            return value
        if default is _MISSING:
            raise KeyError(entity_id)
        return default

    def popitem(self) -> tuple[str, Any]:
        entity_id, value = dict.popitem(self)
        self._mark_dirty(entity_id)
        return entity_id, value

    def clear(self) -> None:
        entity_ids = list(self.keys())
        dict.clear(self)
        for entity_id in entity_ids:
            self._mark_dirty(entity_id)

    def setdefault(self, raw_entity_id: Any, default: Any = None) -> Any:
        entity_id = str(raw_entity_id)
        if entity_id in self:
            return dict.__getitem__(self, entity_id)
        self[entity_id] = default
        return dict.__getitem__(self, entity_id)

    def update(self, *args: Any, **kwargs: Any) -> None:
        for entity_id, value in dict(*args, **kwargs).items():
            self[entity_id] = value


class DataManager:
    """Compatibility facade over the normalized SQLite schema."""

    SAVE_DEBOUNCE_SECONDS = 0.05

    def __init__(self, database_path: str | Path, version: int = 0):
        self.database_path = Path(database_path).resolve()
        self.data_version = version
        self._database_lock = threading.RLock()
        self._dirty_lock = threading.Lock()
        self._dirty_users: set[str] = set()
        self._dirty_servers: set[str] = set()
        self._save_task: asyncio.Task | None = None
        self._database_closed = False
        self._last_save_error: Exception | None = None

        if not self.database_path.exists():
            raise FileNotFoundError(
                f"Database not found: {self.database_path}\n"
                "Run: py scripts\\migrate_json_to_sqlite.py"
            )

        self.connection = sqlite3.connect(
            self.database_path,
            timeout=5.0,
            check_same_thread=False,
        )
        self.connection.row_factory = sqlite3.Row
        self._configure_connection()
        self._verify_schema()

        loaded = self._load_state()
        self.data = {
            "users": EntityMap(loaded["users"], self._mark_user_dirty),
            "servers": EntityMap(loaded["servers"], self._mark_server_dirty),
        }

    # ------------------------------------------------------------------
    # Connection and lifecycle
    # ------------------------------------------------------------------

    def _configure_connection(self) -> None:
        with self._database_lock:
            self.connection.execute("PRAGMA foreign_keys = ON")
            self.connection.execute("PRAGMA journal_mode = WAL")
            self.connection.execute("PRAGMA synchronous = NORMAL")
            self.connection.execute("PRAGMA busy_timeout = 5000")

    def _verify_schema(self) -> None:
        required = {
            "users",
            "user_feature_usage",
            "user_items",
            "findseed_eye_counts",
            "findblock_stats",
            "guilds",
            "guild_channels",
            "banned_users",
            "badwords",
            "mudae_key_events",
            "mudae_soulmates",
            "mudae_waifus",
        }
        with self._database_lock:
            found = {
                row[0]
                for row in self.connection.execute(
                    "SELECT name FROM sqlite_master WHERE type = 'table'"
                )
            }
        missing = sorted(required - found)
        if missing:
            raise RuntimeError(
                f"Database schema is incomplete in {self.database_path}: "
                + ", ".join(missing)
            )

    async def flush_pending(self) -> None:
        """Wait until all dirty cached entities are committed."""
        while True:
            task = self._save_task
            if task is not None:
                await asyncio.shield(task)
                continue
            if not self._has_dirty_entities():
                return
            if self._last_save_error is not None:
                raise RuntimeError("A database save failed") from self._last_save_error
            self._schedule_save()

    async def close_database(self) -> None:
        if self._database_closed:
            return
        await self.flush_pending()
        self._database_closed = True
        await asyncio.to_thread(self._close_connection)

    def _close_connection(self) -> None:
        with self._database_lock:
            try:
                self.connection.execute("PRAGMA wal_checkpoint(TRUNCATE)")
            finally:
                self.connection.close()

    # ------------------------------------------------------------------
    # Dirty tracking and nonblocking saves
    # ------------------------------------------------------------------

    def _mark_user_dirty(self, user_id: str) -> None:
        with self._dirty_lock:
            self._dirty_users.add(str(user_id))
        self._schedule_save()

    def _mark_server_dirty(self, server_id: str) -> None:
        with self._dirty_lock:
            self._dirty_servers.add(str(server_id))
        self._schedule_save()

    def _has_dirty_entities(self) -> bool:
        with self._dirty_lock:
            return bool(self._dirty_users or self._dirty_servers)

    def _schedule_save(self) -> bool:
        if self._database_closed:
            return False
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            return False

        if self._save_task is None or self._save_task.done():
            self._save_task = loop.create_task(self._save_worker())
        return True

    async def _save_worker(self) -> None:
        failed = False
        try:
            await asyncio.sleep(self.SAVE_DEBOUNCE_SECONDS)
            while self._has_dirty_entities():
                snapshot = self._take_dirty_snapshot()
                if not snapshot[0] and not snapshot[1]:
                    break
                try:
                    await asyncio.to_thread(self._write_snapshot, *snapshot)
                    self._last_save_error = None
                except Exception as error:
                    self._restore_dirty_snapshot(*snapshot)
                    self._last_save_error = error
                    failed = True
                    print_red(f"Error saving database state: {error}")
                    return
        finally:
            self._save_task = None
            if not failed and self._has_dirty_entities() and not self._database_closed:
                self._schedule_save()

    def _take_dirty_snapshot(
        self,
    ) -> tuple[dict[str, dict[str, Any] | None], dict[str, dict[str, Any] | None]]:
        with self._dirty_lock:
            dirty_users = self._dirty_users
            dirty_servers = self._dirty_servers
            self._dirty_users = set()
            self._dirty_servers = set()

        users = {
            user_id: _plain(self.data["users"][user_id])
            if user_id in self.data["users"]
            else None
            for user_id in dirty_users
        }
        servers = {
            server_id: _plain(self.data["servers"][server_id])
            if server_id in self.data["servers"]
            else None
            for server_id in dirty_servers
        }
        return users, servers

    def _restore_dirty_snapshot(
        self,
        users: Mapping[str, Any],
        servers: Mapping[str, Any],
    ) -> None:
        with self._dirty_lock:
            self._dirty_users.update(users.keys())
            self._dirty_servers.update(servers.keys())

    def saveData(self, data: dict | None = None) -> bool:
        """Queue changed entities for SQLite persistence.

        ``data`` is retained only for API compatibility. Passing a replacement
        object is unsupported because the tracked ``self.data`` cache must stay
        authoritative.
        """
        if data is not None and data is not self.data:
            raise ValueError("saveData(data=...) is no longer supported; mutate self.data instead")
        if self._schedule_save():
            return True
        return self.flush_now()

    def flush_now(self) -> bool:
        """Synchronously flush dirty entities, primarily for tests and startup."""
        while self._has_dirty_entities():
            snapshot = self._take_dirty_snapshot()
            try:
                self._write_snapshot(*snapshot)
                self._last_save_error = None
            except Exception as error:
                self._restore_dirty_snapshot(*snapshot)
                self._last_save_error = error
                print_red(f"Error saving database state: {error}")
                return False
        return True

    def _write_snapshot(
        self,
        users: Mapping[str, dict[str, Any] | None],
        servers: Mapping[str, dict[str, Any] | None],
    ) -> None:
        with self._database_lock:
            self.connection.execute("BEGIN IMMEDIATE")
            try:
                for user_id, user in users.items():
                    self._write_user(user_id, user)
                for server_id, server in servers.items():
                    self._write_server(server_id, server)
                self.connection.commit()
            except Exception:
                self.connection.rollback()
                raise

    # ------------------------------------------------------------------
    # Normalized user persistence
    # ------------------------------------------------------------------

    def _write_user(self, user_id: str, user: dict[str, Any] | None) -> None:
        self.connection.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
        if user is None:
            return

        known_scalar_keys = {
            "name",
            "use_total",
            "use_last",
            "debug",
            "show_findseed_eyes",
            "loot_bonus",
            "items",
        }
        extra = {
            key: value
            for key, value in user.items()
            if key not in known_scalar_keys and not isinstance(value, dict)
        }

        self.connection.execute(
            """
            INSERT INTO users(
                user_id, name, use_total, use_last, debug,
                show_findseed_eyes, loot_bonus, extra_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                user.get("name"),
                _as_int(user.get("use_total"), 0),
                _as_float_or_none(user.get("use_last")),
                int(bool(user.get("debug", False))),
                int(bool(user.get("show_findseed_eyes", False))),
                _as_int(user.get("loot_bonus"), 0),
                _compact_json(extra),
            ),
        )

        items = user.get("items")
        if isinstance(items, dict):
            self.connection.executemany(
                "INSERT INTO user_items(user_id, item_key, quantity) VALUES (?, ?, ?)",
                [
                    (user_id, str(item_key), _as_int(quantity, 0))
                    for item_key, quantity in items.items()
                ],
            )

        for feature, raw_feature in user.items():
            if feature in known_scalar_keys or not isinstance(raw_feature, dict):
                continue

            feature_data = _plain(raw_feature)
            use_total = _as_int(feature_data.pop("use_total", 0), 0)
            use_last = _as_float_or_none(feature_data.pop("use_last", None))

            if feature == "findseed" and "eye_count" in feature_data:
                eye_counts = feature_data.pop("eye_count")
                if isinstance(eye_counts, list):
                    self.connection.executemany(
                        """
                        INSERT INTO findseed_eye_counts(user_id, eye_count, occurrences)
                        VALUES (?, ?, ?)
                        """,
                        [
                            (user_id, eye_count, max(0, _as_int(occurrences, 0)))
                            for eye_count, occurrences in enumerate(eye_counts)
                        ],
                    )
                else:
                    feature_data["eye_count"] = eye_counts

            if feature == "findblock" and "end_portal_count" in feature_data:
                count = max(0, _as_int(feature_data.pop("end_portal_count"), 0))
                self.connection.execute(
                    "INSERT INTO findblock_stats(user_id, end_portal_count) VALUES (?, ?)",
                    (user_id, count),
                )

            self.connection.execute(
                """
                INSERT INTO user_feature_usage(
                    user_id, feature, use_total, use_last, extra_json
                ) VALUES (?, ?, ?, ?, ?)
                """,
                (
                    user_id,
                    str(feature),
                    use_total,
                    use_last,
                    _compact_json(feature_data),
                ),
            )

    # ------------------------------------------------------------------
    # Normalized guild persistence
    # ------------------------------------------------------------------

    def _write_server(self, server_id: str, server: dict[str, Any] | None) -> None:
        self.connection.execute("DELETE FROM guilds WHERE guild_id = ?", (server_id,))
        if server is None:
            return

        known = {
            "name",
            "channels",
            "prefix",
            "censorship",
            "channel_redirect",
            "someone",
            "show_time_left",
            "say_real",
            "say_true",
            "vc_volume",
            "usable_everywhere",
            "not_in_server",
        }
        extra = {key: value for key, value in server.items() if key not in known}

        self.connection.execute(
            """
            INSERT INTO guilds(
                guild_id, name, prefix, censorship, channel_redirect,
                someone_enabled, show_time_left, say_real, say_true,
                vc_volume, usable_everywhere, not_in_server, extra_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                server_id,
                server.get("name"),
                str(server.get("prefix", ",")),
                int(bool(server.get("censorship", True))),
                int(bool(server.get("channel_redirect", True))),
                int(bool(server.get("someone", False))),
                int(bool(server.get("show_time_left", True))),
                int(bool(server.get("say_real", True))),
                int(bool(server.get("say_true", True))),
                _as_int(server.get("vc_volume"), 10),
                int(bool(server.get("usable_everywhere", False))),
                int(bool(server.get("not_in_server", False))),
                _compact_json(extra),
            ),
        )

        channels = server.get("channels", {})
        if not isinstance(channels, dict):
            return

        for raw_channel_id, raw_channel in channels.items():
            channel_id = str(raw_channel_id)
            if isinstance(raw_channel, dict):
                channel_data = _plain(raw_channel)
                forced_engine = channel_data.pop("forced_engine", None)
            else:
                forced_engine = None
                channel_data = {"__raw_value__": raw_channel}

            self.connection.execute(
                """
                INSERT INTO guild_channels(guild_id, channel_id, forced_engine, extra_json)
                VALUES (?, ?, ?, ?)
                """,
                (
                    server_id,
                    channel_id,
                    None if forced_engine is None else _as_int(forced_engine),
                    _compact_json(channel_data),
                ),
            )

    # ------------------------------------------------------------------
    # Database loading into the compatibility cache
    # ------------------------------------------------------------------

    def _load_state(self) -> dict[str, dict[str, Any]]:
        users: dict[str, dict[str, Any]] = {}
        servers: dict[str, dict[str, Any]] = {}

        with self._database_lock:
            user_rows = self.connection.execute("SELECT * FROM users").fetchall()
            feature_rows = self.connection.execute(
                "SELECT * FROM user_feature_usage ORDER BY user_id, feature"
            ).fetchall()
            item_rows = self.connection.execute(
                "SELECT * FROM user_items ORDER BY user_id, item_key"
            ).fetchall()
            eye_rows = self.connection.execute(
                "SELECT * FROM findseed_eye_counts ORDER BY user_id, eye_count"
            ).fetchall()
            findblock_rows = self.connection.execute(
                "SELECT * FROM findblock_stats"
            ).fetchall()
            guild_rows = self.connection.execute("SELECT * FROM guilds").fetchall()
            channel_rows = self.connection.execute(
                "SELECT * FROM guild_channels ORDER BY guild_id, channel_id"
            ).fetchall()

        for row in user_rows:
            user = _json_loads_object(row["extra_json"])
            user["name"] = row["name"]
            user["use_total"] = int(row["use_total"])
            user["use_last"] = row["use_last"]
            if row["debug"]:
                user["debug"] = True
            if row["show_findseed_eyes"]:
                user["show_findseed_eyes"] = True
            if row["loot_bonus"]:
                user["loot_bonus"] = int(row["loot_bonus"])
            users[str(row["user_id"])] = user

        for row in feature_rows:
            user = users.setdefault(
                str(row["user_id"]),
                {"name": None, "use_total": 0, "use_last": None},
            )
            feature = _json_loads_object(row["extra_json"])
            feature["use_total"] = int(row["use_total"])
            feature["use_last"] = row["use_last"]
            user[str(row["feature"])] = feature

        for row in item_rows:
            user = users[str(row["user_id"])]
            user.setdefault("items", {})[str(row["item_key"])] = int(row["quantity"])
            user.setdefault("loot_bonus", 0)

        eye_counts_by_user: dict[str, dict[int, int]] = {}
        for row in eye_rows:
            eye_counts_by_user.setdefault(str(row["user_id"]), {})[
                int(row["eye_count"])
            ] = int(row["occurrences"])
        for user_id, counts in eye_counts_by_user.items():
            max_index = max(12, max(counts, default=12))
            values = [0] * (max_index + 1)
            for eye_count, occurrences in counts.items():
                values[eye_count] = occurrences
            users[user_id].setdefault(
                "findseed", {"use_total": 0, "use_last": None}
            )["eye_count"] = values

        for row in findblock_rows:
            users[str(row["user_id"])].setdefault(
                "findblock", {"use_total": 0, "use_last": None}
            )["end_portal_count"] = int(row["end_portal_count"])

        for row in guild_rows:
            server = _json_loads_object(row["extra_json"])
            server["name"] = row["name"]
            server["channels"] = {}
            if row["prefix"] != ",":
                server["prefix"] = row["prefix"]
            if not row["censorship"]:
                server["censorship"] = False
            if not row["channel_redirect"]:
                server["channel_redirect"] = False
            if row["someone_enabled"]:
                server["someone"] = True
            if not row["show_time_left"]:
                server["show_time_left"] = False
            if not row["say_real"]:
                server["say_real"] = False
            if not row["say_true"]:
                server["say_true"] = False
            if int(row["vc_volume"]) != 10:
                server["vc_volume"] = int(row["vc_volume"])
            if row["usable_everywhere"]:
                server["usable_everywhere"] = True
            if row["not_in_server"]:
                server["not_in_server"] = True
            servers[str(row["guild_id"])] = server

        for row in channel_rows:
            server = servers.setdefault(
                str(row["guild_id"]),
                {"name": None, "channels": {}},
            )
            channel = _json_loads_object(row["extra_json"])
            if row["forced_engine"] is not None:
                channel["forced_engine"] = int(row["forced_engine"])
            if set(channel) == {"__raw_value__"}:
                channel = channel["__raw_value__"]
            server["channels"][str(row["channel_id"])] = channel

        return {"users": users, "servers": servers}

    # ------------------------------------------------------------------
    # Existing public compatibility API
    # ------------------------------------------------------------------

    def ensureServerExists(self, ctx: "CtxObject" | str | int, name: str | None = None) -> bool:
        server_id = str(ctx.server if _is_ctx(ctx) else ctx)
        if server_id in self.data["servers"]:
            return True

        server = copy.deepcopy(EMPTY_SERVER)
        if _is_ctx(ctx):
            server["name"] = ctx.super.guild.name
        else:
            server["name"] = name
        self.data["servers"][server_id] = server
        return True

    def ensureChannelExists(self, ctx: "CtxObject") -> bool:
        self.ensureServerExists(ctx)
        channels = self.data["servers"][ctx.server].setdefault("channels", {})
        if ctx.channel in channels:
            return False
        channels[ctx.channel] = copy.deepcopy(EMPTY_CHANNEL)
        return True

    def ensureUserExists(self, ctx: "CtxObject") -> bool:
        if ctx.user in self.data["users"]:
            return False
        user = copy.deepcopy(EMPTY_USER)
        if ctx.userInt == ctx.super.message.author.id:
            user["name"] = ctx.message.author.name
        self.data["users"][ctx.user] = user
        return True

    def getServer(self, ctx: "CtxObject" | str | int) -> dict[str, Any] | None:
        server_id = str(ctx.server if _is_ctx(ctx) else ctx)
        return self.data["servers"].get(server_id)

    def getChannel(self, ctx: "CtxObject") -> dict[str, Any] | None:
        if not _is_ctx(ctx):
            raise TypeError(f"Invalid ctx type '{type(ctx)}'")
        server = self.getServer(ctx)
        if server is None:
            return None
        channels = server.get("channels", {})
        return channels.get(ctx.channel)

    def getUser(self, ctx: "CtxObject" | int | str) -> dict[str, Any] | None:
        user_id = str(ctx.user if _is_ctx(ctx) else ctx)
        return self.data["users"].get(user_id)

    def serverExists(self, ctx: "CtxObject") -> bool:
        return ctx.server in self.data["servers"]

    def channelExists(self, ctx: "CtxObject") -> bool:
        server = self.getServer(ctx)
        return bool(server and ctx.channel in server.get("channels", {}))

    def userExists(self, ctx: "CtxObject") -> bool:
        return ctx.user in self.data["users"]

    def deleteServer(self, ctx: "CtxObject") -> bool:
        if self.getServer(ctx) is None:
            return False
        del self.data["servers"][ctx.server]
        return True

    def deleteChannel(self, ctx: "CtxObject") -> bool:
        server = self.getServer(ctx)
        if server is None or ctx.channel not in server.get("channels", {}):
            return False
        del server["channels"][ctx.channel]
        return True

    def deleteUser(self, ctx: "CtxObject") -> bool:
        if self.getUser(ctx) is None:
            return False
        del self.data["users"][ctx.user]
        return True

    def getChannelDict(self, ctx: "CtxObject") -> dict[str, Any]:
        server = self.getServer(ctx)
        if server is None:
            raise KeyError(ctx.server)
        return server["channels"]

    def getUserDict(self, ctx: "CtxObject" | None = None) -> dict[str, Any]:
        return self.data["users"]

    # ------------------------------------------------------------------
    # Moderation and Mudae repositories
    # ------------------------------------------------------------------

    def load_banned_users(self) -> dict[str, Any]:
        with self._database_lock:
            rows = self.connection.execute(
                "SELECT user_id, value_json FROM banned_users"
            ).fetchall()
        return {str(row["user_id"]): json.loads(row["value_json"]) for row in rows}

    def replace_banned_users(self, banned_users: Mapping[str, Any]) -> None:
        with self._database_lock:
            self.connection.execute("BEGIN IMMEDIATE")
            try:
                self.connection.execute("DELETE FROM banned_users")
                self.connection.executemany(
                    "INSERT INTO banned_users(user_id, value_json) VALUES (?, ?)",
                    [
                        (str(user_id), _compact_json(value))
                        for user_id, value in banned_users.items()
                    ],
                )
                self.connection.commit()
            except Exception:
                self.connection.rollback()
                raise

    def load_badwords(self) -> list[str]:
        with self._database_lock:
            return [
                str(row[0])
                for row in self.connection.execute(
                    "SELECT word FROM badwords ORDER BY word"
                )
            ]

    def add_mudae_key_events(
        self,
        rows: Iterable[tuple[str, str, str, int]],
    ) -> None:
        rows = list(rows)
        if not rows:
            return
        with self._database_lock:
            self.connection.executemany(
                """
                INSERT INTO mudae_key_events(user_id, key_type, rarity, occurred_at)
                VALUES (?, ?, ?, ?)
                """,
                rows,
            )
            self.connection.commit()

    def count_mudae_keys(
        self,
        user_id: str,
        key_type: str,
        since_timestamp: int,
    ) -> dict[str, int]:
        with self._database_lock:
            rows = self.connection.execute(
                """
                SELECT rarity, COUNT(*) AS amount
                FROM mudae_key_events
                WHERE user_id = ? AND key_type = ? AND occurred_at >= ?
                GROUP BY rarity
                """,
                (str(user_id), str(key_type), int(since_timestamp)),
            ).fetchall()
        return {str(row["rarity"]): int(row["amount"]) for row in rows}

    def delete_old_mudae_keys(self, cutoff_timestamp: int) -> int:
        with self._database_lock:
            cursor = self.connection.execute(
                "DELETE FROM mudae_key_events WHERE occurred_at < ?",
                (int(cutoff_timestamp),),
            )
            self.connection.commit()
            return int(cursor.rowcount)

    def load_soulmates(self) -> dict[str, list[str]]:
        with self._database_lock:
            rows = self.connection.execute(
                """
                SELECT owner_key, character_name
                FROM mudae_soulmates
                ORDER BY owner_key, source_position, character_name
                """
            ).fetchall()
        result: dict[str, list[str]] = {}
        for row in rows:
            result.setdefault(str(row["owner_key"]), []).append(
                str(row["character_name"])
            )
        return result

    def replace_soulmates(self, owner_key: str, characters: Iterable[str]) -> None:
        characters = list(characters)
        with self._database_lock:
            self.connection.execute("BEGIN IMMEDIATE")
            try:
                self.connection.execute(
                    "DELETE FROM mudae_soulmates WHERE owner_key = ?",
                    (str(owner_key),),
                )
                self.connection.executemany(
                    """
                    INSERT INTO mudae_soulmates(owner_key, character_name, source_position)
                    VALUES (?, ?, ?)
                    """,
                    [
                        (str(owner_key), str(character), position)
                        for position, character in enumerate(characters)
                    ],
                )
                self.connection.commit()
            except Exception:
                self.connection.rollback()
                raise

    def load_waifus(self) -> dict[str, list[Any]]:
        with self._database_lock:
            rows = self.connection.execute(
                """
                SELECT character_name, series_name, key_count
                FROM mudae_waifus
                ORDER BY source_position, character_name
                """
            ).fetchall()
        return {
            str(row["character_name"]): [
                str(row["series_name"]),
                int(row["key_count"]),
            ]
            for row in rows
        }
