# AutoCinema

An original story-to-playable 3D mystery project. **Milestone 1 is implemented:**
a deterministic Reality Engine, an offline console mystery with two endings, SQLite
save/resume and verified replay. Godot currently provides the desktop menu; 3D
exploration is the next milestone. No model account, API key, or network is needed
for validation or the menu after installing the development tools.

## Play the console mystery

On Windows, double-click `Play AutoCinema.cmd` after installing dependencies.
Or run from the repository root:

```powershell
.venv/Scripts/python.exe tools/dev.py play
```

Choose numbered actions to explore, inspect clues, take the key, talk to characters,
and resolve the mystery. Type `s` to checkpoint or `q` to save and quit. Every accepted
action is automatically committed to SQLite. The console prints your session ID.
To resume, use the same database and session:

```powershell
.venv/Scripts/python.exe tools/play_console.py --session YOUR_SESSION_ID
```

Saves default to `generated/blackwater.sqlite3` (gitignored). Use `--database PATH`
for a different save database. Resume restores the latest committed action; named
historical save slots are not implemented.

Run both verified ending routes, including a real mid-route save/reopen and replay:

```powershell
.venv/Scripts/python.exe tools/dev.py demo
```

## Quick start (Windows PowerShell)

Use Python 3.12+ (tested locally with 3.13.1) and Godot **4.7.2 stable**.
From the repository root:

```powershell
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements.lock
.venv/Scripts/python.exe tools/dev.py check
.venv/Scripts/python.exe tools/dev.py validate
$env:GODOT_BIN = 'C:\path\to\Godot_v4.7.2-stable_win64_console.exe'
.venv/Scripts/python.exe tools/dev.py godot-test
.venv/Scripts/python.exe tools/dev.py game
```

Alternatively import `game/project.godot` in Godot 4.7.2 and press F6 on
`scenes/app/MainMenu.tscn`, or F5 to run the project. The menu opens a reference
mystery information dialog and supports Quit. It deliberately does not offer
nonfunctional 3D gameplay buttons. Use the console command above to play now.

On Linux/macOS use `.venv/bin/python` and `export GODOT_BIN=/path/to/godot`.
The lock contains exact direct and transitive dependency versions; platform wheels
are selected by pip. Only Windows/Python 3.13.1 has been executed locally.

```powershell
.venv/Scripts/python.exe tools/dev.py api
```

Development health endpoint: `http://127.0.0.1:8000/health`. This server exposes
health only; no generation, session commands, or world secrets. Gameplay endpoints
will require per-session authentication when introduced.

## Working commands

- `python tools/dev.py check`: Ruff lint/format, mypy, pytest, reference validation, secrets scan.
- `python tools/dev.py test`: Python tests.
- `python tools/dev.py format`: automatic Python formatting and import cleanup.
- `python tools/dev.py godot-test`: exact-version check, headless import, menu interaction smoke test.
- `python tools/validate_world.py examples/blackwater_harbor.json`: JSON validation report.

Validator exits 0 for PASS and 2 for invalid input/schema/semantics. Errors contain
stable codes and JSON paths. PASS means schema and static references passed, **not**
solvability, navigation, asset availability, or a completed game. Prefab validation
checks declarations and kind in the world's manifest; a trusted on-disk registry
and licensed meshes are later work.

## Repository

- `backend/validator/`: JSON Schema adapter and semantic checks.
- `backend/app/`: FastAPI health endpoint, Pydantic response contract.
- `backend/engine/`: pure reducer, typed state/commands/events, SQLite persistence and replay.
- `tools/play_console.py`: interactive mystery and verified ending demonstrations.
- `schemas/`: original six interchange schemas from the supplied specification.
- `examples/`: canonical Blackwater Harbor world, preserved without story changes.
- `game/`: Godot menu and headless test.
- `tests/`, `tools/`, `.github/workflows/`: checks and developer tooling.
- `docs/`, `prompts/`: supplied design documents and implementation decisions.

The supplied docs/prompts are **design references**, not instructions automatically
executed by the application. Future milestones and performance targets in them
are not implemented claims. Implementation status is in `docs/IMPLEMENTATION_STATUS.md`.

## Architecture

Godot is the view/controller. The Python Reality Engine owns authoritative
state; every inventory, fact, door and ending change must pass a typed command.
Generated JSON is data, never executable code. The menu loads no hidden truth.
The WorldIR schema is authoritative; the Python adapter uses it directly instead
of maintaining a second hand-written copy of the model rules.

Next: Milestone 2, the first playable Godot 3D slice connected to this engine.
Runtime choices and limits are documented in `docs/ADR_001_REALITY_ENGINE.md`.

## Troubleshooting restricted environments

If your runner cannot write its default temporary directory, set `TEMP` and `TMP`
to an existing writable scratch directory before installing or testing. For Godot
in a restricted environment, use its self-contained mode: place an empty `._sc_`
file next to the executable in a writable tools directory. Do not commit editor
settings, virtual environments, credentials, or generated game data. If the runtime
cannot write user data, set `APPDATA` to a writable scratch directory for the test
process only; do not change your system-wide user profile settings.
