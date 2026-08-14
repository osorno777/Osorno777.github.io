"""Resolve which physical file the Alertness Books storefront actually serves.

The live path is store_catalog.json -> /admin/translations/private/.
kdp_by_isbn and _staging are other artefacts; they are not the storefront.
This module only locates files. It does not publish, unpublish, or rewrite them.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

_PATH_IN_JSON = re.compile(r"(?i)[^\s\"']+\.(?:html?|xhtml|epub|pdf)$")
_ISBN_KEY = re.compile(r"(?i)isbn")
_FILE_KEY = re.compile(r"(?i)^(file|path|href|html|epub|pdf|src|filename|private)$")


def artefact_lane(path: Path) -> str:
    blob = str(path).lower().replace("\\", "/")
    if "translations/private" in blob:
        return "live-storefront"
    if "fulfillment/_out" in blob:
        return "rebuild-not-storefront"
    if "kdp_by_isbn" in blob:
        return "kdp-not-storefront"
    if "_staging" in blob:
        return "staging-not-storefront"
    return ""


def live_translation_paths(config: dict) -> list[Path]:
    """Return book files named by store_catalog.json, if that file exists locally."""
    catalogs = _catalog_files(config)
    found: list[Path] = []
    seen: set[str] = set()
    for catalog in catalogs:
        for path in parse_store_catalog(catalog):
            key = str(path).lower()
            if key in seen:
                continue
            seen.add(key)
            found.append(path)
    return found


def parse_store_catalog(catalog: Path) -> list[Path]:
    try:
        payload = json.loads(catalog.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return []
    roots = _search_roots(catalog)
    found: list[Path] = []
    seen: set[str] = set()
    for value in _walk_strings(payload):
        for path in _paths_from_string(value, roots):
            key = str(path).lower()
            if key in seen:
                continue
            seen.add(key)
            found.append(path)
    return found


def _catalog_files(config: dict) -> list[Path]:
    files: list[Path] = []
    seen: set[str] = set()
    raw = config.get("store_catalog")
    items = raw if isinstance(raw, list) else [raw] if raw else []
    for item in items:
        path = Path(item)
        marker = str(path).lower()
        if marker in seen:
            continue
        seen.add(marker)
        files.append(path)
    folders = []
    for key in ("translations_dirs", "translations_dir"):
        value = config.get(key)
        folders.extend(value if isinstance(value, list) else [value] if value else [])
    extra = [
        Path("C:/Alertness AI/bookstore/store_catalog.json"),
        Path("C:/Alertness AI/bookstore/data/store_catalog.json"),
        Path("C:/Alertness AI/bookstore/admin/translations/store_catalog.json"),
    ]
    for folder in [Path(item) for item in folders] + extra:
        for candidate in (
            folder if folder.suffix.lower() == ".json" else None,
            folder / "store_catalog.json" if folder.suffix.lower() != ".json" else None,
            folder.parent / "store_catalog.json",
        ):
            if candidate is None:
                continue
            marker = str(candidate).lower()
            if marker in seen:
                continue
            seen.add(marker)
            files.append(candidate)
    return [path for path in files if path.is_file()]


def _search_roots(catalog: Path) -> list[Path]:
    parent = catalog.parent
    return [
        parent,
        parent / "admin" / "translations" / "private",
        parent / "translations" / "private",
        parent.parent / "admin" / "translations" / "private",
        parent / "data",
    ]


def _walk_strings(node: object) -> list[str]:
    values: list[str] = []
    if isinstance(node, dict):
        for key, value in node.items():
            if isinstance(value, str) and (_FILE_KEY.search(str(key)) or _ISBN_KEY.search(str(key))):
                values.append(value)
            values.extend(_walk_strings(value))
    elif isinstance(node, list):
        for item in node:
            values.extend(_walk_strings(item))
    elif isinstance(node, str):
        values.append(node)
    return values


def _paths_from_string(value: str, roots: list[Path]) -> list[Path]:
    found: list[Path] = []
    for match in _PATH_IN_JSON.findall(value) or ([value] if _PATH_IN_JSON.search(value) else []):
        raw = match.replace("\\", "/").lstrip("/")
        if "/admin/translations/private/" in raw:
            raw = raw.split("/admin/translations/private/", 1)[1]
        name = Path(raw).name
        candidates = [Path(raw)] if Path(raw).is_absolute() else []
        for root in roots:
            candidates.append(root / raw)
            candidates.append(root / name)
        for path in candidates:
            try:
                if path.is_file():
                    found.append(path)
            except OSError:
                continue
    return found
