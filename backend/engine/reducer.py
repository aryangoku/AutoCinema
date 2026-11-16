"""Pure action semantics shared by runtime, replay, and future planning."""

from typing import Any

from .models import Belief, Command, Event, GameState, Holder, Kind, Result, digest

VERBS = {
    "inspect": Kind.INSPECT,
    "read": Kind.INSPECT,
    "take": Kind.TAKE,
    "unlock": Kind.UNLOCK,
    "talk": Kind.TALK,
    "present": Kind.PRESENT_EVIDENCE,
    "finish": Kind.START_ENDING,
    "leave": Kind.START_ENDING,
}


def initial_state(world: dict[str, Any], session_id: str) -> GameState:
    return GameState(
        world_id=world["world_id"],
        world_schema_version=world["schema_version"],
        world_hash=digest(world),
        session_id=session_id,
        current_location=world["start_location"],
        rng_state=f"seed:{world['seed']}:unused",
        items={i["id"]: Holder(kind="location", id=i["initial_location"]) for i in world["items"]},
        doors={d["id"]: d["initial_state"] for d in world["doors"]},
        npc_locations={c["id"]: c["start_location"] for c in world["characters"]},
        npc_beliefs={
            c["id"]: tuple(Belief(fact_id=f) for f in sorted(c["initial_known_fact_ids"]))
            for c in world["characters"]
        },
        facts_true=tuple(sorted(f["id"] for f in world["facts"])),
    )


def invariant_errors(world: dict[str, Any], state: GameState) -> list[str]:
    errors = []
    ids = {
        key: {x["id"] for x in world[key]}
        for key in ("locations", "items", "doors", "characters", "facts", "endings")
    }
    if (
        state.world_hash != digest(world)
        or state.world_id != world["world_id"]
        or state.world_schema_version != world["schema_version"]
    ):
        errors.append("WORLD_MISMATCH")
    if state.current_location not in ids["locations"]:
        errors.append("INVALID_LOCATION")
    if set(state.items) != ids["items"]:
        errors.append("INVALID_ITEM_SET")
    portable = {i["id"] for i in world["items"] if i["portable"]}
    for item_id, holder in state.items.items():
        if holder.kind == "location" and holder.id not in ids["locations"]:
            errors.append("INVALID_HOLDER")
        if holder.kind == "inventory" and (holder.id != "player" or item_id not in portable):
            errors.append("INVALID_INVENTORY")
    if set(state.doors) != ids["doors"]:
        errors.append("INVALID_DOOR_SET")
    if (
        set(state.npc_locations) != ids["characters"]
        or not set(state.npc_locations.values()) <= ids["locations"]
    ):
        errors.append("INVALID_NPC_LOCATION")
    if set(state.npc_beliefs) != ids["characters"]:
        errors.append("INVALID_NPC_BELIEFS")
    for beliefs in state.npc_beliefs.values():
        if not {b.fact_id for b in beliefs} <= ids["facts"]:
            errors.append("INVALID_NPC_FACT")
    flags = {e["ref"] for a in world["actions"] for e in a["effects"] if e["type"] == "set_flag"}
    for values, allowed in (
        (state.player_known_facts, ids["facts"]),
        (state.facts_true, ids["facts"]),
        (state.flags, flags),
    ):
        if len(values) != len(set(values)) or not set(values) <= allowed:
            errors.append("INVALID_FACT_OR_FLAG")
    if set(state.facts_true) != ids["facts"]:
        errors.append("INVALID_CANONICAL_TRUTH")
    if state.event_seq != state.state_version:
        errors.append("INVALID_SEQUENCE")
    if state.ending_id is not None:
        ending = next((e for e in world["endings"] if e["id"] == state.ending_id), None)
        if ending is None or not all(predicate(p, state) for p in ending["requires"]):
            errors.append("INVALID_ENDING")
    return errors


def predicate(rule: dict[str, str], state: GameState) -> bool:
    ref = rule["ref"]
    match rule["type"]:
        case "has_item":
            return ref in state.player_inventory
        case "knows_fact":
            return ref in state.player_known_facts
        case "at_location":
            return ref == state.current_location
        case "flag_true":
            return ref in state.flags
        case "door_unlocked":
            return state.doors.get(ref) == "open"
        case _:
            return False


def reject(state: GameState, code: str) -> tuple[GameState, Result]:
    return state, Result(
        accepted=False, code=code, state_version=state.state_version, state_hash=state.checksum()
    )


def present(world: dict[str, Any], state: GameState, target: str) -> bool:
    if target in state.items:
        holder = state.items[target]
        return holder.id == ("player" if holder.kind == "inventory" else state.current_location)
    if target in state.npc_locations:
        return state.npc_locations[target] == state.current_location
    if target in state.doors:
        door = next(d for d in world["doors"] if d["id"] == target)
        return state.current_location in (door["location_a"], door["location_b"])
    return target == state.current_location


