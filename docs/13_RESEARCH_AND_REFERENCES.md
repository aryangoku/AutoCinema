# 13 — Technical References and Verification Notes

Sources checked 2026-11-13; version-dependent details should be verified again before implementation. Links are background/documentation, not endorsements, and their licensing terms differ.

## Engines / runtime
- Godot release support policy: https://docs.godotengine.org/en/stable/about/release_policy.html — indicates 4.7 supported; pin actual patch in project.
- Godot 4.7 features: https://docs.godotengine.org/en/4.7/about/list_of_features.html
- NavigationAgent3D stable: https://docs.godotengine.org/en/stable/classes/class_navigationagent3d.html — pathfinding, physics-step update, navigation mesh requirements.
- Godot CLI/headless: https://docs.godotengine.org/en/latest/tutorials/editor/command_line_tutorial.html
- Godot 4.7 exporting: https://docs.godotengine.org/en/4.7/tutorials/export/exporting_projects.html
- GdUnit4 tests: https://github.com/godot-gdunit-labs/gdUnit4 — verify compatibility with chosen Godot patch.
- ink scripting: https://www.inklestudios.com/ink/ — useful optional narrative authoring adapter; note ink is middleware rather than a whole game engine.
- ink runtime repository: https://github.com/inkle/ink — C#/JS runtime orientation; integration in Godot is not guaranteed plug-and-play.

## AI, security, schemas
- Structured model outputs: https://developers.openai.com/api/docs/guides/structured-outputs — schema adherence doesn't imply semantic validity; handle refusals, interruptions, unsupported JSON Schema features.
- OWASP prompt injection prevention: https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html — treat natural-language material as data, validate tools, least privilege, output checks.
- FastAPI documentation: https://fastapi.tiangolo.com/
- Pydantic documentation: https://docs.pydantic.dev/latest/
- Python JSON Schema validation: https://python-jsonschema.readthedocs.io/en/stable/

## Algorithms to research
- Automated planning: breadth-first search, A*, STRIPS-like preconditions/effects; state-space size, cycles, and soft-lock detection.
- Model checking: CTL/LTL concepts for richer reachability/safety properties later; no need to implement full formal model checker in MVP.
- Property-based testing: Hypothesis for Python action-sequence invariants.
- Knowledge representation: fact graph, beliefs vs actual truth, information flow/provenance.
- Event sourcing and deterministic replay: sequence/idempotency/hash checks, versions and seeds.
- Cinematography: shot language, 180-degree rule, continuity editing; use constrained shot grammar before LLM planning.

## Competitive and product context
The existence of prompt-to-game tools, AI storytelling platforms and generative world models means “type a prompt, get something playable” by itself is not a defensible claim of uniqueness. Differentiation proposed here is **typed narrative reality, character knowledge integrity, replayable causal consequences, automated solvability proof paths, and trustworthy failure reporting**. Measure these directly instead of claiming universal superiority.

## Research and evaluation ethics
Use licensed or original stories, models, meshes, textures, animations, sound, and voices. Never imply that generated content is historically accurate by default. User-generated stories and AI character outputs need clear moderation/ratings rules before a public content-sharing platform is launched.


---
