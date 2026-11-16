# 12 — Reference Mystery: Blackwater Harbor

## Why a reference world is essential
Before using AI to generate hundreds of games, build **one fully playable hand-designed game** with well-defined truth, entities, clues, actions and endings. Use it as a golden fixture across compiler, game builder, reducer, save/load, character rules, and automated testing. The canonical data fixture is `examples/blackwater_harbor.json`.

## Creative brief
**Title:** Blackwater Harbor — The Keeper's Light
**Genre:** Original atmospheric coastal mystery (non-supernatural). **Estimated play:** 10–20 minutes. **Period:** An invented fictional 1920s-inspired setting; don't rely on historically exact electronics or locations without explicit research.
**Premise:** Twenty years after a lighthouse keeper's disappearance, the lighthouse shines again. A detective follows recent evidence hidden among old stories.

## Hidden truth (AUTHOR ONLY)
The keeper deliberately vanished after discovering a smuggling operation. He survived under an assumed identity and has recently returned to collect a concealed ledger. Innkeeper Elena once helped him hide and now worries that telling the truth will endanger others. A recent power cable and shipping records establish that the lighthouse was used after the reported disappearance. The old journal establishes that the keeper planned an escape rather than being murdered. A proper resolution requires gathering evidence, understanding Elena's role, and deciding whether to reveal the truth publicly. The MVP fixture simplifies motives and represents one supported truth ending plus one unresolved exit ending.

## Location map
```
                  [Tavern / Elena]
                       |
[Archive / records] -- [Harbor / Marcus] -- [Lighthouse exterior]
                                               |
                                          [locked door]
                                               |
                                          [Lighthouse interior]
```
Critical paths must remain physically traversable. The key is accessible in the tavern; cable is visible outside before the locked door; journal is inside. Manifest lies at harbor. Archive provides optional backstory.

## Main characters
- **Player / Detective:** starts harbor; records evidence, asks questions, can leave unresolved.
- **Elena / Innkeeper:** holds secret knowledge, avoids revealing it without manifest, cable evidence and journal.
- **Marcus / Dockhand:** knows about unusual shipping activity, can contextualize manifest.
- **Ada / Archivist:** provides historical context about disappearance; optional lead to archive records.

## Clue matrix
| ID | Location | How learned | Gameplay effect |
|---|---|---|---|
| `fact_manifest_after_disappearance` | Harbor | Inspect shipping manifest | Evidence of departure after presumed disappearance |
| `fact_recent_maintenance` | Lighthouse exterior | Inspect new power cable | Evidence of recent lighthouse use |
| `fact_keeper_planned_escape` | Lighthouse interior | Read keeper journal | Evidence of deliberate disappearance |
| `fact_elena_helped` | Tavern | Present all three main clues to Elena | Confrontation flag and revelation |

## Critical path to truth ending
1. Harbor: inspect manifest -> learn late departure fact.
2. Travel to lighthouse exterior: inspect cable -> learn maintenance fact.
3. Tavern: take key with legal pickup action.
4. Exterior: unlock door with key, enter interior; read journal -> learn escape fact.
5. Tavern: present evidence to Elena -> set confrontation flag and learn her contradiction.
6. Taverns: trigger truth ending if required facts and flag are present.
Alternative: return harbor and choose to leave -> unresolved ending. This choice is intentionally reachable without solving the mystery, not an accidental soft-lock.

## Example authored dialogue (fallback, concise)
**Before evidence:** Elena: “The lighthouse has been abandoned for years. I can't help you.”
**After power cable only:** Elena: “A new cable? I wouldn't know who put it there.”
**After all three clues and confrontation:** Elena: “I helped him leave. He was afraid someone would hurt him. He returned to retrieve a ledger.”
**Ending:** Narration summarizes actual collected evidence and Elena's admitted involvement. If player leaves early, ending explicitly states mystery unresolved.

## MVP 3D scene requirements
- Harbor: open dock, a notice board, accessible manifest, Marcus.
- Tavern: accessible key, Elena, warm interior, talk interaction point.
- Lighthouse exterior: locked door, visible new cable.
- Lighthouse interior: keeper journal and atmospheric reveal shot.
- Archive: optional historical note and Ada.
Assets may use placeholder meshes before art replacement. Clue readability and navigation outrank graphics quality during first milestones.

## Test scenarios
- Happy path as above reaches truth ending.
- Early exit reaches unresolved ending.
- Attempt entering interior without key fails without modifying state.
- NPC cannot reveal keeper's identity before confrontation.
- Inspect same manifest twice produces no duplicate inventory/fact bug.
- Save after opening door -> reload retains open door and evidence.
- Forged command with wrong state version rejects without mutation.
- Remove key from fixture -> graph checker rejects or reports truth ending unreachable.
- Move journal to locked room without obtainable key -> checker rejects.
- Disable model server -> script fallback still completes both endings.

## Deliberate narrative scope
This fixture is an **instructional prototype** rather than a finished mystery screenplay. Before public release, revise pacing, clues, character motivations and art direction through writing and human playtesting. The data fixture is kept minimal for schema tests; story content and dialogue can expand without weakening invariants.


---
