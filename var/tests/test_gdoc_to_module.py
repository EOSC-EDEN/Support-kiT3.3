#!/usr/bin/env python3
"""Regression checks for var/gdoc_to_module.py against real Google Docs Markdown exports.

The fixtures are actual Google Docs exports of the template and example Docs (v1, v2 and
the v3 plain table), plus a copy with deliberately messy values. Run from the repository root:  python3 var/tests/test_gdoc_to_module.py
"""
import pathlib, subprocess, sys, yaml

ROOT = pathlib.Path(__file__).resolve().parents[2]
FIX = ROOT / "var/tests/fixtures"


def convert(name):
    r = subprocess.run([sys.executable, str(ROOT / "var/gdoc_to_module.py"), str(FIX / name), "--stdout"],
                       capture_output=True, text=True, cwd=ROOT)
    page = r.stdout[r.stdout.find("---\n"):] if "---\n" in r.stdout else ""
    fm = yaml.safe_load(page.split("---", 2)[1]) if page else None
    return r.returncode, fm, page, r.stdout


fails = 0
def check(label, cond):
    global fails
    print(("ok   " if cond else "FAIL ") + label)
    fails += 0 if cond else 1


code, fm, page, _ = convert("v1_example_preparing_deposits.md")
check("v1 example converts", code == 0 and fm)
check("v1 example: role, kind, primaries", fm["story"]["as"] == "researcher" and fm["kind"] == "how-to"
      and fm["cpps_primary"] == ["CPP-010", "CPP-001"])
check("v1 example: recommendations become a checklist", "- [ ] Check and follow" in page)
check("v1 example: no quote-prefixed lists or escapes left", "> *" not in page and "\\_" not in page)

code, fm, page, out = convert("v1_messy_values.md")
check("messy values convert (warnings, no error)", code == 0 and "error:" not in out)
check("messy: role/kind/order/status read", fm["story"]["as"] == "manager" and fm["kind"] == "how-to"
      and fm["order"] == 2 and fm["status"] == "ready")
check("messy: names matched to CPPs, 4th primary kept as applied",
      fm["cpps_primary"] == ["CPP-010", "CPP-002", "CPP-007"] and "CPP-011" in fm["cpps"])
check("messy: frameworks parsed", {"framework": "cts-2026", "code": "R09"} in fm["satisfies"]
      and {"framework": "iso-16363", "code": "4.2"} in fm["satisfies"])

for name in ("v1_template_empty.md", "v2_template_empty.md", "v3_template_empty.md"):
    code, fm, page, out = convert(name)
    check(f"{name}: blocked only for the missing title", code == 1 and out.count("error:") == 1 and "Title is empty" in out)

code, fm, page, out = convert("v2_filled_dropdowns.md")
check("v2 filled converts", code == 0 and fm)
check("v2: dropdown processes merged", fm["cpps_primary"] == ["CPP-008", "CPP-010"])
check("v2: template-only sections and guidance dropped", "## Considerations" not in page and "One action per bullet" not in page)

code, fm, page, out = convert("v3_filled.md")
check("v3 filled converts", code == 0 and fm)
check("v3: role and kind in plain words", fm["story"]["as"] == "manager" and fm["kind"] == "how-to")
check("v3: one 'Main processes' row, names and numbers", fm["cpps_primary"] == ["CPP-008", "CPP-010"])
check("v3: other processes and frameworks read", "CPP-007" in fm["cpps"]
      and {"framework": "cts-2026", "code": "R14"} in fm["satisfies"])
check("v3: escaped dots removed inside URLs", "<https://www.nationalarchives.gov.uk/PRONOM/>" in page)
check("v3: rows left out get defaults", fm["disciplines"] == ["all"] and "order" not in fm and fm["status"] == "ready")

code, fm, page, out = convert("v3_template_styled_filled.md")
check("v3 styled template: bold labels read", code == 0 and fm["story"]["as"] == "manager"
      and fm["cpps_primary"] == ["CPP-008", "CPP-010"])
check("v3 styled template: italic guidance line dropped", "One action per bullet" not in page)
check("v3 styled template: 'everything below this line' note dropped", "Everything below this line" not in page)

code, fm, page, out = convert("v3_extra_content.md")
check("extra content: converts", code == 0 and fm["kind"] == "tutorial")
check("extra content: paragraphs stay separate", "named link](https://www.nationalarchives.gov.uk/PRONOM/).\n\nSecond opening" in page)
check("extra content: own sections, sub-headings and a section after More information kept",
      all(h in page for h in ("## Before you start", "### Tools that help", "## Steps", "## Glossary")))
check("extra content: numbered and nested lists, tables kept", "1. Run DROID on the folder." in page
      and "  - Nested point about PDF/A." in page and "| DROID | Identifies formats |" in page)
check("extra content: only Recommendations bullets become a checklist", "- [ ] Identify every file." in page
      and "- [ ] DROID" not in page and "- [ ] Which formats" not in page)

# The workflow passes the Doc list between jobs; GitHub drops outputs that contain part of a
# secret (a multi-line JSON key makes "{" secret), so the list must be plain IDs, no braces.
import os
r = subprocess.run([sys.executable, str(ROOT / "var/gdocs_sync.py"), "list"], capture_output=True, text=True, cwd=ROOT,
                   env={**os.environ, "GDRIVE_SA_KEY": "", "DOC_INPUT": "https://docs.google.com/document/d/1uovzhpRg4qmZ_cuc4yztmXPzBpFgJrXjzitlbYrad1U/edit?tab=t.0"})
check("gdocs_sync list: plain ID list, no braces", r.stdout.strip() == 'docs=["1uovzhpRg4qmZ_cuc4yztmXPzBpFgJrXjzitlbYrad1U"]')

# Anchored Doc comments: which row a converter message is about, and where that text sits
# in the real Doc structure (a documents.get read of a filled v3 template copy).
sys.path.insert(0, str(ROOT / "var"))
import gdocs_sync as g
import json as _json
doc = _json.loads((FIX / "v3_doc_structure.json").read_text())
check("anchor: contributor message -> exact name in the Contributors cell",
      g.locate(doc, *g.row_for("Contributor `Arijit Laik` is not in _data/CONTRIBUTORS.yml yet; add them with their ORCID")) == ("t.0", 2371, 2382))
w = g.locate(doc, {"title"})
check("anchor: summary comment -> the Title value", w and w[2] - w[1] == len("Creating checksums before deposit"))
w = g.locate(doc, *g.row_for("'Other processes': read `integrity checking` as CPP-003 Integrity Checking; check this is right"))
check("anchor: process message -> the words in the Other processes cell", w and w[2] - w[1] == len("integrity checking"))
w = g.locate(doc, *g.row_for("Framework `nestro` not recognised; left out"))
check("anchor: word not found -> whole Frameworks value", w and w[2] - w[1] == len("CoreTrustSeal R14"))
check("anchor: messages that name no row are not anchored",
      g.row_for("3 line(s) of the content were still template text and were left out") is None)

print(f"\n{fails} failure(s)")
sys.exit(1 if fails else 0)
