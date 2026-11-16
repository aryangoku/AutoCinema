# 11 — Security, Reliability, Costs, Performance and Release

## Threat model
Attack surfaces: creator-entered prompts; imported narrative/asset metadata; generated JSON; third-party asset packages; provider responses; save files; optional local API endpoint; game mods/extensions; community uploads (later).

## Non-negotiable security boundaries
- User story text and LLM output are **data**, never trusted system instructions or executable code.
- No arbitrary `exec`, `eval`, shell command, GDScript injection, SQL query synthesis, or path traversal from model-generated output.
- Only a typed DSL can request state changes; validate caller identity, references, preconditions and effect permissions.
- Godot loads only approved asset IDs via controlled registry; no arbitrary URLs or filesystem paths in generated IR.
- Model/API keys stored on backend in environment/user OS credential store; never bundled into game project, saved game, or logs.
- Backend development server bound to `127.0.0.1` by default. If remote deployment later, add auth, TLS, rate limits, per-user isolation and abuse controls.
- Validate uploaded file type, size and content in a sandbox. Do not import arbitrary Blender scripts or executables.
- Use parameterized SQL, isolated temporary directories, resource limits, and signed/checksummed world packages.
- Treat all model outputs as untrusted, even if schema-shaped. Structured outputs constrain form, not truth or authority.
- Model-powered dialogue needs output escaping, secret reference checks, refusal handling, rate limits, and safe fallback.
- Generate original content or use authorized sources; warn about copyrighted franchises and forbidden unlicensed assets.

## Privacy and policy
For local MVP, keep game saves and creator prompts local by default; explain when a prompt is sent to an external model. Include clear model-provider disclosure and no-telemetry default. If analytics later, opt-in and aggregate data; publish retention and deletion policies. Do not collect user emails/accounts for V1. Handle youth-facing releases and age ratings as separate future work.

## Performance budgets (initial targets, measure empirically)
- 1080p stylized world: median 60 FPS on named mid-range test machine, >=30 FPS on low preset when possible.
- Interact command -> state response (offline): <50ms p95 excluding animations; track actual.
- Opening inventory/journal: perceived immediate; no blocking model calls.
- Optional dialogue LLM: first response target <5s p95 under service availability, but always show fallback if deadline reached.
- Load compiled world: target <10s on benchmark machine with warm caches; monitor asset sizes.
- Generation: target <3min median for limited story under normal provider availability, but show progress and honest uncertainty. Not a guarantee.
- World package size, GPU memory and draw calls tracked in performance report; set hard build warnings after baseline measurements.
- Abstract verifier: bounded by max states/depth/time and returns UNKNOWN if exceeded.

## Costs / model routing
Token/cost depends on provider and prompt size, so **do not claim a universal per-game cost**. Instrument each stage's input/output tokens, retries, model name, cache hits and estimated cost using configurable rate card. Use smaller models for structure extraction and editing when validated; larger models only for hard synthesis. Turn optional LLM dialogue off by default in the reproducible benchmark. Enforce max model calls per job and manual retry beyond budget.

## Reliability
- Every build has idempotency key and stage state machine; can resume safe deterministic stages.
- Provider failures produce explicit `RETRYABLE` / `NON_RETRYABLE` codes.
- Save with atomic transactions and regular snapshots; verify hash on load.
- Asset missing: fail closed / use approved fallback prefab with visible warning.
- LLM dialogue failure: continue game using authored lines.
- World checker timeout: UNKNOWN, never PASS.
- Telemetry for game generation optional, but local structured logs with redacted sensitive content always available for debugging.

## CI / release process
- Use Python formatter/linter/type checker (`ruff`, `mypy` where useful), `pytest`, schema fixture validation, golden reducer tests.
- Godot headless import/check using exact pinned executable; GdUnit4 optional with version compatibility checked.
- CI runs malware/secret scan, dependency vulnerability audit, asset catalog validation, license inventory.
- Package Windows build from pinned export preset, include attributable licensing, signed manifest checksums, changelog and known limitations.
- Releases have reproducible version tag and test report; avoid automatically shipping generated game files that failed validation.

## Minimum documentation for contributors
Setup (OS, Python version, Godot patch), environment variables (`MODEL_PROVIDER`, `MODEL_API_KEY` server only, `AUTO_CINEMA_DB_URL`, `LOG_LEVEL`), offline sample instructions, test commands, license policy, seed/replay procedure, how to report deterministic bugs, asset catalog extension workflow.

## Suggested dev commands (define scripts in Milestone 0)
```
python -m venv .venv
# activate environment using your OS shell
pip install -e '.[dev]'
python tools/validate_world.py examples/blackwater_harbor.json
pytest -q
ruff check .
godot --headless --path game --editor --quit
# Godot test runner after installing a compatible version; command pinned in Makefile
```
Don't represent the above as already-working commands: the actual repo scaffolding, dependencies and `tools/validate_world.py` will be implemented in Milestone 0.

## Release checklist
[ ] Golden mystery playable entirely offline; [ ] all endings verified within stated bounds; [ ] save/load stable; [ ] input rebinding/subtitles; [ ] no missing/mislicensed assets; [ ] scripts/LLM outputs cannot mutate state except through typed actions; [ ] no keys in binaries; [ ] crash/recovery tests; [ ] measured FPS and model costs; [ ] beta tester feedback; [ ] privacy and attribution docs; [ ] reproducible Windows export.


---
