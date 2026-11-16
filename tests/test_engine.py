import copy
import json
import random
import sqlite3
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

import pytest
from jsonschema import Draft202012Validator
from pydantic import ValidationError

from backend.engine import Command, GameEngine
from backend.engine.demo import TRUTH_ROUTE, UNRESOLVED_ROUTE, issue
from backend.engine.models import Holder
from backend.engine.reducer import initial_state, invariant_errors, predicate, reduce_command
from backend.engine.service import SaveError
from backend.validator.world import ROOT


@pytest.fixture
def world():
    return json.loads((ROOT / "examples/blackwater_harbor.json").read_text(encoding="utf-8"))


@pytest.fixture
def engine(world):
    with GameEngine(world, session_id="test_session") as value:
        yield value


def travel(engine, destination):
    result = issue(engine, "travel:" + destination, destination)
    assert result.accepted, result


def run_route(engine, route):
    for action, target in route:
        assert issue(engine, action, target).accepted


def command(engine, action="act_read_manifest", target="item_manifest", **updates):
    values = dict(
        command_id="cmd_test",
        session_id=engine.session_id,
        expected_state_version=engine.state.state_version,
        action_id=action,
        target_id=target,
    )
    values.update(updates)
    return Command(**values)


def assert_rejected(engine, cmd, code):
    before, events = engine.state, engine.events
    result = engine.dispatch(cmd)
    assert not result.accepted and result.code == code
    assert engine.state == before
    assert engine.events == events
    assert result.state_hash == before.checksum()


def test_initial_state_has_no_player_secrets(engine, world):
    state = engine.state
    assert state.player_inventory == () and state.player_known_facts == ()
    assert state.current_location == "loc_harbor"
    assert not invariant_errors(world, state)
    assert "fact_elena_helped" in {b.fact_id for b in state.npc_beliefs["npc_elena"]}
    assert "fact_elena_helped" not in {b.fact_id for b in state.npc_beliefs["npc_marcus"]}


@pytest.mark.parametrize(
    "updates,code",
    [
        ({"session_id": "other"}, "WRONG_SESSION"),
        ({"actor_id": "npc_elena"}, "UNAUTHORIZED_ACTOR"),
        ({"expected_state_version": 9}, "VERSION_CONFLICT"),
        ({"args": {"grant_fact": "fact_elena_helped"}}, "UNSUPPORTED_ARGUMENTS"),
        ({"action_id": "execute_script"}, "UNKNOWN_ACTION"),
        ({"target_id": "item_key"}, "TARGET_MISMATCH"),
    ],
)
def test_rejected_commands_are_atomic(engine, updates, code):
    assert_rejected(engine, command(engine, **updates), code)


def test_remote_inspection_rejected(engine):
    assert_rejected(engine, command(engine, "act_read_journal", "item_journal"), "NOT_PRESENT")


def test_no_teleport(engine):
    assert_rejected(
        engine, command(engine, "travel:loc_lighthouse_int", "loc_lighthouse_int"), "NO_ROUTE"
    )


def test_locked_door_blocks_travel(engine):
    travel(engine, "loc_lighthouse_ext")
    assert_rejected(
        engine, command(engine, "travel:loc_lighthouse_int", "loc_lighthouse_int"), "DOOR_BLOCKED"
    )


def test_unlock_requires_key(engine):
    travel(engine, "loc_lighthouse_ext")
    assert_rejected(
        engine, command(engine, "act_unlock_lighthouse", "door_lighthouse"), "PRECONDITION_FAILED"
    )


def test_take_exactly_once_and_key_retained(engine):
    run_route(engine, TRUTH_ROUTE[:8])
    assert engine.state.player_inventory == ("item_key",)
    assert engine.state.doors["door_lighthouse"] == "open"
    assert_rejected(
        engine, command(engine, "act_unlock_lighthouse", "door_lighthouse"), "DOOR_ALREADY_OPEN"
    )
    travel(engine, "loc_harbor")
    travel(engine, "loc_tavern")
    assert_rejected(engine, command(engine, "act_take_key", "item_key"), "ITEM_UNAVAILABLE")


