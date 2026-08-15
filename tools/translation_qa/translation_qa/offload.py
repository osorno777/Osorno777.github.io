from __future__ import annotations

import json
import shutil
from pathlib import Path

QA_FOLDER = "translation_qa"
CACHE_DIRS = (
    "translation_qa/__pycache__",
    "tests/__pycache__",
    ".pytest_cache",
    ".cache",
)


def drive_root(letter: str) -> Path:
    letter = letter.strip().rstrip(":\\/").upper()
    if not letter or len(letter) != 1 or not letter.isalpha():
        raise ValueError(f"Drive letter must be A-Z, got {letter!r}")
    return Path(f"{letter}:/")


def qa_layout(root: Path) -> dict[str, Path]:
    base = root / QA_FOLDER
    return {
        "base": base,
        "reports": base / "reports",
        "tmp": base / "tmp",
        "pycache": base / "pycache",
    }


def prepare_layout(root: Path) -> dict[str, Path]:
    layout = qa_layout(root)
    for key in ("reports", "tmp", "pycache"):
        layout[key].mkdir(parents=True, exist_ok=True)
    return layout


def move_tree(src: Path, dest: Path) -> int:
    """Move files across drives (copy+delete). Skip if src is missing. Keep dest on collision."""
    if not src.exists():
        return 0
    dest.mkdir(parents=True, exist_ok=True)
    moved = 0
    for item in list(src.iterdir()):
        target = dest / item.name
        if item.is_dir():
            moved += move_tree(item, target)
            try:
                item.rmdir()
            except OSError:
                pass
            continue
        if target.exists():
            item.unlink()
            moved += 1
            continue
        shutil.move(str(item), str(target))
        moved += 1
    return moved


def patch_output_dir(paths_json: Path, output_dir: Path) -> None:
    data = json.loads(paths_json.read_text(encoding="utf-8"))
    data["output_dir"] = str(output_dir)
    paths_json.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def offload_work_to_drive(
    root: Path,
    repo_dir: Path,
    *,
    require_root_exists: bool = True,
) -> dict[str, str | int]:
    if require_root_exists and not root.exists():
        raise FileNotFoundError(f"Drive {root} is not available")
    layout = prepare_layout(root)
    moved = move_tree(repo_dir / "reports", layout["reports"])
    for rel in CACHE_DIRS:
        moved += move_tree(repo_dir / rel, layout["pycache"] / rel.replace("/", "_").replace("\\", "_"))
    example = repo_dir / "paths.example.json"
    dest_cfg = repo_dir / "paths.json"
    if example.exists():
        dest_cfg.write_text(example.read_text(encoding="utf-8"), encoding="utf-8")
        patch_output_dir(dest_cfg, layout["reports"])
    elif dest_cfg.exists():
        patch_output_dir(dest_cfg, layout["reports"])
    return {
        "reports": str(layout["reports"]),
        "tmp": str(layout["tmp"]),
        "pycache": str(layout["pycache"]),
        "moved": moved,
    }
