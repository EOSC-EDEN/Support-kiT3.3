#!/usr/bin/env python3
"""Mirror WP1's Core Preservation Processes into _data/cpps.json and pages/cpps/.

Source: https://github.com/EOSC-EDEN/wp1-cpp-descriptions, one XML file per CPP.
WP3 never edits CPP content; changes go upstream to WP1.

  python3 var/sync_cpps.py                    shallow-clones WP1 into a temp dir
  python3 var/sync_cpps.py /path/to/wp1       uses an existing checkout
  python3 var/sync_cpps.py --summary FILE     also writes a Markdown change summary (for the PR body)

Writes _data/cpps.json, then regenerates the CPP stub pages (var/make_cpp_pages.py).
Exits 1 only when the WP1 data can't be read; changes that affect modules are reported.
"""
import argparse, json, re, subprocess, sys, tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "_data/cpps.json"
UPSTREAM = "https://github.com/EOSC-EDEN/wp1-cpp-descriptions"
SITE = "https://eosc-eden.github.io/wp1-cpp-descriptions"
DOI = "10.5281/zenodo.16992452"
NS = {"cpp": "https://eden-fidelis.eu/cpp/cpp/"}
# Sections that say what the process is about; joined into `text` for search and anchor suggestions.
TEXT_PARTS = ["cpp:descriptionAndScope", ".//cpp:purpose", ".//cpp:inputs", ".//cpp:outputs"]


def txt(el, sep="; "):
    """Plain text of an element; adjacent <span>/<p>/<li> blocks joined with `sep`, whitespace collapsed."""
    if el is None:
        return ""
    t = re.sub(r"\s+", " ", _flat(el, sep))
    t = re.sub(r"([.;:!?])\s*;", r"\1", t)  # no "; " after a sentence that already ends
    return re.sub(r"\s+([,.;:)])", r"\1", t).replace("( ", "(").strip()


def _flat(el, sep):
    out, prev_block = [el.text or ""], False
    for c in el:
        block = c.tag.split("}")[-1] in ("span", "p", "li")
        out += [sep if block and prev_block else " " if block else "", _flat(c, sep), c.tail or ""]
        prev_block = block and not (c.tail or "").strip()
    return "".join(out)


def parse(path):
    root = ET.parse(path).getroot()
    cid = root.get("ID")
    if not re.fullmatch(r"CPP-\d{3}", cid or ""):
        raise ValueError(f"{path}: no CPP-### ID attribute")
    f = lambda q: txt(root.find(q, NS))
    versions = root.findall(".//cpp:history/cpp:version", NS)
    latest = versions[-1] if versions else None
    number = ".".join(txt(latest.find(f".//cpp:{p}Version", NS)) or "0" for p in ("major", "minor", "patch")) if latest is not None else None
    return {
        "id": cid,
        "label": f(".//cpp:label"),
        "shortDefinition": f(".//cpp:shortDefinition"),
        "oais": f(".//cpp:oaisClassification"),
        "logical": f(".//cpp:logicalClassification"),
        "version": number,
        "versionDate": txt(latest.find("cpp:versionDate", NS)) if latest is not None else None,
        "url": f"{SITE}/{cid.lower()}.html",
        "relationships": [
            {"type": txt(r.find("cpp:relationshipType", NS)), "cpp": txt(r.find("cpp:relatedCPP", NS))}
            for r in root.iterfind(".//cpp:cppRelationships/cpp:relationship", NS)
            if re.fullmatch(r"CPP-\d{3}", txt(r.find("cpp:relatedCPP", NS)))
        ],
        "mappings": [
            {"framework": txt(m.find("cpp:frameworkName", NS)),
             "term": txt(m.find("cpp:correspondingTerm", NS)),
             "section": txt(m.find("cpp:correspondingSection", NS))}
            for m in root.iterfind(".//cpp:mapping", NS)
        ],
        "text": " ".join(txt(e, " ") for q in TEXT_PARTS for e in root.findall(q, NS)),
    }


