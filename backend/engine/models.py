"""Strict runtime contracts. WorldIR remains governed by its JSON Schema."""

import hashlib
import json
from enum import StrEnum
from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field

ID = Annotated[str, Field(min_length=1)]
Version = Annotated[int, Field(ge=0)]


class Model(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)


class Command(Model):
    command_id: ID
    session_id: ID
    expected_state_version: Version
    actor_id: ID = "player"
    action_id: ID
    target_id: ID
    args: dict[str, str | int | float | bool | None] = Field(default_factory=dict)
    issued_at: str = ""


class Kind(StrEnum):
    TRAVEL = "TRAVEL"
    INSPECT = "INSPECT"
    TAKE = "TAKE"
    UNLOCK = "UNLOCK"
    TALK = "TALK"
    PRESENT_EVIDENCE = "PRESENT_EVIDENCE"
    START_ENDING = "START_ENDING"


class Holder(Model):
    kind: Literal["location", "inventory"]
    id: ID


class Belief(Model):
    fact_id: ID
    believed_truth: bool = True
    source: str = "authored_backstory"
    confidence: Annotated[float, Field(ge=0, le=1)] = 1.0


class GameState(Model):
    format_version: Literal[1] = 1
    world_id: ID
    world_schema_version: ID
    world_hash: ID
    session_id: ID
    state_version: Version = 0
    event_seq: Version = 0
    sim_time_minutes: Version = 0
    rng_state: str
    current_location: ID
    items: dict[str, Holder]
    doors: dict[str, Literal["locked", "closed", "open"]]
    npc_locations: dict[str, str]
    npc_beliefs: dict[str, tuple[Belief, ...]]
    facts_true: tuple[str, ...]
    player_known_facts: tuple[str, ...] = ()
    flags: tuple[str, ...] = ()
    interactions_seen: tuple[str, ...] = ()
    ending_id: str | None = None

    @property
    def player_inventory(self) -> tuple[str, ...]:
        # Ownership is stored once. Inventory is a projection, never a second authority.
        return tuple(sorted(k for k, v in self.items.items() if v.kind == "inventory"))

    def checksum(self) -> str:
        return digest(self.model_dump(mode="json"))


class Event(Model):
    event_id: ID
    seq: Version
    session_id: ID
    command_id: ID
    actor_id: ID
    action_id: ID
    entity_ids: tuple[str, ...]
    sim_time_minutes: Version
    state_diff: dict[str, Any]
    world_schema_version: ID
    state_hash_after: ID
    rng_state_before: str
    rng_state_after: str


class Result(Model):
    accepted: bool
    code: str
    state_version: Version
    state_hash: str
    events: tuple[Event, ...] = ()
    dialogue: str | None = None


def digest(value: Any) -> str:
    payload = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
