# 08 — Automated Playtesting and Verification Engine

## Goal
Reject generated worlds that are invalid, obviously unsolvable, unwinnable under intended rules, or trivially broken. The checker supports bounded verification; it cannot prove human fun, polish, or all possible real-time 3D play sequences.

## Verification layers (all required at distinct scopes)
**L0 Schema:** validates shape, types, required fields, enums.
**L1 Semantics:** all IDs and references resolve; actions/effects and entity types match; no circular impossible clue dependencies; items have valid owners.
**L2 Abstract planning:** build game-state graph from available actions; BFS/A* finds one legal route to each intended ending. Track visited state hashes and action depths.
**L3 Soft-lock and fault checks:** explore bounded reachable states for critical dead ends and irreversible loss of required objects. Distinguish intentional failure endings from unintentional soft-locks.
**L4 Godot integration:** instantiate scene, pathfind to key NPCs/objects, interact, verify collision/navmesh/props.
**L5 Human testing:** check mystery quality, readability, fairness, dialogue credibility, accessibility, art style.

## Basic state space
For MVP compile a *projected abstract state*: location, inventory item IDs, door states, known facts, quest flags, remaining single-use actions, ending status. Exclude visual positions/animations. Actions have typed preconditions/effects from same Runtime definition. Hash canonical ordering. Apply state-invariant assertions after every successor.

## Search algorithm pseudocode
```
queue = deque([(initial_state, [])]); visited = {hash(initial_state)}
while queue and len(visited) < MAX_STATES:
    state, path = queue.popleft()
    if goal(state): return SOLUTION(path)
    if len(path) >= MAX_DEPTH: continue
    for action in enabled_actions(state):
        next_state = reducer_preview(state, action)  # same semantics as runtime
        if invalid(next_state): record_failure(...); continue
        key = hash(next_state)
        if key not in visited:
            visited.add(key)
            queue.append((next_state, path + [action]))
return UNKNOWN_IF_LIMIT_HIT_ELSE_UNREACHABLE
```
If resource limits are hit, return `UNKNOWN`, **not** `VERIFIED`. For every mandatory ending, supply a witness route and replay it in runtime. State-space explosion can be mitigated by limiting flags, partial-order reductions for independent actions, level-by-level constraints, and selective symbolic solving.

## Soft-lock taxonomy
- Key consumed on unrelated action -> required door permanently locked.
- NPC needed for ending relocates to unreachable area.
- Required item spawned inside inaccessible geometry.
- Dialogue-only clue requires an unavailable model call.
- Required info on optional route without alternate.
- Changing a flag removes all paths to endings without intentional failure conclusion.
- UI exposes choice before its prerequisites -> impossible action.
- Navmesh reports accessible while blocked by a game-state-dependent door.

## Generator repair feedback
For each problem produce:
```
{ "severity":"error", "code":"MISSING_PREREQUISITE",
  "entity_id":"act_unlock_lighthouse", "path":"actions[7].preconditions",
  "message":"item_iron_key is required but unreachable from start",
  "counterexample":"start -> tavern -> ... [dead end]",
  "repair_hint":"Move key to accessible room or add alternate unlock action" }
```
Compile a precise issue report instead of a generic “couldn't generate game”.

## Testing matrix
- **Unit Python:** schema, refs, actions, predicate interpreter, reducer, checksums, event persistence.
- **Property-based:** random action sequences maintain invariants; idempotency; invalid actions don't mutate.
- **Golden story tests:** hand-reviewed reference worlds with expected reachable endings and known unsolvable variants.
- **Contract:** compiler JSON matches Godot importer; backend API schemas stable.
- **Godot tests:** scene loads, nav reachability, interaction distance, journal and save behaviors, cutscene skip.
- **End-to-end:** create sample world -> compile -> build -> smoke play -> trigger each ending.
- **Adversarial:** malicious prompt injection, asset IDs pointing outside registry, malformed save, forged state mutation, provider outage.
- **Performance:** generation latency, FPS, asset memory, dialogue p50/p95, abstract planning states/s.

## Benchmarks (targets, not achievements)
- All shipped worlds pass schema + semantic validation.
- No automatically published world with `UNREACHABLE_REQUIRED_ENDING` or `UNKNOWN` state-space result.
- Zero known high-severity soft-locks in shipped golden worlds.
- Abstract checker handles <=100k states within an MVP-configured budget; optimize based on measurement.
- 20 distinct sample premises across multiple seeds tracked in CI/nightly job (not necessarily every PR).
- Every published world has machine-readable `test_report.json` with schema, validator versions, world hash, reachable paths, limits and warnings.

## Playtest reporting
`status: PASS|FAIL|UNKNOWN`, `schema_ok`, `semantic_errors`, `endings[{id,status,witness}]`, `dead_ends[{state_hash,reason}]`, `navigation_ok`, `visual_review_pending`, `duration_ms`, `states_explored`, `tool_versions`. Report incomplete coverage honestly.


---