def module_refs():
    """{CPP id: [module files that tag it]}, read without a YAML dependency."""
    refs = {}
    for p in sorted((ROOT / "pages").rglob("*.md")):
        if p.parent.name == "cpps":
            continue
        head = p.read_text(encoding="utf-8").split("---")[1:2]
        for cid in set(re.findall(r"CPP-\d{3}", head[0] if head else "")):
            refs.setdefault(cid, []).append(str(p.relative_to(ROOT)))
    return refs


def summarise(old, new):
    """Markdown list of what changed between two cpps.json payloads; empty if nothing did."""
    o = {c["id"]: c for c in old.get("cpps", [])}
    n = {c["id"]: c for c in new["cpps"]}
    refs = module_refs()
    lines = []
    for cid in sorted(n.keys() - o.keys()):
        lines.append(f"- **New:** {cid} {n[cid]['label']}")
    for cid in sorted(o.keys() - n.keys()):
        used = refs.get(cid, [])
        lines.append(f"- **Removed:** {cid} {o[cid]['label']}" + (f" ⚠ still tagged in {', '.join(used)}" if used else ""))
    for cid in sorted(o.keys() & n.keys()):
        a, b = o[cid], n[cid]
        if a == b:
            continue
        what = [k for k in b if a.get(k) != b[k]]
        bits = []
        if "label" in what:
            bits.append(f"renamed from “{a['label']}”")
        if "version" in what:
            bits.append(f"version {a.get('version')} → {b['version']}")
        rest = [k for k in what if k not in ("label", "version", "versionDate")]
        if rest:
            bits.append("changed: " + ", ".join(rest))
        used = refs.get(cid, [])
        lines.append(f"- {cid} {b['label']}: {'; '.join(bits) or 'updated'}" + (f" (tagged in {len(used)} module{'s' * (len(used) != 1)})" if used else ""))
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("wp1", nargs="?", help="local checkout of wp1-cpp-descriptions (default: clone it)")
    ap.add_argument("--summary", type=Path, help="write a Markdown change summary here")
    args = ap.parse_args()

    with tempfile.TemporaryDirectory() as tmp:
        src = Path(args.wp1) if args.wp1 else Path(tmp)
        if not args.wp1:
            subprocess.run(["git", "clone", "--quiet", "--depth", "1", UPSTREAM, tmp], check=True)
        try:
            commit = subprocess.run(["git", "-C", src, "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
        except subprocess.CalledProcessError:
            commit = None
        files = sorted(src.glob("CPP-[0-9][0-9][0-9]/cpp-[0-9][0-9][0-9].xml"))
        if not files:
            sys.exit(f"sync_cpps: no CPP-###/cpp-###.xml files in {src}")
        cpps = [parse(p) for p in files]

    new = {
        "source": {"repo": UPSTREAM, "commit": commit, "site": f"{SITE}/", "doi": DOI},
        "note": "Generated by var/sync_cpps.py from WP1. Do not edit by hand; change CPPs upstream. "
                "`text` holds the plain text of descriptionAndScope, purpose, inputs and outputs, "
                "for search and anchor suggestions.",
        "cpps": cpps,
    }
    old = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else {}
    if old.get("cpps") == cpps:
        print(f"No CPP changes in WP1 {(commit or str(src))[:7]}; {OUT.relative_to(ROOT)} left as is.")
        if args.summary:
            args.summary.write_text("No CPP changes.", encoding="utf-8")
        return
    OUT.write_text(json.dumps(new, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    subprocess.run([sys.executable, ROOT / "var/make_cpp_pages.py"], check=True)

    changes = summarise(old, new)
    print(f"Wrote {OUT.relative_to(ROOT)}: {len(cpps)} CPPs from {(commit or str(src))[:7]}")
    print(changes or "No CPP content changes.")
    if args.summary:
        prev = (old.get("source") or {}).get("commit") or "?"
        args.summary.write_text(
            f"WP1 [`{prev[:7]}`…`{(commit or '?')[:7]}`]({UPSTREAM}/compare/{prev}...{commit})\n\n"
            + changes, encoding="utf-8")


if __name__ == "__main__":
    main()
