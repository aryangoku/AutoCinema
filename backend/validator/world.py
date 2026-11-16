"""Schema-first WorldIR adapter. No generated code or asset paths are executed."""

import json
from collections import Counter
from pathlib import Path
from typing import Any, Literal

from jsonschema import Draft202012Validator
from pydantic import BaseModel, ConfigDict

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / "schemas/world.schema.json"
CATEGORIES = ("locations", "doors", "characters", "items", "facts", "actions", "endings")


class Issue(BaseModel):
    model_config = ConfigDict(frozen=True)
    code: str
    path: str
    message: str


class ValidationReport(BaseModel):
    status: Literal["PASS", "FAIL_SCHEMA", "FAIL_SEMANTIC", "FAIL_INPUT"]
    issues: list[Issue]
    scope: str = "schema_and_static_references_only"


def validate_world(world: Any) -> ValidationReport:
    """Validate structure before traversing references; PASS is not a solvability proof."""
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    issues = [
        Issue(code="SCHEMA_INVALID", path=error.json_path, message=error.message)
        for error in sorted(validator.iter_errors(world), key=lambda error: error.json_path)
    ]
    if issues:
        return ValidationReport(status="FAIL_SCHEMA", issues=issues)

    def issue(code: str, path: str, message: str) -> None:
        issues.append(Issue(code=code, path=path, message=message))

    ids = {category: {entry["id"] for entry in world[category]} for category in CATEGORIES}
    counts = Counter(entry["id"] for category in CATEGORIES for entry in world[category])
    for entity_id, count in sorted(counts.items()):
        if count > 1:
            issue("DUPLICATE_ID", "$", f"Entity ID {entity_id!r} appears {count} times")

    def ref(value: str, allowed: set[str], path: str) -> None:
        if value not in allowed:
            issue("MISSING_REFERENCE", path, f"Unknown reference {value!r}")

    if world["start_location"] not in ids["locations"]:
        issue("INVALID_START_LOCATION", "$.start_location", "Start location does not exist")
    manifest: dict[str, str] = {}
    for i, asset in enumerate(world["asset_manifest"]):
        if asset["asset_id"] in manifest:
            issue("DUPLICATE_ASSET", f"$.asset_manifest[{i}]", "Asset ID is repeated")
        manifest[asset["asset_id"]] = asset["kind"]

    for category, kind, location_field in (
        ("locations", "location", None),
        ("characters", "npc", "start_location"),
        ("items", "prop", "initial_location"),
    ):
        for i, entity in enumerate(world[category]):
            path = f"$.{category}[{i}]"
            prefab = entity["prefab_id"]
            if prefab not in manifest:
                issue("MISSING_PREFAB", path + ".prefab_id", f"Undeclared prefab {prefab!r}")
            elif manifest[prefab] != kind:
                issue("PREFAB_KIND_MISMATCH", path + ".prefab_id", f"Expected {kind} asset")
            if location_field:
                ref(entity[location_field], ids["locations"], path + "." + location_field)

    doors = {door["id"]: door for door in world["doors"]}
    for i, location in enumerate(world["locations"]):
        for j, edge in enumerate(location["exits"]):
            path = f"$.locations[{i}].exits[{j}]"
            ref(edge["to_location_id"], ids["locations"], path + ".to_location_id")
            if edge["door_id"] is not None:
                ref(edge["door_id"], ids["doors"], path + ".door_id")
                door = doors.get(edge["door_id"])
                if door and {location["id"], edge["to_location_id"]} != {
                    door["location_a"],
                    door["location_b"],
                }:
                    issue("DOOR_ENDPOINT_MISMATCH", path, "Door does not connect this exit")
    for i, door in enumerate(world["doors"]):
        for field in ("location_a", "location_b"):
            ref(door[field], ids["locations"], f"$.doors[{i}].{field}")
    for i, character in enumerate(world["characters"]):
        for field in ("initial_known_fact_ids", "secret_fact_ids"):
            for j, fact in enumerate(character[field]):
                ref(fact, ids["facts"], f"$.characters[{i}].{field}[{j}]")
    for i, fact in enumerate(world["truth"]["secret_fact_ids"]):
        ref(fact, ids["facts"], f"$.truth.secret_fact_ids[{i}]")

    flags = {
        effect["ref"]
        for action in world["actions"]
        for effect in action["effects"]
        if effect["type"] == "set_flag"
    }
    predicates = {
        "has_item": ids["items"],
        "knows_fact": ids["facts"],
        "at_location": ids["locations"],
        "door_unlocked": ids["doors"],
        "flag_true": flags,
    }
    effects = {
        "take_item": ids["items"],
        "learn_fact": ids["facts"],
        "unlock_door": ids["doors"],
        "trigger_ending": ids["endings"],
        "set_flag": flags,
    }
    targets = ids["locations"] | ids["doors"] | ids["characters"] | ids["items"]
    items = {item["id"]: item for item in world["items"]}
    for i, action in enumerate(world["actions"]):
        path = f"$.actions[{i}]"
        ref(action["location_id"], ids["locations"], path + ".location_id")
        ref(action["target_id"], targets, path + ".target_id")
        for field, allowed in (("preconditions", predicates), ("effects", effects)):
            for j, operation in enumerate(action[field]):
                ref(operation["ref"], allowed[operation["type"]], f"{path}.{field}[{j}].ref")
        if action["verb"] == "take":
            item = items.get(action["target_id"])
            matching_effect = {"type": "take_item", "ref": action["target_id"]}
            if (
                not item
                or not item["portable"]
                or item["initial_location"] != action["location_id"]
                or matching_effect not in action["effects"]
            ):
                issue("INVALID_TAKE", path, "Take requires a co-located portable item and effect")
    triggered = {
        effect["ref"]
        for action in world["actions"]
        for effect in action["effects"]
        if effect["type"] == "trigger_ending"
    }
    for i, ending in enumerate(world["endings"]):
        for j, predicate in enumerate(ending["requires"]):
            ref(predicate["ref"], predicates[predicate["type"]], f"$.endings[{i}].requires[{j}]")
        if ending["id"] not in triggered:
            issue("ENDING_NOT_TRIGGERED", f"$.endings[{i}]", "No action triggers this ending")
    return ValidationReport(status="FAIL_SEMANTIC" if issues else "PASS", issues=issues)