def test_confrontation_gated_by_evidence(engine):
    travel(engine, "loc_tavern")
    assert_rejected(
        engine, command(engine, "act_confront_elena", "npc_elena"), "PRECONDITION_FAILED"
    )
    assert "fact_elena_helped" not in engine.state.player_known_facts


def test_ending_requirements_are_independent(world):
    world["actions"][-2]["preconditions"] = []
    with GameEngine(world) as engine:
        travel(engine, "loc_tavern")
        assert_rejected(
            engine, command(engine, "act_finish_truth", "npc_elena"), "ENDING_REQUIREMENTS_FAILED"
        )


def test_effects_roll_back_if_later_effect_fails(world):
    world["actions"][0]["effects"].append({"type": "take_item", "ref": "item_key"})
    with GameEngine(world) as engine:
        assert_rejected(engine, command(engine), "ITEM_UNAVAILABLE")
        assert engine.state.player_known_facts == ()


def test_two_endings_in_one_action_rejected(world):
    world["actions"][-1]["effects"].append({"type": "trigger_ending", "ref": "ending_truth"})
    with GameEngine(world) as engine:
        assert_rejected(engine, command(engine, "act_leave_town", "loc_harbor"), "MULTIPLE_ENDINGS")


@pytest.mark.parametrize(
    "route,ending", [(TRUTH_ROUTE, "ending_truth"), (UNRESOLVED_ROUTE, "ending_unresolved")]
)
def test_complete_routes_and_replay(world, route, ending):
    with (
        GameEngine(world, session_id="same") as first,
        GameEngine(world, session_id="same") as second,
    ):
        run_route(first, route)
        run_route(second, route)
        assert first.state.ending_id == ending
        assert first.state == second.state == first.replay()
        assert first.events == second.events
        assert_rejected(first, command(first), "GAME_FINISHED")


def test_talk_is_offline_and_does_not_learn_hidden_facts(engine):
    travel(engine, "loc_tavern")
    before = engine.state
    result = issue(engine, "talk:npc_elena", "npc_elena")
    assert result.accepted and result.dialogue == "The lighthouse has been abandoned for years."
    assert engine.state.player_known_facts == before.player_known_facts
    assert engine.state.npc_beliefs == before.npc_beliefs


def test_remote_talk_rejected(engine):
    assert_rejected(engine, command(engine, "talk:npc_elena", "npc_elena"), "NOT_PRESENT")


def test_inspect_learns_only_authored_fact(engine):
    result = engine.dispatch(command(engine))
    assert result.accepted
    assert engine.state.player_known_facts == ("fact_manifest_after_disappearance",)
    assert len(result.events) == 1
    assert result.events[0].state_hash_after == engine.state.checksum()


def test_same_command_id_returns_original_result(engine):
    cmd = command(engine)
    first = engine.dispatch(cmd)
    travel(engine, "loc_tavern")
    before = engine.state
    assert engine.dispatch(cmd) == first
    assert engine.state == before
    assert len(engine.events) == 2


def test_id_reuse_with_changed_payload_rejected(engine):
    cmd = command(engine)
    engine.dispatch(cmd)
    assert_rejected(engine, cmd.model_copy(update={"target_id": "item_key"}), "COMMAND_ID_CONFLICT")


def test_state_and_world_are_defensive_copies(world):
    with GameEngine(world) as engine:
        world["items"].clear()
        snapshot = engine.state
        snapshot.items["item_key"] = Holder(kind="inventory", id="player")
        assert engine.state.player_inventory == ()
        assert issue(engine, "act_read_manifest", "item_manifest").accepted


