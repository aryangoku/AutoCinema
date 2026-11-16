# 15 — Practical Getting-Started Handbook (Human + AI Agent)

## Goal for the first development session
Set up a repository, validate the included schema and reference fixture, create a Godot project that opens to a menu, and establish a repeatable test command. Do NOT start by asking a model to generate 3D worlds or write the entire app.

## Recommended development workstation
- Windows 11/macOS/Linux all possible; Windows target for initial export.
- Git; Python 3.12+; a terminal; VS Code or JetBrains IDE; current supported Godot 4.7 patch; optional Blender for asset inspection.
- Install Python `jsonschema` to run the included *specification* validator; install `pytest`, `ruff`, FastAPI and Pydantic after scaffolding the actual app.
- Optional model API account for compiler phase later; not required for milestones 0–3.
- Source control from day one; do not commit `.env` or API keys.

## Quick reference-pack check
From the extracted `AutoCinema_Build_Blueprint` folder:
```
python -m pip install jsonschema
python tools/check_reference.py examples/blackwater_harbor.json
python -m unittest discover -s tests -v
```
Expected (as of spec preparation): WorldIR passes structural/semantic checks and a bounded abstract checker finds one path to both reference endings; five reference checker unit tests pass. **These are documentation-fixture checks, not a playable game or final verifier.**

## Give the documentation to a coding AI
1. Extract the ZIP into an `AutoCinema_Build_Blueprint` folder or provide the single `AUTOCINEMA_MASTER_SPEC.md`.
2. Supply `prompts/AI_CODING_AGENT_MASTER_PROMPT.md` as the coding agent's project instruction.
3. Tell the agent where it should create the **actual new code repository** (do not overwrite the specification pack unless intentionally versioning docs).
4. Ask it to implement **Milestone 0 only**: repo structure, validation, tests and minimal Godot menu.
5. Have the agent show actual commands/test results; open and check the Godot project locally.
6. Continue ticket by ticket using `prompts/ENGINE_IMPLEMENTATION_PROMPTS.md`.
7. Keep this spec and the implementation in the same Git repository once stabilized, so docs/tests evolve together.

## Suggested initial repo creation commands
```
git init autocinema
cd autocinema
mkdir backend game tools docs schemas examples tests
# Copy this pack's schemas/, examples/, docs/, and prompts/ into repo.
# Make a Python pyproject.toml and install pinned dev dependencies.
# Create a new Godot project in game/ with MainMenu.tscn.
```
These are illustrative shell commands; adapt to PowerShell (or let the coding agent create directories). Do not try to run missing application modules until the agent has created them.

## The first 5 demos to build, in order
1. **Schema + terminal:** print a world definition and validate it with clear errors.
2. **Console mystery:** type `take key`, `read journal`, `confront Elena`; observe events and two endings.
3. **3D mystery:** move through placeholder rooms and interact with objects; all state controlled by Python sidecar.
4. **Deterministic generator:** change a seed/template and get a different but still solvable small world.
5. **AI-generated story:** replace template choices with model-generated *validated* structure; never replace existing validator.

## What to provide the AI when blocked
Send actual project tree, logs, error stack, failing command, your OS, exact Python/Godot versions, and which ticket is currently being implemented. Ask for the smallest safe correction with a regression test. Avoid vague requests like “fix everything”.

## Human decisions not worth blocking the first milestone
Character visual style, optional NPC voice, final logo/name, exact model provider, music choice, monetization, user accounts, marketplace and open-world gameplay. Defaults in this specification can be revised after the first executable vertical slice.

## Human decisions to verify early
1. Whether the bundled Python sidecar packaging approach is acceptable for desktop distribution; test a frozen executable early.
2. License/attribution of your initial assets.
3. First-person camera comfort and readability.
4. Network behavior when no Internet or API key exists.
5. The budget/quality tradeoff for generated character dialogue.

## Definition of "we have started building"
A real local repository exists; the reference fixture validates; automated tests are green; Godot launches; and one screenshot/terminal output demonstrates a working, version-controlled milestone. A long architecture document alone is preparation, not implementation.


---

# AI CODING AND GENERATION PROMPTS


---
