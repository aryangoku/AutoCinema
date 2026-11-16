"""Run from the repository root: python tools/validate_world.py WORLD.json."""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.validator.world import Issue, ValidationReport, validate_world  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("world", type=Path)
    args = parser.parse_args()
    try:
        world = json.loads(args.world.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError) as exc:
        report = ValidationReport(
            status="FAIL_INPUT",
            issues=[Issue(code="INVALID_INPUT", path="$", message=str(exc))],
        )
    else:
        report = validate_world(world)
    print(report.model_dump_json(indent=2))
    return 0 if report.status == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
