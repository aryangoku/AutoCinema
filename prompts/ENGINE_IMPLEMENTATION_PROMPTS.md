# Incremental AI Coding Prompts — Use After Master Prompt

These prompts are designed to be sent one by one after the agent has access to the full spec. Ask for tests and a runnable/demo result after each task.

## Prompt A — Reality Engine
> Implement Milestone 1 as specified in `docs/05_REALITY_ENGINE.md` using the validated `examples/blackwater_harbor.json`. Define typed commands, preconditions/effects, state transitions, idempotency, state version checks, events and save/load. Build a command-line reference playthrough to both endings. Write tests for no item duplication, forbidden actions, knowledge gating, event replay, and save/load hash equality. No LLM calls or Godot dependencies in the core reducer. Report real test output.

## Prompt B — Godot world builder
> Implement a Godot vertical slice using placeholder primitives and the approved asset ID registry. Instantiate harbor, tavern, lighthouse grounds/interior, and archive. Provide first-person movement, interact ray, highlight, inspect/take, locked door, journal, NPC interaction UI. All player interactions must call the Reality Engine; don't create duplicate mutable game-state stores. Write headless and manual test scripts including reachability of critical objects.

## Prompt C — Story compiler
> Build the deterministic compiler first: template -> WorldIR -> JSON Schema validation -> semantic validation -> asset plan -> abstract playtest -> immutable package. Implement precise errors for unknown IDs, unsolvable endings, missing prefabs and clue cycles. Generate five variations and prove at least one witness path to each intended ending in the abstract model. Do not add LLMs yet.

## Prompt D — AI generation
> Add a provider-agnostic structured output adapter with strict stage schemas, bounded retries, caching, and per-job budget. Implement story bible then plot graph then WorldIR; validate after every stage. Never permit model-generated script execution. Add evaluation fixtures and track success/failure by stage. Do not claim valid JSON implies valid gameplay.

## Prompt E — AI NPCs
> Implement NPC belief projection, secret gating and speech-act policy from `docs/06_AI_CHARACTERS.md`. First complete authored deterministic fallback dialogue, then optional model phrasing. Use allowable fact IDs and reject any proposed lines referencing forbidden or unlearned secrets. Add save/load and adversarial tests. No model output may directly mutate quest or item state.

## Prompt F — Cinematic Director
> Implement event-driven shot plans using named scene anchors. For each committed LOCATION_ENTERED, EVIDENCE_DISCOVERED, CONFRONTATION, and ENDING event, choose a validated shot template; cameras must never clip through obstacles and all cutscenes must be skippable. Add comfort settings and tests for missing anchors, interrupts and control restoration. Do not use speculative AI video generation.

## Prompt G — Automated playtesting
> Implement L0–L4 playtest checks. Reuse the authoritative predicate/effect semantics; BFS or A* on projected state with bounded budget, witness path for every ending, dead-end classification and explicit UNKNOWN on timeout. Run reference mystery and deliberately unsolvable fixture; produce machine-readable `test_report.json`. Test 3D navigation separately from abstract gameplay reachability.

## Prompt H — Pre-release quality
> Implement the `docs/11_SECURITY_PERFORMANCE_RELEASE.md` checklist. Benchmark FPS, interaction latency, world-generation latency and model calls on named hardware and provider; measure instead of inventing. Verify input remapping, subtitles, asset licensing, save/load, offline fallback, sample world and error reporting. Build signed/checksummed world package and Windows export using pinned Godot patch.

## Code review prompt (use anytime)
> Review current work strictly against AutoCinema's docs. Prioritize contradictions between runtime and model-generated state, unsolvable quests, hidden-secret leakage, missing entity references, insecure asset paths, non-determinism, model outage handling, and soft-locks. Return severity-ranked concrete defects with file/line references and reproducible failing tests. Do not redesign unrelated modules.

## UX/art critique prompt
> Review the playable 3D vertical slice for mystery atmosphere, clue readability, camera comfort, accessible subtitles, interface consistency, pacing, and visual coherence. Propose changes within the current curated asset budget. Distinguish verified usability problems from subjective preferences and do not replace core testable narrative mechanics.


---
