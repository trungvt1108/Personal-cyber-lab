"""Lint only exact public Markdown candidates, excluding ignored runtime files."""

import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.check_repository import candidate_files  # noqa: E402


def main() -> int:
    name = "pymarkdown.exe" if os.name == "nt" else "pymarkdown"
    executable = Path(sys.executable).parent / name
    if not executable.is_file():
        discovered = shutil.which("pymarkdown")
        if not discovered:
            print("Install .[dev] to obtain PyMarkdown", file=sys.stderr)
            return 2
        executable = Path(discovered)
    files = [
        path.relative_to(ROOT).as_posix() for path in candidate_files() if path.suffix == ".md"
    ]
    result = subprocess.run(
        [str(executable), "--config", ".pymarkdown.json", "scan", *files], cwd=ROOT, check=False
    )
    if result.returncode == 0:
        print(f"[PASS] Markdown lint: {len(files)} public documentation files")
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
