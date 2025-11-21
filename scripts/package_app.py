#!/usr/bin/env python3
"""Helper to run PySide6 deployment with the repo spec."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    spec_file = repo_root / "pysidedeploy.spec"
    build_dir = repo_root / "build"
    build_dir.mkdir(exist_ok=True)

    if not spec_file.exists():
        print(f"[package] Spec file not found: {spec_file}", file=sys.stderr)
        return 1

    cmd = ["pyside6-deploy", "--spec", str(spec_file)]
    print(f"[package] Running: {' '.join(cmd)}")
    subprocess.run(cmd, check=True, cwd=repo_root)
    print(f"[package] Artifacts available under: {build_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
