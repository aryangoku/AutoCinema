# 02 — System Architecture and Engineering Decisions

## Architecture decision record (ADR)
| Decision | Choice | Why / when to revisit |
|---|---|---|
| ADR-001 | Godot 4.7 GDScript, first-person 3D | Mature scene runtime, accessible toolchain. Pin exact patch at project bootstrap; revisit only with real performance evidence. |
| ADR-002 | Python 3.12+ FastAPI generation worker | Strong AI/data ecosystem and typed schemas. Avoid coupling gameplay to Python availability. |
| ADR-003 | Offline-capable game runtime | A compiled game should remain playable without model calls. Optional NPC dialogue enhances but cannot block completion. |
| ADR-004 | World IR is versioned JSON | Independent compiler, validator, builder and replay; safe inspectability. |
| ADR-005 | One authoritative Reality Engine | All state mutations via typed commands and deterministic reducer. Never through LLM text or scene script direct writes. |
| ADR-006 | SQLite MVP (WAL) | Simple local persistence; upgrade only when multi-user/cloud needs appear. |
| ADR-007 | Source-of-truth vs view | Python Reality Engine runs in a packaged localhost sidecar and owns state/SQLite saves; Godot renders a read-only projection and submits typed commands. Avoid dual authority. |
| ADR-008 | Modular curated asset catalog | Quality and predictable compilation; generative asset pipelines can be plugged in later after validation. |
| ADR-009 | Internal narrative DSL | Avoid mandatory ink runtime coupling. Optional import/export adapter for ink scripts later; it is not the game's canonical truth. |
| ADR-010 | Deterministic rules first, model dialogue optional | Replay, testability, budgets, safety, offline play. |

## Top-level boundaries
```
[Creator UI / Premise input]
       | REST / JSON
[FastAPI orchestrator]
       | -> [LLM adapter + cached outputs]
       | -> [StoryWorldCompiler: premise -> draft -> WorldIR]
       | -> [Validator + Graph/Solvability checker]
       | -> [Build manifest / asset IDs]
       v
[Compiled world package: validated WorldIR + asset manifest + test report]
       | file import / local IPC
[Godot World Builder] -> places modular scenes -> navmesh + interactables
       v
[Godot Runtime] -> authenticated localhost IPC -> [Python Reality Engine Sidecar]
       | Player commands -> Reality Engine -> events -> canonical state
       |        |             |            |
       |   rule validator     |        save/snapshot store
       |        +-------------+--------> NPC belief projections
       |                                  dialogue rules / optional LLM
       |                                 cinematic director
       +-------------------------------- journal / UI / analytics
```

## Runtime separation
- **Compiler/authoring time:** model generation, graph checking, asset plan creation, expensive repairs; no persistent play session mutation.
- **Runtime:** packaged Python sidecar owns authoritative state (inventory, entities, locations, quest flags, known facts, time), commands/events and persistence; Godot owns only rendered location, movement/UI presentation and submits typed actions. Runtime cannot silently recompile the world.
- **Persistence:** serializes snapshots plus event tail, world version and RNG state. If compiled blueprint changes, explicit versioned migration or mark saves incompatible.

## Monorepo structure (target)
```
autocinema/
  README.md  .env.example  .gitignore  pyproject.toml  Makefile
  docs/  schemas/  examples/  prompts/
  backend/
    app/main.py  api/  models/  compiler/  validator/
    llm/adapters/  assets/  experiments/  storage/
    tests/unit/ tests/integration/ tests/golden/
  game/
    project.godot
    addons/  scenes/{app,world,player,npc,ui,props}/
    scripts/{runtime,world_builder,characters,cinematics,ui}/
    assets/{environments,characters,props,materials,audio}/
    tests/
  tools/{validate_world.py,benchmark.py,package_world.py}
  generated/   # gitignored; produced artifacts
  .github/workflows/
```

## Golden architectural invariants
1. One world object has exactly one stable entity ID; no missing or duplicate IDs.
2. An object's location is either a world location/container **or** a single inventory, not both.
3. An action cannot commit unless its preconditions pass and all effects can apply atomically.
4. Player knowledge and NPC knowledge are independent from canonical truth; characters can hold false beliefs.
5. Endings arise only from explicit, evaluated ending conditions.
6. Dialogue can never create inventory, facts, relationships, or events unless it requests a vetted game action and receives approval.
7. All nontrivial random decisions use a saved seeded RNG source; no ambient untracked randomness in authoritative reducers.
8. Generated asset paths are restricted to a preapproved catalog; arbitrary paths, scripts and network URLs cannot execute.
9. Players can complete the game with deterministic fallback dialogue if optional model service fails.
10. Test systems execute the same rules/reducer as runtime; avoid a separate, inconsistent interpretation of actions.

## State and event ownership
Python sidecar receives `WorldIR`. On `new_game` it constructs `GameState`, validates invariants, and uses a `GameEngine.dispatch(Command) -> Result` method. Within one dispatch: validate caller, validate preconditions, compute effects against an isolated draft, assert invariants, commit state and append event(s), increment version, emit UI/render events. On failure no state change and descriptive error.

## Cross-service protocol
- **Build service:** REST request/response for creating world packages; optional WebSocket/SSE for progress; typed JSON, correlation IDs, idempotency keys for repeat requests.
- **Game runtime:** bundled local Python sidecar + compiled JSON/asset manifest; no Internet or AI provider required after package publication. Launcher starts/stops sidecar and passes a random per-session local authentication token to Godot.
- **Dialogue:** optionally POST allowed context + desired `speech_act` to local service; service returns candidate utterance only. Timeout -> authored fallback; sanitize text before rendering.
- **State replay:** event log includes seq ID, typed action, arguments, effect delta, simulation timestamp, RNG state checksum, and post-state hash.

## Threat/failure scenarios
- Prompt produces an unknown resource ID -> compiler validation rejects.
- Missing scene prefab -> build fails with actionable mapping report.
- Player uses key twice -> first transaction consumes/moves item; second fails precondition; no duplicate.
- Character wants to reveal unlearned secret -> dialogue context filter omits secret; rule-based response selected; output validator rejects leaked fact.
- Save crashes mid-write -> SQLite transaction and last verified snapshot+events restore.
- AI provider outage -> compile operation stops with recoverable error; precompiled sample remains playable.

## Performance strategy
Author on small worlds, instrument with a profiler, then optimize. Use asset reuse, scene instancing, occlusion/LOD where appropriate, asynchronous builds, bounded dialogue context, on-demand NPC planning, cached snapshots. Never embed API keys in exported game binaries.

## Build vs buy
Build Story IR, Reality Engine, semantic validator, proof-of-solvability, knowledge projections, and artifact assembly — these are the product's IP. Reuse Godot for graphics/navigation, FastAPI/Pydantic for APIs, a maintained test runner, and an approved asset library.

## Offline distribution / sidecar deployment
For MVP, package a Python runtime service (e.g. with a pinned tested freezing tool) **together with** Godot. The desktop launcher starts the sidecar on loopback, negotiates an ephemeral port + high-entropy per-session token, starts Godot, and stops sidecar on exit. Keep command and event state in Python, not replicated as authoritative GDScript dictionaries. Cache visual projections client-side with explicit `state_version`; refresh on version conflicts. The Python service is local software and does not require Internet to play an already-generated world. Budget for packaging and process-supervision tests; a standalone `.exe` Godot export alone is not the complete product.


---
