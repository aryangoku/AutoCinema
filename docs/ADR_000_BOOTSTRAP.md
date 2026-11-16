# Bootstrap decisions

Date: 2026-11-16

The user requested that development begin in the existing empty AutoCinema repo.
The attached coding prompt is project context; the bounded Milestone 0 scope was
selected as the first useful implementation increment. The full product and later
milestones are not represented as complete.

- Preserve Godot + Python architecture. Pin Godot 4.7.2 stable, verified locally as
  `4.7.2.stable.official.ed1daf0bf` using the existing downloaded Windows archive.
- Python 3.13.1 locally; Python >=3.12 declared. Exact Python dependencies are in
  requirements.lock. Build tooling is development-only, no runtime AI dependency.
- Adopt WorldIR 1.0.0 unchanged from the supplied master document, including the
  canonical example. JSON Schema is the authoritative structure adapter; Pydantic
  models cover diagnostic/API envelopes. This avoids schema/model drift.
- Do not promote the documentation-only BFS checker into the runtime. Reachability
  must use the authoritative reducer once it exists.
- Manifest membership and asset kinds can be checked now. This does not prove that
  a prefab exists on disk. No third-party art assets have been installed or shipped.
- Flags are declared by set_flag effects under the original 1.0.0 schema; predicates
  must refer to one of those declarations. Reachability remains unverified.
- Health-only API binds to loopback through the provided launcher. Stateful API,
  SQLite, session authentication and process supervision belong to later work.
