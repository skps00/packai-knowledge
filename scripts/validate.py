#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validate every knowledge file in this repo.

Checks (all deterministic, no network):
  1. every mods/*.json parses;
  2. each file is either a single entry object or {"entries": [...]};
  3. required fields exist (schema/entry.schema.json) — validated with jsonschema
     when available, otherwise a built-in subset check;
  4. every fact carries a non-empty `source` and tier in {A,B,C};
  5. NO duplicate keys: (item, mechanism type, normalized effect text) must be unique
     across the whole repo;
  6. `item` namespace matches the file name (mods/<namespace>.json).

Usage: python scripts/validate.py [repo_root]
Exit code 0 = OK, 1 = problems (printed).
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

TIERS = {"A", "B", "C"}
MECH_KEYS = ("obtain", "use", "worn")
REQUIRED = ("item", "mod", "applies_to", "contributors", "updated")


def norm(text: str) -> str:
    """Normalize effect text so cosmetic differences do not look like separate facts."""
    t = (text or "").lower()
    t = re.sub(r"[^a-z0-9\u4e00-\u9fff]+", " ", t)
    return " ".join(t.split())


def fact_key(item: str, mech: str, fact: dict) -> str:
    bits = [
        norm(str(fact.get("trigger", ""))),
        norm(str(fact.get("effect", ""))),
        norm(" ".join(map(str, fact.get("effects", []) or []))),
        norm(str(fact.get("type", ""))),
        norm(str(fact.get("mob", ""))),
        norm(str(fact.get("container", ""))),
    ]
    return f"{item}|{mech}|" + "|".join(b for b in bits if b)


def load_entries(path: Path):
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict) and "entries" in data:
        return list(data["entries"])
    if isinstance(data, list):
        return list(data)
    return [data]


def subset_check(entry: dict, problems: list[str], where: str) -> None:
    for field in REQUIRED:
        if field not in entry:
            problems.append(f"{where}: missing required field '{field}'")
    if not isinstance(entry.get("contributors"), list) or not entry.get("contributors"):
        problems.append(f"{where}: 'contributors' must be a non-empty list")
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", str(entry.get("updated", ""))):
        problems.append(f"{where}: 'updated' must be YYYY-MM-DD")
    if not re.match(r"^[a-z0-9_.-]+:[a-z0-9_./-]+$", str(entry.get("item", ""))):
        problems.append(f"{where}: 'item' must be 'namespace:path'")
    applies = entry.get("applies_to") or {}
    if "mc" not in applies:
        problems.append(f"{where}: 'applies_to.mc' is required")
    for mech in MECH_KEYS:
        for i, fact in enumerate(entry.get(mech) or []):
            if not isinstance(fact, dict):
                problems.append(f"{where}: {mech}[{i}] is not an object")
                continue
            if not str(fact.get("source", "")).strip():
                problems.append(f"{where}: {mech}[{i}] missing 'source'")
            if fact.get("tier") not in TIERS:
                problems.append(f"{where}: {mech}[{i}] tier must be A/B/C")


def main() -> int:
    root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent
    problems: list[str] = []
    seen: dict[str, str] = {}
    files = sorted((root / "mods").glob("*.json")) if (root / "mods").is_dir() else []
    if not files:
        print("OK (no entries yet)")
        return 0

    schema = None
    try:  # optional dependency; subset check runs regardless
        import jsonschema  # type: ignore

        schema = json.loads((root / "schema" / "entry.schema.json").read_text(encoding="utf-8"))
    except Exception:
        schema = None

    for path in files:
        ns = path.stem
        try:
            entries = load_entries(path)
        except Exception as exc:
            problems.append(f"{path.name}: not valid JSON ({exc})")
            continue
        for idx, entry in enumerate(entries):
            where = f"{path.name}[{idx}]"
            if not isinstance(entry, dict):
                problems.append(f"{where}: entry must be an object")
                continue
            if schema is not None:
                try:
                    import jsonschema  # type: ignore

                    jsonschema.validate(entry, schema)
                except Exception as exc:
                    problems.append(f"{where}: schema error: {getattr(exc, 'message', exc)}")
            subset_check(entry, problems, where)
            item = str(entry.get("item", ""))
            if item and not item.startswith(ns + ":"):
                problems.append(f"{where}: item namespace '{item}' != file '{path.name}'")
            for mech in MECH_KEYS:
                for fact in entry.get(mech) or []:
                    if not isinstance(fact, dict):
                        continue
                    key = fact_key(item, mech, fact)
                    if key in seen:
                        problems.append(f"DUPLICATE fact key: {key} (also in {seen[key]})")
                    else:
                        seen[key] = where

    if problems:
        print(f"FAILED ({len(problems)} problem(s)):")
        for p in problems:
            print("  -", p)
        return 1
    print(f"OK ({len(files)} file(s), {len(seen)} fact key(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
