# 09 — API, Database and Interchange Contracts

## Data ownership and canonical schemas
`schemas/world.schema.json` is the initial interchange schema for WorldIR. Treat it as a starter baseline; evolve it with tests and generated Pydantic types. Keep separate schemas for full internal generation drafts, immutable build manifest, runtime commands/events, and UI views. Do not duplicate schema rules by hand without parity tests.

## REST (versioned /v1) — proposed
| Method | Endpoint | Purpose | Key request/response |
|---|---|---|---|
| POST | `/v1/worlds/draft` | Create blueprint from premise | `{premise, template, tone, seed}` -> `{job_id}` |
| GET | `/v1/jobs/{id}` | Inspect state/progress/errors | `{stage,status,progress,issues}` |
| POST | `/v1/worlds/{id}/validate` | Run schema/semantic/graph checks | `{report_id,status,issues}` |
| POST | `/v1/worlds/{id}/compile` | Build validated world package | `{job_id}`; returns immutable hash on completion |
| GET | `/v1/worlds/{id}/artifact` | Download local package/manifest | signed or local-only artifact response |
| GET | `/v1/worlds/{id}/report` | Validation/playtest report | `{report,...}` |
| POST | `/v1/dialogue` | Optional candidate NPC utterance | input filtered state view -> validated text response |
| GET | `/health` | Server health | `{status,version}` |

Use `Idempotency-Key` for generation requests, `X-Request-ID` for traceability, and structured error codes. `POST /dialogue` must never include raw hidden world truth beyond permitted character projection. Generated games must remain playable if this service is offline.

## Example create request
```
POST /v1/worlds/draft
{
 "premise":"A detective arrives at a coastal town ...",
 "template":"coastal_mystery", "tone":"suspenseful",
 "target_minutes":15, "seed":1042
}
```
Reply `202 Accepted`: `{"job_id":"job_...","status":"QUEUED"}`; poll or subscribe for progress. Do not keep a synchronous HTTP request open for entire generation pipeline.

## Progress channel
Use WebSocket or SSE `/v1/jobs/{id}/events` for `stage_started`, `stage_progress`, `validation_failed`, `repair_started`, `stage_completed`, `build_ready`; include sequence number for resuming after disconnect. `FAILED` always includes recoverable error text, trace correlation ID and actionable stage context.

## Unified error contract
```
{"error":{"code":"SEMANTIC_UNREACHABLE_ENDING",
 "message":"Ending cannot be reached from the initial state",
 "details":[{"path":"endings[1]","entity_id":"ending_truth"}],
 "request_id":"req_123","retryable":false}}
```
Never expose provider credentials, raw model prompts, user file paths, database stack traces or hidden secrets to player-facing error messages.

## Suggested SQLite tables
```
worlds(world_id PK, schema_version, world_hash UNIQUE, title, ir_json, created_at)
world_builds(build_id PK, world_id FK, compiler_version, asset_catalog_version,
             artifact_path, status, report_json, created_at)
generation_jobs(job_id PK, world_id NULL, status, stage, stage_attempts, errors_json,
                idempotency_key UNIQUE, created_at, updated_at)
sessions(session_id PK, build_id FK, state_version, snapshot_json, rng_state,
         current_ending_id NULL, updated_at)
events(session_id FK, seq, command_id UNIQUE, event_json, state_hash, created_at,
       PRIMARY KEY(session_id,seq))
asset_registry(asset_id PK, kind, resource_path, license_id, metadata_json)
asset_licenses(license_id PK, source, license_name, attribution, commercial_ok)
model_usage(job_id, stage, provider, model, input_tokens, output_tokens, cost_estimate,
            duration_ms, cache_hit, created_at)
```
Encrypt or exclude sensitive content as appropriate. Never store raw provider API keys in DB. Add backup/export before changing schema. Use database transactions for command/event save.

## Runtime local sidecar endpoints
In addition to authoring APIs, expose `POST /v1/sessions` to load a compiled world, `POST /v1/sessions/{id}/commands` to dispatch an authoritative command, `GET /v1/sessions/{id}/state` for redacted player-facing state, and `POST /v1/sessions/{id}/save` / `POST /v1/sessions/{id}/load` for saves. All endpoints localhost-only with per-session authentication. Never send full hidden truth in a player-facing state response.

## Runtime command envelope
```
{"command_id":"uuid", "session_id":"uuid", "expected_state_version":42,
 "actor_id":"player", "action_id":"act_take_manifest",
 "target_id":"item_manifest", "args":{}, "issued_at":"ISO8601"}
```
Runtime returns accepted/rejected with new version, emitted events and reason. For offline single-player MVP, this is a localhost command to the **bundled Python Reality Engine sidecar**. It requires no Internet connection but does require the sidecar process. Use an ephemeral per-session token and origin checks on local endpoints.

## World package contents
```
worlds/<world-id>/<build-hash>/
  world.json          # validated and immutable WorldIR
  manifest.json       # version, content hash, asset IDs, checksums, generator versions
  test_report.json    # proof paths and checker limits
  scene_plan.json     # template rooms, prop placements, nav anchors
  creator_report.json # warnings/assumptions; no player-visible spoilers
```
Compiler-side private truth may be packaged into runtime-required facts but never into unfiltered dialogue prompts or player UI. Shipping game binaries cannot guarantee secrecy from someone who inspects local files; avoid treating fictional spoiler data as security-sensitive.

## Version compatibility
- Schema version MAJOR mismatch -> reject with upgrade path.
- Minor update -> migrate via explicit tested transformation.
- Package manifest hash mismatch -> reject corrupted file.
- Runtime event version must match reducer version used for replay; write migrations/golden tests before changing event semantics.
- Model provider response schema may be narrower than internal WorldIR; map/validate stage schemas before merging.

## Provider adapter contract
`generate_structured(stage, schema, context, budget) -> Success(parsed, usage) | Failure(code, retryable)` with timeout, exponential backoff for transient failures, no retries for invalid premises beyond configured repair budget, per-user/per-job spend limit, cache and audit metadata. Structured outputs do not replace semantic validation. Keep secrets server-side; local runtime may use user-provided BYOK only through protected settings, never bundled credentials.


---
