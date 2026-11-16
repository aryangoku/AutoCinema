# 10 — Roadmap, Epics, Detailed Backlog and Delivery Gates

## Engineering approach
Deliver playable vertical slices. The repo must always have a runnable example and green tests. Prioritize verifiable game state before artwork, and do not build multi-agent orchestration until a deterministic compiler+runtime works with hand-authored sample JSON. Do not ask an AI agent to implement every epic in a single request.

## Milestone 0 — Repository and exact contracts (week 1)
**Tickets**
- AC-001 Initialize Git mono-repo, Python project, Godot project, README, env example, formatting/lint/test tools.
- AC-002 Pin Godot 4.7 exact tested patch; Python dependency lock; license manifest policy.
- AC-003 Adopt `schemas/world.schema.json`; build Pydantic models or JSON Schema adapters with parity tests.
- AC-004 Load `examples/blackwater_harbor.json` in Python validator; test missing ID and duplicate-ID rejection.
- AC-005 CI: Python lint/types/tests; Godot headless import and scene smoke test; secrets scanner.
**Exit criteria:** `make test` passes; example validates; intentionally broken fixture fails with clear errors; game starts to menu. No AI required yet.

## Milestone 1 — Reality Engine foundation (weeks 2–3)
- AC-010 Implement `GameState`, `Command`, `Event`, `Result`, reducers, predicate/effect interpreter.
- AC-011 Implement `TAKE`, `INSPECT`, `UNLOCK`, `TALK`, `PRESENT_EVIDENCE`, `TRAVEL`, `START_ENDING` against hand-authored world.
- AC-012 Add item uniqueness, reference resolution, ending authority, idempotent command IDs, optimistic version checks.
- AC-013 Write 25+ focused tests incl. illegal command no mutation, key reuse, knowledge unlock, replay determinism.
- AC-014 Save/load snapshot+event tail in SQLite and hash comparison test.
**Exit:** Console-driven full Blackwater Harbor playthrough reaches truth ending and unresolved ending with identical results after save/load; rejected commands do not mutate.

## Milestone 2 — First playable Godot slice (weeks 4–6)
- AC-020 Build first-person movement, interact ray, prompts, inventory, journal, subtitles.
- AC-021 Handcraft harbor + tavern + lighthouse exterior/interior + archive with modular placeholders.
- AC-022 Asset registry maps fixture IDs to scene resources; fail closed for missing IDs.
- AC-023 Implement `RuntimeBridge` from Godot interaction to same canonical reducer.
- AC-024 NPC static positions, dialogue UI with authored fallback and evidence presentation.
- AC-025 Navigation + door state integration; verify critical props are reachable.
**Exit:** Entire hand-authored mystery is playable in 3D start-to-end offline, including two endings.

## Milestone 3 — Compiler baseline without LLM (weeks 7–8)
- AC-030 Build deterministic template generator from fixed mystery templates + seed.
- AC-031 Add schema validation, semantic reference checks, clue graph checker.
- AC-032 Build abstract action search for witness paths and dead-end categorization.
- AC-033 Build immutable world package and build report with asset mapping.
- AC-034 Create 5 synthetic distinct worlds by swapping names, layouts, clue placements under constraints.
**Exit:** Deterministic generation produces >=5 valid, playable template variants with test reports; unsolvable variants are rejected.

## Milestone 4 — AI Story-to-World Compiler (weeks 9–12)
- AC-040 Provider-agnostic structured generation adapter with timeouts, cache, spend budget.
- AC-041 Multi-stage story Bible -> clue graph -> world IR with controlled schemas.
- AC-042 Localized repair prompts generated from actual validation failures.
- AC-043 Creator outline preview + stage progress UI + retries/fail report.
- AC-044 Run evals on 20 original premises; capture success rates and recurring errors.
**Exit:** At least one unseen original user premise can be converted into a validated playable small mystery with no manual JSON editing. Record success and failure instead of inventing quality metrics.

## Milestone 5 — NPC dialogue and knowledge (weeks 13–14)
- AC-050 NPC belief/secret projection and speech-act policy.
- AC-051 Optional LLM dialogue adaptation; JSON response validation and evidence rules.
- AC-052 Character confrontation test suite; injection and leakage tests.
- AC-053 Fallback authored dialogue whenever provider unavailable.
**Exit:** Model cannot directly edit state; critical dialogues function offline; test suite rejects premature secret disclosures.

## Milestone 6 — Cinematic Director + polish (weeks 15–17)
- AC-060 Add reusable shot templates and named camera anchors.
- AC-061 Trigger location introductions, clue inserts and ending cutscenes from committed events.
- AC-062 Add licensed music/effects, subtitles and comfort controls.
- AC-063 Add save selection, pause, settings, creator debug panel.
**Exit:** 3 key sequences look coherent, are skippable, and always restore control; no duplicate event effects.

## Milestone 7 — Verification, QA and release (weeks 18–21+)
- AC-070 Complete L0–L4 checker; witness route replay; soft-lock fixtures.
- AC-071 Perf profiling; measured FPS, build latency and usage costs.
- AC-072 Human test 10 stories, including accessibility pass and creator usability review.
- AC-073 Package Windows build, license/attribution list, crash reporting opt-in, backup/recovery.
- AC-074 Beta test with 5–10 external users; prioritize bug reports by severity.
**Exit:** Meets PRD acceptance gates or explicitly reports which targets remain unmet. Deliver a downloadable playable demo.

## Phase 2 (after MVP; no deadlines committed)
- Editable world blueprint with round-trip validation; extra genres (horror, fantasy, educational stories).
- Story branching forks/replay UI; NPC schedules; dynamic background scenes.
- More advanced procedural scene assembly; larger location/asset catalogs.
- Optional voice with licensing and opt-in; cinematography recommendation model.
- Creator sharing/community gallery with content policy, moderation, abuse/report controls.
- Multiplayer only after deterministic authoritative networking design is tested.

## Task prioritization matrix
**P0:** schema + reducer + save/load + 3D playability + solvability. **P1:** AI compiler + dialogue + cinematic quality. **P2:** advanced procedural assets + social/distribution. Avoid shipping P1 novelty on top of broken P0 mechanics.

## Developer workflow
1. Pull one ticket; write explicit acceptance criteria and at least one failure test.
2. Implement minimal code behind existing interface; no unrelated refactors.
3. Run formatter, lint, type checking, unit tests, Godot import/test as applicable.
4. Show file changes, exact executed commands, test results and remaining limitations.
5. Commit with clear message and update decision docs for architectural changes.

## Definition of Done (for every ticket)
- Type and schema contracts honored; at least unit/integration tests as appropriate.
- No hard-coded production secrets or unlicensed assets.
- No direct state mutation outside Reality Engine.
- Useful error messages and logs; no concealed failures.
- README/run instructions updated when commands change.
- Demonstrated with an exact reproducible test or playable walkthrough.

## Solo-developer reality check
18–21+ weeks is an aggressive estimate for an experienced developer familiar with Godot, Python, procedural game pipelines and AI integration. A first-time Godot developer may need 6–12+ months part-time. Resist the urge to prioritize gorgeous graphics before proving the narrative core.


---
