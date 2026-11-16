# 07 — Cinematic Director Engine

## Goal
Automatically present game events using controlled camera language, lighting/audio presets, subtitle timing and animation cues, without breaking interactivity or inventing story facts.

## Design rule
The Reality Engine emits **events**; the Director selects presentation **for those actual events**. The Director cannot create proof, inventory, NPC knowledge, endings or gameplay decisions. Its cutscene can be canceled/skipped without changing the outcome of an already committed action.

## Trigger types
- `LOCATION_ENTERED`: brief establishing camera or title card.
- `EVIDENCE_DISCOVERED`: detail close-up plus journal confirmation.
- `NPC_CONFRONTED`: shot/reverse-shot using validated actor anchors.
- `QUEST_TURNING_POINT`: tonal lighting/audio cue; no obstructive autoplay.
- `ENDING_TRIGGERED`: composed final sequence, recap, credits.

## Storyboard / ShotPlan DSL
```
{
  "plan_id":"cin_cable_reveal",
  "trigger_event":"EVIDENCE_DISCOVERED",
  "location_id":"loc_lighthouse",
  "shots":[
    {"shot":"INSERT","anchor":"obj_power_cable:LookAt","duration_s":2.5},
    {"shot":"OVER_SHOULDER","anchor":"player:CameraAnchor","duration_s":2.0}
  ],
  "audio_cue":"aud_reveal_soft",
  "subtitle_id":"line_cable_not_old",
  "skip_allowed":true
}
```
This is a conceptual DSL. In implementation validate `shot`, `anchor`, durations, audio IDs and location refs; only use asset registry resources.

## Rule-based MVP director
1. On supported event, choose one of a small curated `ShotPlan` templates.
2. Resolve participants and anchors; test camera rays against walls and actor occlusion.
3. Apply pacing constraints (e.g., max 6 seconds for ordinary item inspection; skippable).
4. Ease camera to target; trigger animation and licensed sound; display subtitles.
5. Restore player camera, controls and audio state in all exit paths (normal, skip, load, crash-recover).

## Camera inventory
`ESTABLISHING_WIDE`, `MEDIUM`, `CLOSE_UP`, `INSERT`, `OVER_SHOULDER`, `TWO_SHOT`, `TRACKING`, `REACTION`. Each maps to preapproved relative poses and collision-aware candidate anchors. Prevent camera clipping by ray checks / fallback to safe fixed camera. Respect FOV and motion comfort settings.

## Lighting/audio
Use scene-level presets: `MYSTERY_DAY`, `FOG_NIGHT`, `TENSION_INTERVIEW`, `REVEAL`, `ENDING`. Stems/music loops must be licensed, mixed below dialogue and accessibility-safe; captions label important non-dialogue sounds. Avoid generated copyrighted music unless appropriate rights exist.

## Optional AI Director (post-MVP)
Given an actual event, permitted scene entities, shot catalog and player comfort settings, model can suggest a constrained ShotPlan. Validate candidate; fail over to deterministic shot. **Do not** let it spawn new actors or imply events that did not occur.

## Performance / comfort rules
- No expensive realtime cinematic synthesis in V1; preset animations + reusable shaders.
- Preload critical camera paths and audio before playback.
- Skip button always available on critical story scenes; skipping still applies the event result.
- No sudden unannounced flashes, extreme shake, or uncontrollable camera swings.
- Return to exact safe player position and view; input reenabled even if animation is interrupted.

## Automated tests
- All mandatory triggers map to a valid template and known anchors.
- Every shot ends or times out, and all cutscenes are skippable.
- Camera anchor missing -> fallback `MEDIUM` safe camera, no crash.
- Story event IDs are logged once even if cutscene restarts.
- Video/headless tests for mechanics plus visual tests for composition/human QA.


---
