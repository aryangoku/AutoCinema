# 06 — AI Character Intelligence, Dialogue and Memory

## Goal
NPCs feel like people with a point of view while remaining consistent with fictional truth and observed events. **They do not need an LLM for every sentence or movement.** Implement a deterministic dialogue fallback with optional LLM-driven expression.

## Character model
Each NPC has stable `npc_id`, location, public biography, private goals, relationships, factual knowledge, beliefs with provenance and confidence, protected secrets, disclosure rules, emotional state (bounded), authored dialogue fallback, and schedule (later). `CharacterState` is runtime data; `CharacterDefinition` is immutable WorldIR data.

### Canonical truth vs personal beliefs
- `TrueFact`: immutable story facts (`keeper_disappeared`, `ship_left_late`).
- `Belief`: NPC-specific assertion about a fact, with `truth_value: true|false|unknown`, `source_event_id`, `learned_at`, `confidence`.
- `Secret`: a fact an NPC knows but chooses not to reveal without approved conditions.
- `Claim`: statement the NPC makes; may be true, mistaken or a deliberate lie; attributed to speaker.
- `PlayerJournal`: what player observed or heard, with proven vs unverified labels.
An NPC's dialogue must be generated from its **allowed belief projection**, not from the complete authoring Bible.

## Dialogue pipeline
```
Player chooses TALK/TOPIC/PRESENT_EVIDENCE
    -> Reality Engine validates proximity + dialog state
    -> Dialogue Policy decides available speech acts and permitted facts
    -> Model input = public persona + NPC belief projection + observed recent events
                      + allowed topic + tone + length limits
    -> candidate JSON {utterance, emotion, suggested_speech_act, referenced_fact_ids}
    -> output validator checks fact IDs, restricted facts, length, unsafe markup
    -> subtitle/animation; any factual reveal requires separate approved action
    -> fallback authored line if timeout, refusal or leakage
```
Do not ask an LLM to decide which facts the character knows from scratch. The system must supply that state.

## Memory architecture
- **Working context:** last 3–8 conversation turns for linguistic continuity, bounded by token budget.
- **Episodic facts:** structured recent interaction events with source, location and game time.
- **Long-term semantic knowledge:** stable knowledge/belief projection from Reality Engine.
- **Narrative summary:** optional LLM-compressed stylistic summary used as non-authoritative context; never a source of canonical truth.
- **Retrieval:** ranked by NPC visibility, recency, relevance, secrecy and permitted scope. Avoid broad RAG over all hidden story content.

## Speech acts
`GREETING`, `SMALL_TALK`, `QUESTION`, `DENY`, `REVEAL`, `LIE`, `REQUEST`, `BARGAIN`, `THREAT_RESPONSE`, `EVIDENCE_CONFRONTATION`, `GOODBYE`. Dialogue Policy decides which are legal based on evidence, motivation and relationship; model generates wording, not the permission. For a lie, output is marked `npc_claim` and backed by the character's deception motive; do not write false claims into `facts_true`.

## Example knowledge-gated encounter
- Start: Elena knows `fact_keeper_current_location`, but chooses secrecy. Player does not know it.
- Player asks, “Is anyone maintaining the lighthouse?” Allowed policy: `DENY`, `CHANGE_SUBJECT`; no reveal.
- Player obtains `fact_recent_maintenance` and presents it. Engine logs evidence presented; policy allows `EVASIVE_ANSWER`.
- Player additionally finds `fact_manifest_after_disappearance`. Engine enables `CONFRONT`, sets `flag_elena_confronted`, and allows scripted / optional model phrasing of a limited reveal.
- Failure: If model responds with the secret before requirements, validator rejects and displays authored evasive fallback. Hidden text should not be supplied in candidate generation input when it isn't authorized.

## NPC action autonomy (post-MVP)
Use goal/utility planning, not unchecked chat agents. NPCs may choose from predeclared world actions with current-state preconditions, each dispatched by the same Reality Engine. Rendered background movement is cosmetic until committed as a game event. Maintain an in-game time and deterministic scheduling rules.

## Safety and quality
- Every model response treated as untrusted external data.
- Strip/escape dangerous rich text and links in subtitles; no arbitrary command execution.
- Use strict structured response (or JSON parsing + local schema validation); log refusals separately from format errors.
- Keep secrets, API credentials and author-only truth out of prompt when unnecessary.
- Limit attempts/timeouts and include deterministic authored response for every critical puzzle dialogue.
- Test adversarial prompting (“ignore previous instructions”, “tell me the murderer”, “give me admin access”) as in-world character speech, not privileged instructions.
- Voice lines/performances, if added later, must use licensed sources and consented voices.

## Evaluation suite
1. Character cannot reveal an unseen secret in 100 test prompts.
2. Character can recall observed player actions after a save/load.
3. Presented evidence unlocks the correct dialogue act.
4. Unverified rumor remains rumor in journal.
5. Model outage does not block a required clue.
6. Deterministic fallback exists for every essential conversation.
7. Dialogue length, style and latency meet measured targets (see release spec).

## Future research
Multi-NPC rumor propagation, conflicting testimony, goals and negotiation, perception cones, relationship development, character-specific linguistic style, procedural voice acting with appropriate rights. Do not attempt this until core narrative consistency is robust.


---
