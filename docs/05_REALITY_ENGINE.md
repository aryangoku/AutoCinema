# 05 — Story Reality Engine (Core Technical IP)

## Goal and trust model
This is the single source of truth for a play session. It evaluates commands, enforces preconditions, mutates state transactionally, and publishes events. LLMs, UI widgets, NPC meshes, cinematics and imported story text are **untrusted proposal/view layers**.

## Canonical state model
```
GameState {
  world_id, world_version, session_id, state_version, sim_time, rng_state,
  current_location, player_position?, player_inventory: [item_id],
  items: {item_id: {holder_type, holder_id, state}},
  doors: {door_id: locked/open/closed},
  npc_locations: {npc_id: location_id},
  npc_goals: {npc_id: [goal_id]},
  facts_true: [fact_id],
  player_known_facts: [fact_id],
  npc_beliefs: {npc_id: [{fact_id, believed_truth, source_event_id, confidence}]},
  quest_flags: [flag_id], relationships: {npc_id: {target_id: score}},
  interactions_seen: [action_id], ending_id: null|string,
  event_seq, previous_state_hash
}
```
Use explicit schemas and migration versions, not arbitrary nested dictionaries throughout the final implementation. Distinguish objective truth, a character's beliefs, and what the player has learned; beliefs can be incorrect or uncertain.

## Command design
Typed commands: `MOVE_TO`, `TRAVEL`, `INSPECT`, `TAKE`, `DROP`, `USE`, `UNLOCK`, `TALK`, `PRESENT_EVIDENCE`, `CHOOSE_DIALOGUE`, `CONFRONT`, `WAIT`, `START_ENDING`. All calls include command ID (idempotency), acting entity, target ID and version expected. The authority (player or NPC) and range/line-of-sight checks occur outside/inside reducer according to command type. Never trust client-supplied distance/permission.

## Allowed preconditions (DSL, no code execution)
`has_item(item_id)`, `at_location(location_id)`, `knows_fact(actor_id,fact_id)`, `door_state(door_id,state)`, `flag_is(flag_id,bool)`, `npc_present(npc_id,location_id)`, `relationship_at_least(npc_id,threshold)`, and logical `all/any/not` with depth/size limits. Interpret with an exhaustive enum dispatcher; reject unknown predicates.

## Allowed effects
`move_item(item_id,from,to)`, `learn_fact(actor_id,fact_id,source_event_id)`, `set_flag(flag_id,bool)`, `set_door_state(door_id,state)`, `move_actor(actor_id,location_id)`, `adjust_relationship(...)`, `advance_time(minutes)`, `schedule_cinematic(cue_id)`, `trigger_ending(ending_id)`. Each effect has a validator, bounds, and invariant checks. No generic `execute_script` effect.

## Reducer algorithm
```
def dispatch(cmd, state, world):
    if already_applied(cmd.command_id): return prior_result(cmd.command_id)
    if cmd.expected_version != state.version: return conflict(current_version)
    definition = world.lookup_action(cmd.action_id)
    if not actor_authorized(cmd.actor_id, definition, state): return denied()
    if not valid_target_and_range(cmd, state): return denied()
    if not predicates_true(definition.preconditions, state): return rejected(reason)
    candidate = deep_copy_or_copy_on_write(state)
    apply_typed_effects(definition.effects, candidate)
    if not all_invariants_hold(candidate): return rejected(invariant)
    event = make_event(cmd, state, candidate)
    atomically_commit(candidate, event, state.version + 1)
    return accepted(state_version=..., events=[event])
```
This is design pseudocode, not a drop-in runnable module. Implement state mutation and event append atomically; keep one writer per game session. Use explicit results rather than exceptions for ordinary illegal game actions.

## Critical invariants / test properties
- No item duplication; each item has exactly one holder/location.
- No negative health/currency/resource values if introduced.
- All entity references resolve; state fields constrained to declared enum/range.
- No knowledge revealed without a valid event observation, speech act or authored backstory.
- No state mutation on rejected command.
- Replay of identical initial snapshot + ordered commands + RNG state yields identical canonical state hash.
- Save/load gives the same state hash before any subsequent command.
- All endings are irreversibly settled once triggered unless user explicitly forks/reloads a save.
- Confrontations without required evidence either fail, redirect or lead to a defined wrong-ending path.

## Event sourcing and time travel
Event fields: `event_id`, `seq`, `session_id`, `command_id`, `actor`, `action_type`, `entity_ids`, `state_diff`, `sim_time`, `rng_before`, `rng_after`, `world_version`, `state_hash_after`. Store snapshot every N actions (e.g., 50) plus event tail. Time travel in MVP means **load a prior snapshot and replay**; branching timelines are post-MVP and require unique branch IDs and parent references.

## Canonical truth and information flow
`facts_true` is hidden world truth, not necessarily visible. `player_known_facts` stores confirmed discoveries. Each NPC has `beliefs`, `observation_scope`, `secrecy_policy` and `conversation_history_summary`. Characters can lie about facts they know, but cannot truthfully reference information they were never exposed to. Separate what an NPC *says* from what a player *knows*; hearing a rumor creates a `heard_claim` and does not necessarily mark the claim as true.

## Clues, puzzles, endings
Represent puzzles as predicates/effects. For example `UNLOCK lighthouse_door` requires `has_item(iron_key)` and `at_location(lighthouse)`; effect changes door state and logs event. `CONFRONT elena` requires `fact_power_cable` and `fact_manifest_after_disappearance`; effect sets `flag_elena_confronted` and permits `ending_truth_revealed`. Ending predicates are evaluated by rule interpreter at dispatch time, never inferred from dialogue sentiment.

## Replay and debug overlay
Expose state version and event trace in creator/developer builds. Investigate any reported contradiction by replaying from a saved seed + event log, then comparing state hashes. A player-facing optional journal can summarize past actions but shouldn't leak hidden state.

## Extension hooks
After solid core: NPC schedules through planned actions; cutscene-trigger policy; reputation updates; branching saves; time-dependent clues. Keep these modules as event consumers/producers that call the same dispatch interface rather than bypassing state authority.


---