def test_preview_does_not_change_state_or_leak_secret_actions(engine):
    before = engine.state
    options = engine.available_commands()
    assert engine.state == before and engine.events == ()
    ids = {o["action_id"] for o in options}
    assert "act_read_manifest" in ids and "act_confront_elena" not in ids
    view = json.dumps(engine.player_view())
    for secret in (
        "fact_elena_helped",
        "private_goal",
        "npc_beliefs",
        "facts_true",
        "antagonist_or_secret",
    ):
        assert secret not in view


def test_event_and_command_schema_parity(engine):
    cmd = command(engine)
    result = engine.dispatch(cmd)
    for name, payload in (("command", cmd), ("event", result.events[0])):
        schema = json.loads((ROOT / f"schemas/{name}.schema.json").read_text())
        Draft202012Validator(schema).validate(payload.model_dump(mode="json"))


@pytest.mark.parametrize(
    "updates",
    [
        {"expected_state_version": -1},
        {"expected_state_version": True},
        {"command_id": ""},
        {"action_id": 123},
        {"args": {"script": []}},
        {"extra": 1},
    ],
)
def test_strict_command_contract(engine, updates):
    with pytest.raises(ValidationError):
        command(engine, **updates)


@pytest.mark.parametrize(
    "rule,expected",
    [
        ({"type": "at_location", "ref": "loc_harbor"}, True),
        ({"type": "has_item", "ref": "item_key"}, False),
        ({"type": "knows_fact", "ref": "fact_elena_helped"}, False),
        ({"type": "door_unlocked", "ref": "door_lighthouse"}, False),
        ({"type": "flag_true", "ref": "flag_elena_confronted"}, False),
        ({"type": "execute_script", "ref": "x"}, False),
    ],
)
def test_predicate_dispatch(engine, rule, expected):
    assert predicate(rule, engine.state) is expected


def test_pure_reducer_does_not_mutate_inputs(world):
    before = copy.deepcopy(world)
    state = initial_state(world, "pure")
    cmd = Command(
        command_id="read",
        session_id="pure",
        expected_state_version=0,
        action_id="act_read_manifest",
        target_id="item_manifest",
    )
    candidate, result = reduce_command(world, state, cmd)
    assert result.accepted and candidate != state
    assert state.player_known_facts == () and world == before


def test_randomized_legal_and_illegal_commands_keep_invariants(engine, world):
    rng = random.Random(1042)
    for i in range(100):
        candidates = engine.available_commands()
        if candidates and rng.random() < 0.6:
            chosen = rng.choice(candidates)
            cmd = command(
                engine, chosen["action_id"], chosen["target_id"], command_id=f"random:{i}"
            )
        else:
            cmd = command(engine, action="unknown", command_id=f"random:{i}")
        before = engine.state
        result = engine.dispatch(cmd)
        assert not invariant_errors(world, engine.state)
        if not result.accepted:
            assert engine.state == before
    assert engine.replay() == engine.state


@pytest.mark.parametrize("route", [TRUTH_ROUTE, UNRESOLVED_ROUTE])
def test_persistence_checkpoint_tail_and_idempotency(world, tmp_path, route):
    path = tmp_path / "save.sqlite3"
    with GameEngine(world, path, "persisted") as engine:
        cmd = command(engine, route[0][0], route[0][1])
        original = engine.dispatch(cmd)
        checkpoint = engine.save()
    with GameEngine.load(world, path, "persisted") as loaded:
        assert loaded.state.checksum() == checkpoint
        assert loaded.dispatch(cmd) == original
        run_route(loaded, route[1:])
        expected = loaded.state
    # No explicit save after the remaining route: recover the committed event tail.
    with GameEngine.load(world, path, "persisted") as recovered:
        assert recovered.state == expected == recovered.replay()


def test_database_failure_rolls_back_event_and_version(engine):
    engine._db.execute(
        "CREATE TRIGGER fail_update BEFORE UPDATE ON sessions "
        "BEGIN SELECT RAISE(ABORT, 'simulated write failure'); END"
    )
    before = engine.state
    with pytest.raises(sqlite3.Error):
        engine.dispatch(command(engine))
    assert engine.state == before and engine.events == ()
    engine._db.execute("DROP TRIGGER fail_update")
    assert engine.dispatch(command(engine)).accepted


