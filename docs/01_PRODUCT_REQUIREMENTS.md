# 01 — Product Requirements Document (PRD)

## 1. Product vision
**AutoCinema** converts a short, original story premise into an **actual playable cinematic mystery**. The product promise is: *Give me a premise; let me explore, investigate, talk, make consequential decisions, and finish a coherent story.* It is not a general text-adventure chatbot, movie generator, or unlimited photorealistic world model.

### North-star measure
**Verified playable-story completion rate:** Of generated games accepted for publication, percentage that human testers can start, progress through, and finish without blocking logic/technical faults. Track model checker pass and human playtest pass separately.

### Supporting measures
- World generation success after bounded repair attempts; schema and semantic validation rates.
- Playtest-reachable endings vs advertised endings; rate of unsolvable puzzles / soft-locks.
- Contradictions per 100 character dialogue turns (manually annotated and automated flags).
- Median time to first playable version, generation cost, failed generation recovery time.
- Average human playthrough completion, interaction responsiveness, crash-free sessions.
- User satisfaction and creator edit-to-play iteration count.

## 2. Target users
1. **Solo creators:** nonprogrammers prototyping short narrative games.
2. **Indie game designers:** exploring branching mystery structures before writing full scenes.
3. **Educators:** using original interactive scenarios in lessons, with factual content clearly distinguished from fictional game worlds (later).
4. **Players:** exploring community-created mysteries (post-MVP).

## 3. Primary user journey
1. User opens AutoCinema, chooses **Create Mystery**, enters an original story premise (max ~1,200 characters MVP).
2. User selects a bounded style: coastal mystery / manor mystery / small-town mystery; tone: cozy / suspenseful; estimated length: 10/15/20 minutes.
3. Product shows outline draft: setting, central truth, characters, locations, clue graph, endings. User can inspect and regenerate outline BEFORE compiling.
4. Compiler validates references, secrets, routes, prerequisites, and endings. If invalid, show error or repair within a strict budget.
5. World Builder selects modular licensed assets, assembles scenes, and bakes navmesh/offline data as needed.
6. Automated playtester proves at least one legal path to each intended ending in bounded abstract state space; 3D navigation smoke tests verify critical travel paths.
7. User enters 3D game, uses WASD/mouse, interacts with objects/NPCs, collects evidence, sees journal/objectives, and finishes an ending.
8. User can save/load and replay another branch. Creator can inspect the generation report and edit supported settings.

## 4. Core capabilities / priority
| ID | Feature | Priority | MVP acceptance |
|---|---|---|---|
| PR-01 | Original premise to structured story | P0 | Output conforms to versioned IR and semantic checks |
| PR-02 | Coherent mystery truth and clue graph | P0 | One established truth and reachable reveal paths |
| PR-03 | Modular 3D world | P0 | 3–5 connected and traversable locations |
| PR-04 | Player movement and interaction | P0 | Walk, look, inspect, use, talk, collect; keyboard/mouse |
| PR-05 | Authoritative world state | P0 | Commands validated and effects event-logged |
| PR-06 | Inventory, puzzle rules, journal | P0 | Items unique, clues discoverable, objectives update |
| PR-07 | Character knowledge and dialogue | P0 | Knowledge gating + deterministic fallback dialogue |
| PR-08 | Cinematic moments | P1 | Entry, clue reveal, confrontation, ending; skip supported |
| PR-09 | Automated solvability | P0 | Checker finds paths to supported endings or rejects build |
| PR-10 | Save/load + crash recovery | P0 | Restore identical canonical state from save |
| PR-11 | Generation error diagnostics | P0 | No silently published invalid game |
| PR-12 | User editing | P1 | Adjust characters, locations and clues via validated forms |
| PR-13 | Adaptive voice acting | P2 | Not needed for MVP; use text + licensed stock audio |
| PR-14 | Shared worlds & marketplace | P2 | Not needed for MVP |
| PR-15 | Live story mutation mid-session | P2 | Defer; hard for consistency |

## 5. Product UX screens
- **Home:** New Mystery, Load Game, Example Mystery, Settings.
- **Premise Editor:** genre template, tone, max characters, content/rights reminder; estimated generation steps and constraints.
- **Story Blueprint Review:** outline, secrets, NPCs, clue dependencies, ending choices, regenerate one section, accept/compile.
- **Build Inspector:** stage progress (draft/validate/plan/place/test/package); issue table, repair explanations.
- **Game Screen:** third-person or first-person camera (choose first-person MVP), interact reticle, inventory, journal, subtitles, skip prompt.
- **Creator Debug Overlay:** event timeline, entity inspector, fact/knowledge inspector, graph of quest states, test report.
- **Post-game:** outcome, evidence timeline, alternate ending availability; no unfounded claim that other endings are verified unless checker says so.

## 6. Accessibility and inclusivity
- Full subtitles and scalable text; UI focus indication and contrast; remappable keys.
- Offer reduced camera motion, reduced flashes, adjustable mouse sensitivity, disable screen shake.
- Critical clues conveyed by text/interaction, not solely color or audio.
- Avoid mandatory QTEs and inaccessible precision timing in MVP.
- Localize UI with externalized strings; localized generated games later.

## 7. Deliberate non-goals at launch
Photorealistic generative 3D; unlimited genres and story duration; infinite NPC memory; open-world freeform manipulation; perfect natural-language actions; automatically trained voice actors; multiplayer; full autonomous NPC schedules; user-uploaded executable mods; cloud marketplace; self-verified narrative quality.

## 8. Success gates
**MVP exit:** 20 internally generated premises tested; at least 18 compile into complete playable games after <=2 bounded repair iterations; all accepted games pass schema and deterministic semantic checks; 0 known P0 soft-locks; manual test of 10 games each played from start to conclusion; save/load 100-cycle test; critical interactions meet latency target in `11_SECURITY_PERFORMANCE_RELEASE.md`. These are proposed acceptance targets, not proven capability. Benchmark across distinct templates and random seeds.

## 9. Major risks and mitigation
- **Unbounded generation:** use narrow genre, asset catalog, budgets, deterministic templates.
- **Beautiful but unplayable:** verify abstract action graph and scene navmesh independently.
- **NPC contradictions:** store structured beliefs and expose only permitted context.
- **Asset mismatch:** compiler chooses existing asset IDs; fail closed for missing mapping.
- **High LLM costs:** draft in stages, cache per content hash, only regenerate affected stage.
- **Long waits:** show step-level progress and a deterministic example story while offline.
- **Story IP/content:** require original or authorized premises; no automatic recreation of protected franchise worlds/characters.

## 10. Product guardrails
An offline preview/demo must be available. Explain when generated dialogue is AI-authored. Preserve player agency; don't pretend to support unconstrained actions that the engine can't execute. Treat all numerical performance and quality goals as design targets until measured.


---
