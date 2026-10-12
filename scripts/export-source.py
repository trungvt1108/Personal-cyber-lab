"""Export reviewed Git candidate source without local runtime or VM files."""

from __future__ import annotations

import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.check_repository import candidate_files  # noqa: E402
from scripts.publication_audit import scan_file  # noqa: E402


def main() -> int:
    files = candidate_files()
    if not files or any(scan_file(path) for path in files):
        print("[ABORT] Review scripts/publication_audit.py findings before exporting.")
        return 1
    destination = ROOT / ".generated/personal-cyber-lab-source.zip"
    if (
        destination.parent.is_symlink()
        or destination.is_symlink()
        or not destination.resolve().is_relative_to(ROOT)
    ):
        print("[ABORT] Source archive paths must not be links.")
        return 1
    destination.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            archive.write(path, path.relative_to(ROOT).as_posix())
    print(f"[EXPORTED] .generated/{destination.name}: {len(files)} source files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
