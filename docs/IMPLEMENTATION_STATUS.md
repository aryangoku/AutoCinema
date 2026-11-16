# Implementation status - Milestone 1

AutoCinema now includes an offline console playthrough of Blackwater Harbor, backed
by one deterministic Python Reality Engine. Godot remains a menu pending Milestone 2.

## Delivered

- AC-010: strict GameState, Command, Event, Result, item-holder and NPC-belief contracts;
  pure reducer and canonical state hashing.
- AC-011: TAKE, INSPECT/read, UNLOCK, TALK, PRESENT_EVIDENCE, TRAVEL and START_ENDING.
  Both canonical endings are reachable through the authoritative command dispatcher.
- AC-012: one owner per item, presence checks, evidence and ending gates, exact retry
  idempotency, changed-payload ID rejection, optimistic versions and final endings.
- AC-013: 53 focused engine/console tests, including randomized command sequences, failed-effect
  rollback, concurrent connections and injected SQLite commit failure.
- AC-014: SQLite WAL transactions, snapshots plus event tails, world-build compatibility,
  corruption rejection, exact save/resume hashes and full deterministic replay.

Milestone 0 contracts, validator, 50 earlier tests, CI configuration and Godot menu
are preserved. Schema versions remain 1.0.0; application version is now 0.2.0.

## Verification

- `python tools/dev.py check`: 101 tests passed, Ruff lint/format passed, mypy
  passed (14 source files), canonical fixture passed.
- Two subsequent console integration tests passed (save/resume and missing-save errors).
  Total: 103 tests verified. The initial 51-test engine suite also passed independently.
- Secrets scan passed with the new engine files tracked.
- `python tools/dev.py demo`: both ending routes passed, including checkpoint/close/reopen
  and full replay comparison. Truth route used 15 accepted commands; unresolved used one.
- `python tools/dev.py godot-test`: headless import and menu/dialog smoke test passed on
  Godot 4.7.2.stable.official.ed1daf0bf.
- An initial combined run was interrupted when Windows sandbox networking blocked
  asyncio socket-pair setup in the existing health test. After network permission
  was granted, the full check completed successfully.
- Local environment: Windows and Python 3.13.1. Hosted CI has not been run.

## Play

Double-click `Play AutoCinema.cmd` on Windows, or run
`.venv/Scripts/python.exe tools/dev.py play` from the repository root.
The console prints the session ID needed to resume with `tools/play_console.py --session ID`.
Every accepted command is committed; `s` writes a checkpoint and `q` saves and exits.

## Limits

No 3D movement or scene assembly yet. No model generation, cloud service, voice, physical
interaction-range checks, save-slot rewind or Godot sidecar integration. Dialogue is
an authored offline fallback; NPC knowledge-filtered generative dialogue is later work.
The two authored routes are verified; this is not exhaustive solvability verification
of arbitrary generated worlds. Checksums detect corruption, not malicious local rewriting.

Next smallest ticket: AC-020, first-person Godot movement, interaction ray/prompts,
inventory, journal and subtitles, connected to this authoritative engine.