def test_two_connections_serialize_writes(world, tmp_path):
    path = tmp_path / "save.sqlite3"
    with (
        GameEngine(world, path, "shared") as first,
        GameEngine.load(world, path, "shared") as second,
    ):
        a = command(first, command_id="first")
        b = command(second, "travel:loc_tavern", "loc_tavern", command_id="second")
        with ThreadPoolExecutor(max_workers=2) as pool:
            futures = [pool.submit(first.dispatch, a), pool.submit(second.dispatch, b)]
            results = [f.result() for f in futures]
        assert sum(r.accepted for r in results) == 1
        assert {r.code for r in results if not r.accepted} == {"VERSION_CONFLICT"}
        assert first.state == second.state
        assert len(first.events) == 1


def test_save_rejects_changed_world(world, tmp_path):
    path = tmp_path / "save.sqlite3"
    with GameEngine(world, path, "original"):
        pass
    world["seed"] += 1
    with pytest.raises(SaveError, match="different world"):
        GameEngine.load(world, path, "original")


@pytest.mark.parametrize("corruption", ["snapshot", "event", "missing_event", "version"])
def test_corrupt_save_rejected(world, tmp_path, corruption):
    path = tmp_path / "save.sqlite3"
    with GameEngine(world, path, "corrupt") as engine:
        issue(engine, "act_read_manifest", "item_manifest")
        engine.save()
    with sqlite3.connect(path) as db:
        if corruption == "snapshot":
            db.execute("UPDATE sessions SET snapshot_json='{}'")
        elif corruption == "event":
            db.execute("UPDATE events SET command_json='{}'")
        elif corruption == "missing_event":
            db.execute("DELETE FROM events")
        else:
            db.execute("PRAGMA user_version=999")
    with pytest.raises(SaveError):
        GameEngine.load(world, path, "corrupt")


def test_missing_session_does_not_silently_create(world, tmp_path):
    path = tmp_path / "save.sqlite3"
    with pytest.raises(SaveError):
        GameEngine.load(world, path, "missing")
    with GameEngine(world, path, "existing"):
        pass
    with pytest.raises(SaveError):
        GameEngine.load(world, path, "missing")


def test_automatic_checkpoint_and_resume(world, tmp_path):
    path = tmp_path / "save.sqlite3"
    with GameEngine(world, path, "long") as engine:
        for _ in range(51):
            assert issue(engine, "talk:npc_marcus", "npc_marcus").accepted
        assert engine._db.execute("SELECT snapshot_seq FROM sessions").fetchone()[0] == 50
        expected = engine.state
    with GameEngine.load(world, path, "long") as loaded:
        assert loaded.state == expected == loaded.replay()


def test_interactive_console_save_and_resume(tmp_path):
    database = tmp_path / "console.sqlite3"
    cli = [sys.executable, str(ROOT / "tools/play_console.py"), "--database", str(database)]
    first = subprocess.run(cli, input="invalid\ns\nq\n", text=True, capture_output=True, timeout=30)
    assert first.returncode == 0, first.stderr
    assert "Choose one of the listed options." in first.stdout
    assert "Saved. Resume with --session" in first.stdout
    session = next(
        line.split(": ", 1)[1] for line in first.stdout.splitlines() if line.startswith("Session: ")
    )
    second = subprocess.run(
        cli + ["--session", session], input="q\n", text=True, capture_output=True, timeout=30
    )
    assert second.returncode == 0, second.stderr
    assert f"Session: {session}" in second.stdout


def test_console_missing_save_reports_error(tmp_path):
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "tools/play_console.py"),
            "--database",
            str(tmp_path / "missing.sqlite3"),
            "--session",
            "missing",
        ],
        text=True,
        capture_output=True,
        timeout=30,
    )
    assert result.returncode == 2
    assert "Save database does not exist" in result.stderr
