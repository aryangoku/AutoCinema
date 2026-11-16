# Asset and dependency policy

No external artwork, audio, fonts, character models or environment packs are included.
The menu uses Godot's built-in UI and font. World prefab IDs are symbolic declarations,
not shipped scenes. Do not resolve generated IDs directly into file paths or URLs.

Before shipping assets, maintain a trusted registry with asset_id, kind,
repository-relative resource_path, origin URL, license identifier/text, author,
attribution requirement and redistribution/commercial permission. Reject unmapped
IDs, path traversal, remote resources and assets lacking verified permission.

Godot is distributed under MIT; preserve its copyright/license and third-party
notices when distributing the engine. Python packages retain their own licenses;
requirements.lock is a version inventory, not a licensing clearance. Review and
bundle required notices before any packaged game release. Project source licensing
has not been selected by the owner; no blanket license is assumed for supplied docs.
