#!/usr/bin/env python3
"""Build one zip for each skill folder, for the claude.ai "Upload skill" step.

Each zip holds one folder with the skill name, and SKILL.md is in that folder:
`dist/joey.zip` holds `joey/SKILL.md` and `joey/references/...`.

The output is deterministic: the same files give the same bytes. The script
sorts the files, and it sets one fixed time, fixed permissions and one
compression level on each entry.

Usage: python3 -I scripts/build_skill_zips.py [--out DIR]
"""

from __future__ import annotations

import argparse
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO_ROOT / "skills"
FIXED_TIME = (1980, 1, 1, 0, 0, 0)
COMPRESS_LEVEL = 9
FILE_MODE = 0o100644
UNIX_SYSTEM = 3
IGNORED_NAMES = {".DS_Store", "__pycache__"}


def skill_dirs() -> list[Path]:
    """Give the skill folders, sorted by name."""
    return sorted(path for path in SKILLS_DIR.iterdir() if path.is_dir())


def skill_files(skill_dir: Path) -> list[Path]:
    """Give the files of one skill, sorted by their path in the skill."""
    files: list[Path] = []
    for path in skill_dir.rglob("*"):
        if IGNORED_NAMES.intersection(path.relative_to(skill_dir).parts):
            continue
        if path.is_symlink():
            raise SystemExit(f"A skill must not contain a symlink: {path}")
        if path.is_file():
            files.append(path)
    return sorted(files, key=lambda path: path.relative_to(skill_dir).as_posix())


def build_zip(skill_dir: Path, out_dir: Path) -> Path:
    """Write `<out_dir>/<skill>.zip` and give its path."""
    if not (skill_dir / "SKILL.md").is_file():
        raise SystemExit(f"The skill has no SKILL.md: {skill_dir}")
    target = out_dir / f"{skill_dir.name}.zip"
    with zipfile.ZipFile(target, "w") as archive:
        for path in skill_files(skill_dir):
            name = f"{skill_dir.name}/{path.relative_to(skill_dir).as_posix()}"
            info = zipfile.ZipInfo(name, date_time=FIXED_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = UNIX_SYSTEM
            info.external_attr = FILE_MODE << 16
            archive.writestr(info, path.read_bytes(), compresslevel=COMPRESS_LEVEL)
    return target


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--out",
        type=Path,
        default=REPO_ROOT / "dist",
        help="the folder for the zips (default: dist/)",
    )
    out_dir = parser.parse_args().out.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    for skill_dir in skill_dirs():
        print(build_zip(skill_dir, out_dir))


if __name__ == "__main__":
    main()
