#!/usr/bin/env python3
"""Check module front matter before the site builds.

Keeps the kit navigable as it grows: every CPP id must exist in WP1's data,
`cpps_primary` names 1-3 processes the module mainly teaches (and they must also
be in `cpps`), roles and kinds come from fixed lists.

It reports, it doesn't block: one module with a problem must not stop the whole
site from publishing. In GitHub Actions the findings appear as annotations on the
file. Use --strict to exit 1 on errors (for a local pre-commit check).

Usage: python3 var/check_modules.py [--strict]   (from the repository root)
"""
import json, os, pathlib, sys
import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
CPPS = {c["id"] for c in json.loads((ROOT / "_data/cpps.json").read_text())["cpps"]}
ROLES = {r["id"] for r in yaml.safe_load((ROOT / "_data/roles.yml").read_text())} | {"anyone"}
KINDS = {"tutorial", "how-to", "reference", "explanation"}
MODULE_DIRS = ["getting_started", "researchers", "repository_managers", "rdm_trainers"]
MAX_PRIMARY, MAX_CPPS = 3, 12

errors, warnings = [], []
for d in MODULE_DIRS:
    for f in sorted((ROOT / "pages" / d).glob("*.md")):
        text = f.read_text(encoding="utf-8")
        if not text.startswith("---"):
            errors.append(f"{f}: no front matter"); continue
        fm = yaml.safe_load(text.split("---", 2)[1]) or {}
        rel = f.relative_to(ROOT)
        if not fm.get("title"):
            errors.append(f"{rel}: missing `title`")
        for key in ("kind", "story"):
            if not fm.get(key):
                warnings.append(f"{rel}: no `{key}` yet")
        if fm.get("kind") and fm["kind"] not in KINDS:
            errors.append(f"{rel}: kind `{fm['kind']}` is not one of {sorted(KINDS)}")
        story = fm.get("story") or {}
        if story.get("as", "anyone") not in ROLES:
            errors.append(f"{rel}: story.as `{story.get('as')}` is not one of {sorted(ROLES)}")
        if story and not story.get("want"):
            warnings.append(f"{rel}: story.want is empty")
        if story.get("task") and len(story["task"]) > 45:
            warnings.append(f"{rel}: story.task is long for the home-page picker ({len(story['task'])} chars)")
        cpps = fm.get("cpps") or []
        primary = fm.get("cpps_primary") or []
        for c in cpps + primary:
            if c not in CPPS:
                errors.append(f"{rel}: `{c}` is not a WP1 CPP id")
        if cpps and not primary:
            warnings.append(f"{rel}: has `cpps` but no `cpps_primary`; CPP pages will list it only under 'Also applied in'")
        if len(primary) > MAX_PRIMARY:
            errors.append(f"{rel}: {len(primary)} entries in cpps_primary (max {MAX_PRIMARY}); pick the processes it mainly teaches")
        for c in primary:
            if c not in cpps:
                errors.append(f"{rel}: cpps_primary `{c}` is not also listed in cpps")
        if len(cpps) > MAX_CPPS:
            warnings.append(f"{rel}: {len(cpps)} CPPs; consider splitting the module or keeping only processes it actually applies")

gha = os.environ.get("GITHUB_ACTIONS") == "true"
for level, items in (("warning", warnings), ("error", errors)):
    for msg in items:
        if gha:                                   # annotation on the file; never fails the build
            path, _, text = msg.partition(": ")
            print(f"::warning file={path},title=Module {level}::{text}")
        else:
            print(f"{level}: {msg}")
print(f"{len(errors)} error(s), {len(warnings)} warning(s)")
sys.exit(1 if errors and "--strict" in sys.argv else 0)
