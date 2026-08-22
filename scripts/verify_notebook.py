#!/usr/bin/env python3
"""Verify one or more rct-visualization marimo notebooks.

This is the executable companion to skills/rct-notebook/SKILL.md. It does not
claim that execution proves clinical correctness; it proves the notebook can be
parsed, exported, run, and structurally inspected. Source-number arithmetic
still needs trial-specific review.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUIRED_MARKERS = (
    "@app.cell",
    "CONSORT",
    "provenance",
    "if __name__ == \"__main__\":",
    "app.run()",
)


def run(command: list[str], *, cwd: Path, stdout=None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=cwd,
        stdout=stdout,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )


def verify(path: Path, *, skip_ruff: bool = False) -> bool:
    path = path.resolve()
    print(f"\n== {path.relative_to(ROOT)} ==")
    text = path.read_text(encoding="utf-8")
    missing = [marker for marker in REQUIRED_MARKERS if marker not in text]
    if missing:
        print("STRUCTURE_FAIL: missing " + ", ".join(repr(m) for m in missing))
        return False
    print("STRUCTURE_OK")

    if not skip_ruff:
        result = run(["uv", "run", "ruff", "check", str(path)], cwd=ROOT)
        if result.returncode:
            print("RUFF_FAIL")
            print(result.stderr.strip())
            return False
        print("RUFF_OK")

    with tempfile.NamedTemporaryFile(
        mode="w+", suffix="-marimo-export.py", delete=False
    ) as exported:
        export_path = Path(exported.name)
    try:
        with export_path.open("w", encoding="utf-8") as output:
            result = run(
                ["uv", "run", "marimo", "export", "script", str(path)],
                cwd=ROOT,
                stdout=output,
            )
        if result.returncode:
            print("EXPORT_FAIL")
            print(result.stderr.strip())
            return False
        print("EXPORT_OK")

        result = run(["uv", "run", "python", str(export_path)], cwd=ROOT)
        if result.returncode:
            print("EXECUTE_FAIL")
            print(result.stderr.strip())
            return False
        print("EXECUTE_OK")
        return True
    finally:
        export_path.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("notebooks", nargs="+", type=Path)
    parser.add_argument("--skip-ruff", action="store_true")
    args = parser.parse_args()

    ok = True
    for path in args.notebooks:
        if not path.is_absolute():
            path = ROOT / path
        if not path.is_file():
            print(f"MISSING: {path}")
            ok = False
            continue
        ok = verify(path, skip_ruff=args.skip_ruff) and ok
    print("\nALL_OK" if ok else "\nFAILURES_PRESENT")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
