"""Play Blackwater Harbor offline, or run a verified demonstration route."""

import argparse
import json
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.engine.demo import TRUTH_ROUTE, UNRESOLVED_ROUTE, issue  # noqa: E402
from backend.engine.service import GameEngine, SaveError  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", type=Path, default=ROOT / "generated/blackwater.sqlite3")
    parser.add_argument("--session", help="Resume this saved session; omit to create a new one")
    parser.add_argument("--demo", choices=["truth", "unresolved"])
    args = parser.parse_args()
    world = json.loads((ROOT / "examples/blackwater_harbor.json").read_text(encoding="utf-8"))
    if args.session and args.demo:
        parser.error("Demo routes start a new session; use --session for interactive resume")
    args.database.parent.mkdir(parents=True, exist_ok=True)
    engine = (
        GameEngine.load(world, args.database, args.session)
        if args.session
        else GameEngine(world, args.database)
    )
    try:
        print("AutoCinema | Blackwater Harbor | offline console prototype")
        print(f"Session: {engine.session_id}")
        print(f"Save database: {args.database}")
        if args.demo:
            route = TRUTH_ROUTE if args.demo == "truth" else UNRESOLVED_ROUTE
            for index, (action, target) in enumerate(route):
                result = issue(engine, action, target)
                print(f"{index + 1:02d}. {action}: {result.code}")
                if not result.accepted:
                    return 1
                # Exercise a checkpoint followed by a real close/reopen mid-playthrough.
                if index == len(route) // 2:
                    saved_hash = engine.save()
                    session_id = engine.session_id
                    engine.close()
                    engine = GameEngine.load(world, args.database, session_id)
                    if engine.state.checksum() != saved_hash:
                        raise SaveError("Save/load state hash mismatch")
                    print("    Checkpoint reopened: identical state hash")
            expected = "ending_truth" if args.demo == "truth" else "ending_unresolved"
            replay = engine.replay()
            if replay != engine.state or replay.ending_id != expected:
                raise SaveError("Ending or replay verification failed")
            print(f"PASS: {replay.ending_id}; replay matches; state hash {replay.checksum()}")
            return 0
        while True:
            view = engine.player_view()
            print(f"\n{view['location']['name']} — {view['location']['description']}")
            print("Inventory:", ", ".join(view["inventory"]) or "empty")
            for fact in view["known_facts"]:
                print("Evidence:", fact["text"])
            if view["ending_id"]:
                ending = next(e for e in world["endings"] if e["id"] == view["ending_id"])
                print(f"\n{ending['name']}\n{ending['summary']}")
                break
            options = engine.available_commands()
            for index, option in enumerate(options, 1):
                print(f"  {index}. {option['label']}")
            choice = input("Choose a number, [s] checkpoint, [q] save and quit: ").strip().lower()
            if choice in ("s", "q"):
                engine.save()
                print(f"Saved. Resume with --session {engine.session_id}")
                if choice == "q":
                    break
            elif choice.isdigit() and 1 <= int(choice) <= len(options):
                selected = options[int(choice) - 1]
                result = issue(engine, selected["action_id"], selected["target_id"])
                print(result.dialogue or result.code)
            else:
                print("Choose one of the listed options.")
        return 0
    finally:
        engine.close()


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (SaveError, sqlite3.Error, ValueError) as exc:
        print(f"Could not load or update the game: {exc}", file=sys.stderr)
        raise SystemExit(2) from None
    except (EOFError, KeyboardInterrupt):
        print("\nClosed. Accepted actions are already saved.")
        raise SystemExit(0) from None
