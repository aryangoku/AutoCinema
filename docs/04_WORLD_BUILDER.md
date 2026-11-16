# 04 — World Builder / Godot 3D Specification

## Goal
Turn validated WorldIR into a cohesive, explorable **small 3D mystery world**, with modular assets, reachable interactions, predictable performance and deterministic placement. Rendering quality is important, but navigability, clue discoverability and asset consistency are hard gates.

## Recommended client architecture
- `MainMenu.tscn`, `PremiseEditor.tscn` (optional external launcher), `GameRoot.tscn`.
- `PlayerController.tscn` with `CharacterBody3D`, camera, interaction raycast, subtitles + interaction UI.
- `LocationInstance.tscn` as container for modular prefab rooms; stable entry anchor and exit markers.
- `InteractableBase.gd` owns `entity_id`, action verb, display label; **emits command requests**, never writes state directly.
- `NpcActor.tscn` with mesh, animation tree, dialog anchor, optional `NavigationAgent3D`.
- `RuntimeBridge.gd` routes interaction requests to the authoritative **localhost Python sidecar** `RealityEngine.dispatch` endpoint and listens for approved state events. Godot caches view state only.
- `SceneAssembler.gd` reads immutable manifest; instance prefab registry mapping ID -> `PackedScene`.
- `CinematicController.gd` receives only validated Director plans and owns temporary camera/UI overrides.

## Initial art direction
Choose **stylized atmospheric mystery** rather than photorealism: fog, strong silhouette lighting, reusable Victorian/coastal assets, readable item highlights, limited color palette, clean subtitles and an unobtrusive detective journal. This reduces asset scope while retaining cinematic impact.

## Asset catalog contract
Each catalog entry:
```
{
  "asset_id":"prop_iron_key_v1", "kind":"interactable_prop",
  "godot_resource":"res://assets/props/iron_key/iron_key.tscn",
  "bounds_m":[0.12,0.04,0.04], "interaction_anchor":"PickPoint",
  "tags":["key","small","metal"], "license_id":"asset_lic_001",
  "nav_behavior":"nonblocking", "compatible_styles":["coastal_mystery"]
}
```
Asset catalog entries must be hand-approved or produced by a trusted import pipeline. No arbitrary path from AI output gets passed to `load()`; check against a registry. Track license, author, source URL, commercial rights and attribution requirements for every asset. Check animation skeleton compatibility and object scale at import time.

## World assembly procedure
1. Resolve `start_location` and required location graph.
2. Select scene template for each location from curated set: harbor, tavern, lighthouse, archive room, alley.
3. Place rooms and connectors using declared anchors, dimensions and collision rules.
4. Instantiate props in tagged sockets (`desk`, `shelf`, `door`, `ground`). Respect minimum free clearance.
5. Place NPCs only at valid navigation points; assign stable entity IDs.
6. Bake navmesh or use pre-baked modular navigation regions; build paths across scene boundaries.
7. Spawn player at start anchor with non-clipping capsule; test essential interactions from spawn and ingress routes.
8. Configure lighting, sky, fog, audio zones, and post-process presets.
9. Produce `builder_report.json`: missing assets, blocked doors, navigation connectivity, performance/visibility warnings.
10. Build package only if P0 checks pass.

## Interaction design
- Inputs: WASD, mouse look, E interact, Tab inventory, J journal, Esc pause, F skip cinematic; settings remap.
- A center-screen reticle highlights valid interactable target within ~2.5m and line of sight.
- Display action affordance from authoritative rules; e.g. `Inspect shipping manifest`, `Unlock lighthouse door [requires iron key]`.
- All inspect actions record necessary evidence through the Reality Engine even if UI animation fails.
- Important clues cannot be hidden solely through tiny pixel hunting: optional highlight/assistance setting and proximity marker.

## Navigation
Godot `NavigationAgent3D` supports navigation paths/avoidance; call `get_next_path_position` in physics ticks when actively navigating, and configure navigation mesh and collision geometry. Required traversal checks: each mandatory location has valid entrance; doors have state-sensitive path connectivity; critical NPCs have reachable interaction positions. For stationary narrative NPCs, avoid unnecessary pathfinding systems.

## Cinematic compatibility
Every prefab exposes designated anchors such as `ShotWide`, `ShotClose`, `EntryMarker`, `LookAt`, plus fallback angle candidates. A generated shot references these named anchors, not raw coordinates hallucinated by an LLM. Always restore control after cutscene interruption.

## Deterministic scene generation
World package includes `seed`, ordered entities and prefab placements. Random variations (prop rotations, decor) use isolated, seeded visual RNG and cannot alter puzzle-critical object accessibility. Puzzle-critical item positions are fixed/validated to avoid changing solvability between runs.

## Technical constraints for MVP
- Target Windows desktop at 1080p, medium settings; 60 FPS goal on a specified mid-range benchmark PC, 30 FPS fallback on lower settings. Measure actual hardware.
- 3–5 small connected scenes, not seamless open world.
- 3–6 characters, ~10–30 interactables total, 5–10 critical clues.
- Use baked/stylized lighting where feasible; limit expensive dynamic shadows and effects.
- Load locations on demand; preserve logical state independent of unloaded scenes.
- Game must display a playable built-in demo even when API generation fails.

## Quality assurance
Unit: prefab registry, scene assembly IDs, interactable anchors, collision bounds. Integration: player enters all required rooms, opens all required doors, objects can be selected and picked up. Visual review: text readable, landmarks distinct, key objects recognizable. Automated: import scenes in headless Godot, instantiate smoke tests, report missing resources and crashes. Human QA still required for camera clips, discovery fairness and art coherence.


---