def reduce_command(
    world: dict[str, Any], state: GameState, command: Command
) -> tuple[GameState, Result]:
    """Return an isolated draft and result. Never mutate state or world on rejection."""
    if invariant_errors(world, state):
        return reject(state, "INVALID_STATE")
    if command.session_id != state.session_id:
        return reject(state, "WRONG_SESSION")
    if command.actor_id != "player":
        return reject(state, "UNAUTHORIZED_ACTOR")
    if command.expected_state_version != state.state_version:
        return reject(state, "VERSION_CONFLICT")
    if command.args:
        return reject(state, "UNSUPPORTED_ARGUMENTS")
    if state.ending_id is not None:
        return reject(state, "GAME_FINISHED")
    draft = state.model_copy(deep=True)
    dialogue = None
    if command.action_id == "travel:" + command.target_id:
        kind = Kind.TRAVEL
        location = next(x for x in world["locations"] if x["id"] == state.current_location)
        exits = [e for e in location["exits"] if e["to_location_id"] == command.target_id]
        if not exits:
            return reject(state, "NO_ROUTE")
        if not any(e["door_id"] is None or state.doors[e["door_id"]] == "open" for e in exits):
            return reject(state, "DOOR_BLOCKED")
        draft = draft.model_copy(update={"current_location": command.target_id})
    else:
        action = next((a for a in world["actions"] if a["id"] == command.action_id), None)
        if (
            command.action_id == "talk:" + command.target_id
            and command.target_id in state.npc_locations
        ):
            action = {
                "verb": "talk",
                "target_id": command.target_id,
                "location_id": state.npc_locations[command.target_id],
                "preconditions": [],
                "effects": [],
            }
        if action is None:
            return reject(state, "UNKNOWN_ACTION")
        kind = VERBS[action["verb"]]
        if command.target_id != action["target_id"]:
            return reject(state, "TARGET_MISMATCH")
        if action["location_id"] != state.current_location or not present(
            world, state, command.target_id
        ):
            return reject(state, "NOT_PRESENT")
        if not all(predicate(p, state) for p in action["preconditions"]):
            return reject(state, "PRECONDITION_FAILED")
        if kind == Kind.TALK:
            npc = next((c for c in world["characters"] if c["id"] == command.target_id), None)
            if npc is None:
                return reject(state, "INVALID_TARGET_TYPE")
            dialogue = npc["dialogue_fallback"]
        if kind == Kind.PRESENT_EVIDENCE and command.target_id not in state.npc_locations:
            return reject(state, "INVALID_TARGET_TYPE")
        if kind == Kind.UNLOCK and command.target_id not in state.doors:
            return reject(state, "INVALID_TARGET_TYPE")
        pending_endings = []
        for effect in action["effects"]:
            ref = effect["ref"]
            match effect["type"]:
                case "learn_fact":
                    draft = draft.model_copy(
                        update={
                            "player_known_facts": tuple(
                                sorted(set(draft.player_known_facts) | {ref})
                            )
                        }
                    )
                case "set_flag":
                    draft = draft.model_copy(
                        update={"flags": tuple(sorted(set(draft.flags) | {ref}))}
                    )
                case "take_item":
                    holder = draft.items[ref]
                    item = next(i for i in world["items"] if i["id"] == ref)
                    if (
                        not item["portable"]
                        or holder.kind != "location"
                        or holder.id != state.current_location
                    ):
                        return reject(state, "ITEM_UNAVAILABLE")
                    draft.items[ref] = Holder(kind="inventory", id="player")
                case "unlock_door":
                    if not present(world, draft, ref):
                        return reject(state, "NOT_PRESENT")
                    if draft.doors[ref] == "open":
                        return reject(state, "DOOR_ALREADY_OPEN")
                    draft.doors[ref] = "open"
                case "trigger_ending":
                    pending_endings.append(ref)
                case _:
                    return reject(state, "UNSUPPORTED_EFFECT")
        # Endings are checked against the complete atomic draft, not effect ordering.
        if len(pending_endings) > 1:
            return reject(state, "MULTIPLE_ENDINGS")
        if pending_endings:
            ending = next(e for e in world["endings"] if e["id"] == pending_endings[0])
            if not all(predicate(p, draft) for p in ending["requires"]):
                return reject(state, "ENDING_REQUIREMENTS_FAILED")
            draft = draft.model_copy(update={"ending_id": ending["id"]})
    if draft == state and dialogue is None:
        return reject(state, "NO_CHANGE")
    draft = draft.model_copy(
        update={
            "state_version": state.state_version + 1,
            "event_seq": state.event_seq + 1,
            "sim_time_minutes": state.sim_time_minutes + 1,
            "interactions_seen": tuple(sorted(set(state.interactions_seen) | {command.action_id})),
        }
    )
    if invariant_errors(world, draft):
        return reject(state, "INVARIANT_FAILED")
    before, after = state.model_dump(mode="json"), draft.model_dump(mode="json")
    event = Event(
        event_id=f"{state.session_id}:{draft.event_seq}",
        seq=draft.event_seq,
        session_id=state.session_id,
        command_id=command.command_id,
        actor_id=command.actor_id,
        action_id=command.action_id,
        entity_ids=(command.target_id,),
        sim_time_minutes=draft.sim_time_minutes,
        state_diff={key: value for key, value in after.items() if value != before[key]},
        world_schema_version=state.world_schema_version,
        state_hash_after=draft.checksum(),
        rng_state_before=state.rng_state,
        rng_state_after=draft.rng_state,
    )
    return draft, Result(
        accepted=True,
        code=kind.value,
        state_version=draft.state_version,
        state_hash=draft.checksum(),
        events=(event,),
        dialogue=dialogue,
    )
