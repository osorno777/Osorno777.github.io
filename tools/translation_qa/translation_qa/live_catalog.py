"""Resolve which physical file the Alertness Books storefront actually serves.

Live map: bookstore/public/store_catalog.json (also https://alertnessbooks.com/store_catalog.json).
Each row is slug + lang + status. Delivery files are conventionally
{slug}_{lang}.html under /admin/translations/private/ or fulfillment/_out.
kdp_by_isbn, _staging, and dated _live_* snapshots are not the storefront.
This module only locates files. It does not publish, unpublish, or rewrite them.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

_PATH_IN_JSON = re.compile(r"(?i)[^\s\"']+\.(?:html?|xhtml|epub|pdf)$")
_ISBN_KEY = re.compile(r"(?i)isbn")
_FILE_KEY = re.compile(r"(?i)^(file|path|href|html|epub|pdf|src|filename|private|master)$")
_BOOK_SUFFIXES = {".html", ".htm", ".xhtml", ".epub", ".pdf"}


def artefact_lane(path: Path) -> str:
    blob = str(path).lower().replace("\\", "/")
    if "/_live_" in blob or blob.split("/")[-1].startswith("_live_"):
        return "snapshot-not-storefront"
    if "translations/private" in blob:
        return "live-storefront"
    if "bookstore/public/" in blob and path.name.lower() == "store_catalog.json":
        return "live-catalog"
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
    wanted = {name.lower() for name in _wanted_names(payload)}
    found: list[Path] = []
    seen: set[str] = set()
    if wanted:
        for root in roots:
            if not root.is_dir():
                continue
            for path in root.rglob("*"):
                if path.suffix.lower() not in _BOOK_SUFFIXES:
                    continue
                if path.name.lower() not in wanted:
                    continue
                blob = str(path).lower().replace("\\", "/")
                if "/_live_" in blob:
                    continue
                key = str(path).lower()
                if key in seen:
                    continue
                seen.add(key)
                found.append(path)
    for value in _walk_strings(payload):
        for path in _paths_from_string(value, roots):
            key = str(path).lower()
            if key in seen:
                continue
            seen.add(key)
            found.append(path)
    return found


def _wanted_names(payload: object) -> list[str]:
    names: list[str] = []
    rows = payload if isinstance(payload, list) else []
    if isinstance(payload, dict):
        for key in ("items", "books", "skus", "catalog"):
            if isinstance(payload.get(key), list):
                rows = payload[key]
                break
    for row in rows:
        if not isinstance(row, dict):
            continue
        slug = str(row.get("slug") or "").strip()
        lang = str(row.get("lang") or "").strip()
        if not slug:
            continue
        slug_l = slug.lower()
        lang_l = lang.lower()
        already = bool(lang_l) and (
            slug_l.endswith("_" + lang_l) or slug_l.endswith("-" + lang_l)
        )
        stems = [slug]
        if lang and not already:
            stems.append(f"{slug}_{lang}")
        for stem in stems:
            for suffix in (".html", ".htm", ".xhtml", ".epub", ".pdf"):
                names.append(stem + suffix)
        master = row.get("master")
        if isinstance(master, str) and master.strip():
            names.append(Path(master.replace("\\", "/")).name)
    return names


def _catalog_files(config: dict) -> list[Path]:
    files: list[Path] = []
    seen: set[str] = set()
    raw = config.get("store_catalog")
    items = raw if isinstance(raw, list) else [raw] if raw else []
    extra = [
        Path("C:/Alertness AI/bookstore/public/store_catalog.json"),
        Path("C:/Alertness AI/bookstore/store_catalog.json"),
        Path("C:/Alertness AI/bookstore/data/store_catalog.json"),
        Path("C:/Alertness AI/bookstore/admin/translations/store_catalog.json"),
    ]
    for item in list(items) + [str(path) for path in extra]:
        path = Path(item)
        marker = str(path).lower().replace("\\", "/")
        if marker in seen:
            continue
        if "/_live_" in marker:
            continue
        seen.add(marker)
        files.append(path)
    folders = []
    for key in ("translations_dirs", "translations_dir"):
        value = config.get(key)
        folders.extend(value if isinstance(value, list) else [value] if value else [])
    for folder in [Path(item) for item in folders]:
        for candidate in (
            folder if folder.suffix.lower() == ".json" else None,
            folder / "store_catalog.json" if folder.suffix.lower() != ".json" else None,
            folder / "public" / "store_catalog.json" if folder.suffix.lower() != ".json" else None,
            folder.parent / "store_catalog.json",
            folder.parent / "public" / "store_catalog.json",
        ):
            if candidate is None:
                continue
            marker = str(candidate).lower().replace("\\", "/")
            if marker in seen or "/_live_" in marker:
                continue
            seen.add(marker)
            files.append(candidate)
    return [path for path in files if path.is_file()]


def _search_roots(catalog: Path) -> list[Path]:
    parent = catalog.parent
    bookstore = parent.parent if parent.name.lower() == "public" else parent
    return [
        bookstore / "admin" / "translations" / "private",
        bookstore / "fulfillment" / "_out",
        bookstore / "btw_rerender",
        bookstore / "data",
        parent,
        bookstore,
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
    matches = _PATH_IN_JSON.findall(value)
    if not matches and _PATH_IN_JSON.search(value):
        matches = [value]
    for match in matches:
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
