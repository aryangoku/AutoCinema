# ADR-001: Milestone 1 authoritative runtime

The original WorldIR 1.0.0 and command/event envelopes remain unchanged.
The implementation adapts those contracts rather than adding a second world schema.
Typed Pydantic models cover commands, state, item ownership, beliefs, events and results.

## Semantics

- World action IDs resolve to authored definitions. `read` maps to INSPECT,
  `present` to PRESENT_EVIDENCE, and `finish`/`leave` to START_ENDING.
- `travel:<location_id>` and `talk:<npc_id>` are reserved runtime action IDs.
  The WorldIR identifier pattern excludes colons, so authored actions cannot collide.
  Travel uses authored exits and current door state. Talk uses co-located authored
  fallback text and never teaches facts implicitly. No provider or network is used.
- Targets must be present in the current location or carried by the player. This is
  abstract location validation; physical reach and line-of-sight await 3D integration.
- Item ownership is one typed holder per item; inventory is derived from that mapping.
  The reference key is retained after use because its authored effect does not consume it.
- Effects apply to a deep draft. Failure discards the entire action. Ending predicates
  are checked against the completed draft; multiple endings in one action are rejected.
- Accepted commands increment version, event sequence and simulation time (one abstract
  minute per action). RNG state records the seed; no runtime random draws exist yet.
- NPC beliefs are separate from player knowledge and canonical facts. WorldIR 1.0.0
  declares its facts as canonical; false-belief authoring and knowledge-filtered generated
  dialogue remain future work. Hidden fields never appear in the player projection.

## Persistence and replay

SQLite WAL, foreign keys and FULL synchronization are enabled. BEGIN IMMEDIATE serializes
writers. One transaction records the accepted command/result and advances the session
version. Checkpoints are stored every 50 events or on explicit save. Reading reconstructs
the snapshot plus committed event tail. Reopening also audits the full history from the
initial state. All checks use the real reducer, never a separate rules implementation.

A command ID is unique per session. Exact retries of accepted commands return the original
result, even after later actions; a changed payload using that ID is rejected. Rejected
commands never enter the authoritative event log and may be retried after conditions change.

Save/load means resume the latest committed session, including actions after its most
recent checkpoint. Named historical save slots, rewinds and branching are not implemented.
A world content hash and schema version reject incompatible saves. Checksums detect
corruption; they do not make user-editable local files tamper-proof. Session IDs are part
of canonical hashes, so deterministic comparisons use the same session ID.

## Boundaries

The console is the first controller. Godot still displays a menu; it does not own or modify
runtime state. No unauthenticated gameplay HTTP endpoints were added. Local sidecar token
negotiation, process supervision, physical interaction validation and redacted projections
will be wired into Godot in the next milestone. Source builds and the health endpoint are
version 0.2.0. Existing schema versions remain 1.0.0.
