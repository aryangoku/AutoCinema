"""Fail on potential secrets in Git-tracked files (no network verification)."""

import json
import subprocess
import sys
from pathlib import Path


def main() -> int:
    executable = sys.executable
    result = subprocess.run(
        [
            executable,
            "-m",
            "detect_secrets",
            "scan",
            "--no-verify",
            "--exclude-files",
            r"^\.secrets-allowlist\.json$",
        ],
        cwd=Path(__file__).resolve().parents[1],
        check=True,
        capture_output=True,
        text=True,
    )
    findings = json.loads(result.stdout)["results"]
    # Exact reviewed false positives only; changing the content invalidates the allowance.
    allowlist = json.loads(
        (Path(__file__).resolve().parents[1] / ".secrets-allowlist.json").read_text()
    )
    findings = {
        filename: [
            entry
            for entry in entries
            if not any(
                filename.replace("\\", "/") == allowed["file"]
                and entry["hashed_secret"] == allowed["hash"]
                and entry["type"] == allowed["type"]
                for allowed in allowlist
            )
        ]
        for filename, entries in findings.items()
    }
    findings = {filename: entries for filename, entries in findings.items() if entries}
    if findings:
        print(json.dumps(findings, indent=2))
        return 1
    print("PASS: no potential secrets in tracked files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
