# Implementation status - Milestone 0

Validated locally on 2026-11-16, Windows, Python 3.13.1 and Godot
4.7.2.stable.official.ed1daf0bf.

## Delivered

- AC-001: monorepo, Python config, Godot menu, README, env example, lint/format/test commands.
- AC-002: exact tested Godot patch, full Python dependency version lock, asset license policy.
- AC-003: canonical WorldIR JSON Schema adapter; schema parity and malformed input tests.
- AC-004: canonical Blackwater Harbor validates; missing IDs, duplicate IDs, references,
  start location, prefab declarations/kinds and other semantic failures have focused tests.
- AC-005: Python lint/types/tests and Godot headless CI jobs are configured; secrets scan
  runs on tracked files. Hosted CI execution remains pending publication/authentication.

## Commands actually executed

- `python tools/dev.py check`: PASS. Ruff lint + format, mypy (8 source files),
  pytest (50 passed), reference world PASS, secret scanner PASS.
- `python tools/dev.py godot-test`: PASS. Headless editor import, main scene load,
  control presence, reference dialog open/close.
- Godot rendered three frames of the main scene; menu screenshot visually inspected
  at 1280x720 for text, layout and clipping.

The initial test attempts found runner permissions blocking default temp/AppData
folders. Reruns used workspace TEMP/TMP and APPDATA plus Godot self-contained mode;
final runs had no Godot errors and no Python test warnings.
The scanner's single reviewed false positive was the fictional antagonist secret;
an exact file/type/content-hash allowance retains detection for changed content.
The allowance configuration itself is excluded from scanning its hash values.

## Limits

This is a menu and validation foundation, not a playable game. No movement, world
assembly, gameplay reducer, persistence, model integration or reachable-ending proof
exists yet. Manifest membership does not prove a prefab exists on disk. No third-party
art is bundled. Linux/macOS, hosted CI and desktop export packaging are unverified.

GitHub publication is blocked: GitHub CLI is signed out and a noninteractive push
probe could not obtain credentials. The initial commit is saved locally.

Next smallest ticket: AC-010 - typed GameState, Command, Event and Result, with a
pure deterministic reducer and rejected-command-no-mutation tests.
