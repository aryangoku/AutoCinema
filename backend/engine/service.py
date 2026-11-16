"""SQLite transactions couple authoritative state versions and accepted event records."""

import copy
import json
import sqlite3
import threading
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any
from uuid import uuid4

from backend.validator import validate_world

from .models import Command, Event, GameState, Result, digest
from .reducer import initial_state, invariant_errors, reduce_command, reject


class SaveError(ValueError):
    """A save is missing, incompatible, or corrupt; never silently restart it."""


class GameEngine:
    def __init__(
        self,
        world: dict[str, Any],
        database: str | Path = ":memory:",
        session_id: str | None = None,
        *,
        create: bool = True,
    ) -> None:
        report = validate_world(world)
        if report.status != "PASS":
            raise ValueError("Invalid world: " + report.model_dump_json())
        self._world = copy.deepcopy(world)
        self.session_id = session_id or str(uuid4())
        self._lock = threading.RLock()
        self._db = sqlite3.connect(
            str(database), isolation_level=None, timeout=5, check_same_thread=False
        )
        self._db.row_factory = sqlite3.Row
        self._db.execute("PRAGMA foreign_keys=ON")
        self._db.execute("PRAGMA journal_mode=WAL")
        self._db.execute("PRAGMA synchronous=FULL")
        version = self._db.execute("PRAGMA user_version").fetchone()[0]
        if version not in (0, 1):
            self.close()
            raise SaveError("Unsupported save database version")
        self._db.executescript("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY, world_hash TEXT NOT NULL,
                snapshot_json TEXT NOT NULL, snapshot_hash TEXT NOT NULL,
                snapshot_seq INTEGER NOT NULL, state_version INTEGER NOT NULL
            );
            CREATE TABLE IF NOT EXISTS events (
                session_id TEXT NOT NULL REFERENCES sessions(session_id),
                seq INTEGER NOT NULL, command_id TEXT NOT NULL,
                command_json TEXT NOT NULL, result_json TEXT NOT NULL,
                PRIMARY KEY(session_id, seq), UNIQUE(session_id, command_id)
            );
            PRAGMA user_version=1;
        """)
        try:
            with self._transaction():
                row = self._db.execute(
                    "SELECT session_id FROM sessions WHERE session_id=?", (self.session_id,)
                ).fetchone()
                if row is None:
                    if not create:
                        raise SaveError("Saved session does not exist")
                    state = initial_state(self._world, self.session_id)
                    self._db.execute(
                        "INSERT INTO sessions VALUES (?, ?, ?, ?, 0, 0)",
                        (
                            self.session_id,
                            state.world_hash,
                            state.model_dump_json(),
                            state.checksum(),
                        ),
                    )
                self._read_state()
            self.replay()
        except Exception:
            self.close()
            raise

    @classmethod
    def load(cls, world: dict[str, Any], database: str | Path, session_id: str) -> "GameEngine":
        if not Path(database).is_file():
            raise SaveError("Save database does not exist")
        return cls(world, database, session_id, create=False)

    @contextmanager
    def _transaction(self) -> Iterator[None]:
        with self._lock:
            self._db.execute("BEGIN IMMEDIATE")
            try:
                yield
                self._db.execute("COMMIT")
            except BaseException:
                self._db.execute("ROLLBACK")
                raise

    def _read_state(self) -> GameState:
        row = self._db.execute(
            "SELECT * FROM sessions WHERE session_id=?", (self.session_id,)
        ).fetchone()
        if row is None or row["world_hash"] != digest(self._world):
            raise SaveError("Save belongs to a different world build")
        try:
            state = GameState.model_validate_json(row["snapshot_json"])
        except ValueError as exc:
            raise SaveError("Malformed snapshot") from exc
        if (
            state.session_id != self.session_id
            or state.checksum() != row["snapshot_hash"]
            or state.event_seq != row["snapshot_seq"]
            or invariant_errors(self._world, state)
        ):
            raise SaveError("Snapshot integrity check failed")
        records = self._records()
        if len(records) != row["state_version"] or any(
            record["seq"] != i + 1 for i, record in enumerate(records)
        ):
            raise SaveError("Event sequence is incomplete")
        if state.event_seq > len(records):
            raise SaveError("Snapshot is ahead of the event log")
        if state.event_seq:
            anchor = self._result(records[state.event_seq - 1])
            if anchor.state_hash != state.checksum():
                raise SaveError("Snapshot does not match its event")
        elif state != initial_state(self._world, self.session_id):
            raise SaveError("Initial snapshot does not match world")
        for record in records[state.event_seq :]:
            state = self._replay_record(state, record)
        return state

    def _records(self) -> list[sqlite3.Row]:
        return list(
            self._db.execute(
                "SELECT * FROM events WHERE session_id=? ORDER BY seq", (self.session_id,)
            )
        )

    @staticmethod
    def _result(record: sqlite3.Row) -> Result:
        try:
            return Result.model_validate_json(record["result_json"])
        except ValueError as exc:
            raise SaveError("Malformed event result") from exc

    def _replay_record(self, state: GameState, record: sqlite3.Row) -> GameState:
        try:
            command = Command.model_validate_json(record["command_json"])
        except ValueError as exc:
            raise SaveError("Malformed saved command") from exc
        candidate, result = reduce_command(self._world, state, command)
        if (
            command.command_id != record["command_id"]
            or not result.accepted
            or result != self._result(record)
            or candidate.event_seq != record["seq"]
        ):
            raise SaveError("Replay diverged from recorded result")
        return candidate

    @property
    def state(self) -> GameState:
        with self._transaction():
            return self._read_state()

    @property
    def events(self) -> tuple[Event, ...]:
        with self._transaction():
            return tuple(
                event for record in self._records() for event in self._result(record).events
            )

    def dispatch(self, command: Command) -> Result:
        try:
            with self._transaction():
                state = self._read_state()
                previous = self._db.execute(
                    "SELECT * FROM events WHERE session_id=? AND command_id=?",
                    (self.session_id, command.command_id),
                ).fetchone()
                if previous is not None:
                    if json.loads(previous["command_json"]) != command.model_dump(mode="json"):
                        return reject(state, "COMMAND_ID_CONFLICT")[1]
                    return self._result(previous)
                candidate, result = reduce_command(self._world, state, command)
                if not result.accepted:
                    return result
                self._db.execute(
                    "INSERT INTO events VALUES (?, ?, ?, ?, ?)",
                    (
                        self.session_id,
                        candidate.event_seq,
                        command.command_id,
                        command.model_dump_json(),
                        result.model_dump_json(),
                    ),
                )
                self._db.execute(
                    "UPDATE sessions SET state_version=? WHERE session_id=?",
                    (candidate.state_version, self.session_id),
                )
                if candidate.event_seq % 50 == 0:
                    self._checkpoint(candidate)
                return result
        except sqlite3.Error:
            # Transaction rollback has completed; no in-memory state was published.
            # Storage errors are operational failures, not gameplay rejection codes.
            raise

    def _checkpoint(self, state: GameState) -> None:
        self._db.execute(
            "UPDATE sessions SET snapshot_json=?, snapshot_hash=?, snapshot_seq=? "
            "WHERE session_id=?",
            (state.model_dump_json(), state.checksum(), state.event_seq, self.session_id),
        )

    def save(self) -> str:
        """Checkpoint current state. Every accepted command is already durably committed."""
        with self._transaction():
            state = self._read_state()
            self._checkpoint(state)
            return state.checksum()

    def replay(self) -> GameState:
        """Audit the complete accepted command history using the same runtime reducer."""
        with self._transaction():
            state = initial_state(self._world, self.session_id)
            for record in self._records():
                state = self._replay_record(state, record)
            if state != self._read_state():
                raise SaveError("Replay differs from snapshot and tail")
            return state

    def player_view(self) -> dict[str, Any]:
        state = self.state
        location = next(x for x in self._world["locations"] if x["id"] == state.current_location)
        return {
            "session_id": self.session_id,
            "state_version": state.state_version,
            "location": {k: location[k] for k in ("id", "name", "description")},
            "exits": [e["to_location_id"] for e in location["exits"]],
            "inventory": list(state.player_inventory),
            "known_facts": [
                {"id": f["id"], "text": f["text"]}
                for f in self._world["facts"]
                if f["id"] in state.player_known_facts
            ],
            "characters": [
                {"id": c["id"], "name": c["name"], "public_role": c["public_role"]}
                for c in self._world["characters"]
                if state.npc_locations[c["id"]] == state.current_location
            ],
            "ending_id": state.ending_id,
        }

    def available_commands(self) -> list[dict[str, str]]:
        """Offer only currently legal commands, verified by the authoritative reducer."""
        state = self.state
        candidates = [
            {"action_id": a["id"], "target_id": a["target_id"], "label": a["label"]}
            for a in self._world["actions"]
        ]
        candidates += [
            {
                "action_id": "travel:" + loc["id"],
                "target_id": loc["id"],
                "label": "Travel to " + loc["name"],
            }
            for loc in self._world["locations"]
        ]
        candidates += [
            {
                "action_id": "talk:" + npc["id"],
                "target_id": npc["id"],
                "label": "Talk to " + npc["name"],
            }
            for npc in self._world["characters"]
        ]
        return [
            c
            for c in candidates
            if reduce_command(
                self._world,
                state,
                Command(
                    command_id="preview",
                    session_id=self.session_id,
                    expected_state_version=state.state_version,
                    action_id=c["action_id"],
                    target_id=c["target_id"],
                ),
            )[1].accepted
        ]

    def close(self) -> None:
        self._db.close()

    def __enter__(self) -> "GameEngine":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()
