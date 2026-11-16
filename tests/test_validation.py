import asyncio
import copy
import json
import subprocess
import sys

import httpx
import pytest
from jsonschema import Draft202012Validator

from backend.app.main import app
from backend.validator.world import ROOT, SCHEMA_PATH, validate_world


@pytest.fixture
def world():
    return json.loads((ROOT / "examples/blackwater_harbor.json").read_text(encoding="utf-8"))


def test_canonical_fixture_and_no_mutation(world):
    before = copy.deepcopy(world)
    report = validate_world(world)
    assert report.status == "PASS"
    assert report.issues == []
    assert world == before


@pytest.mark.parametrize(
    "category", ["locations", "doors", "characters", "items", "facts", "actions", "endings"]
)
def test_duplicate_ids(world, category):
    world[category].append(copy.deepcopy(world[category][0]))
    assert "DUPLICATE_ID" in {i.code for i in validate_world(world).issues}


def test_cross_category_duplicate(world):
    world["facts"][0]["id"] = world["items"][0]["id"]
    assert "DUPLICATE_ID" in {i.code for i in validate_world(world).issues}


@pytest.mark.parametrize("field", ["id", "prefab_id", "exits"])
def test_missing_required_fields(world, field):
    del world["locations"][0][field]
    assert validate_world(world).status == "FAIL_SCHEMA"


@pytest.mark.parametrize(
    "category,field",
    [
        ("actions", "target_id"),
        ("actions", "location_id"),
        ("characters", "start_location"),
        ("items", "initial_location"),
        ("doors", "location_a"),
        ("doors", "location_b"),
    ],
)
def test_missing_reference(world, category, field):
    world[category][0][field] = "missing_entity"
    report = validate_world(world)
    assert report.status == "FAIL_SEMANTIC"
    assert any(i.code == "MISSING_REFERENCE" and i.path.endswith(field) for i in report.issues)


@pytest.mark.parametrize("category", ["locations", "characters", "items"])
def test_missing_prefab(world, category):
    world[category][0]["prefab_id"] = "missing_prefab"
    assert "MISSING_PREFAB" in {i.code for i in validate_world(world).issues}


def test_invalid_start(world):
    world["start_location"] = "loc_missing"
    assert "INVALID_START_LOCATION" in {i.code for i in validate_world(world).issues}


@pytest.mark.parametrize("field", ["initial_known_fact_ids", "secret_fact_ids"])
def test_missing_npc_fact(world, field):
    world["characters"][0][field] = ["fact_missing"]
    assert "MISSING_REFERENCE" in {i.code for i in validate_world(world).issues}


def test_missing_truth_fact(world):
    world["truth"]["secret_fact_ids"] = ["fact_missing"]
    assert "MISSING_REFERENCE" in {i.code for i in validate_world(world).issues}


@pytest.mark.parametrize(
    "field,operation",
    [
        ("effects", {"type": "learn_fact", "ref": "fact_missing"}),
        ("preconditions", {"type": "has_item", "ref": "loc_harbor"}),
        ("preconditions", {"type": "flag_true", "ref": "flag_missing"}),
    ],
)
def test_typed_reference(world, field, operation):
    world["actions"][0][field] = [operation]
    assert "MISSING_REFERENCE" in {i.code for i in validate_world(world).issues}


def test_missing_exit_destination_and_door(world):
    world["locations"][0]["exits"][0] = {"to_location_id": "loc_missing", "door_id": "door_missing"}
    assert len([i for i in validate_world(world).issues if i.code == "MISSING_REFERENCE"]) == 2


def test_door_endpoints(world):
    world["locations"][0]["exits"][0]["door_id"] = "door_lighthouse"
    assert "DOOR_ENDPOINT_MISMATCH" in {i.code for i in validate_world(world).issues}


def test_manifest_kind(world):
    world["asset_manifest"][0]["kind"] = "npc"
    assert "PREFAB_KIND_MISMATCH" in {i.code for i in validate_world(world).issues}


def test_duplicate_manifest(world):
    world["asset_manifest"].append(world["asset_manifest"][0])
    assert "DUPLICATE_ASSET" in {i.code for i in validate_world(world).issues}


def test_invalid_take(world):
    world["items"][1]["portable"] = False
    assert "INVALID_TAKE" in {i.code for i in validate_world(world).issues}


def test_untriggered_ending(world):
    world["actions"] = [a for a in world["actions"] if a["verb"] != "finish"]
    assert "ENDING_NOT_TRIGGERED" in {i.code for i in validate_world(world).issues}


def test_unknown_ending_condition(world):
    world["endings"][0]["requires"][0]["ref"] = "flag_missing"
    assert "MISSING_REFERENCE" in {i.code for i in validate_world(world).issues}


@pytest.mark.parametrize("value", [None, [], {}, "execute this", 12])
def test_malformed_top_level(value):
    assert validate_world(value).status == "FAIL_SCHEMA"


@pytest.mark.parametrize("mutation", ["unknown_effect", "path", "version", "extra"])
def test_schema_adapter_parity(world, mutation):
    if mutation == "unknown_effect":
        world["actions"][0]["effects"][0]["type"] = "execute_script"
    elif mutation == "path":
        world["locations"][0]["prefab_id"] = "../../malicious.gd"
    elif mutation == "version":
        world["schema_version"] = "2.0.0"
    else:
        world["shell_command"] = "untrusted input"
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    assert not Draft202012Validator(schema).is_valid(world)
    assert validate_world(world).status == "FAIL_SCHEMA"


def test_all_schemas_are_valid():
    for path in (ROOT / "schemas").glob("*.json"):
        Draft202012Validator.check_schema(json.loads(path.read_text(encoding="utf-8")))


@pytest.mark.parametrize(
    "mode,expected",
    [
        ("valid", "PASS"),
        ("broken", "FAIL_SEMANTIC"),
        ("malformed", "FAIL_INPUT"),
        ("absent", "FAIL_INPUT"),
    ],
)
def test_cli(world, tmp_path, mode, expected):
    path = tmp_path / "world.json"
    if mode == "broken":
        world["start_location"] = "loc_missing"
    if mode != "absent":
        path.write_text("{" if mode == "malformed" else json.dumps(world), encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(ROOT / "tools/validate_world.py"), str(path)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == (0 if expected == "PASS" else 2)
    assert json.loads(result.stdout)["status"] == expected


def test_health():
    async def request():
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://test"
        ) as client:
            return await client.get("/health")

    response = asyncio.run(request())
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": "0.2.0", "milestone": 1}
