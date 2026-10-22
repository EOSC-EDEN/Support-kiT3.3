#!/usr/bin/env python3
"""Turn a module written in the Google Docs template into a support-kit page.

Authors write in the "EDEN Support-kit – module template" Google Doc and export it
with File > Download > Markdown (.md). This script reads that export and writes
pages/<role folder>/<page_id>.md with the YAML front matter the site expects.
The sidebar is rebuilt from the pages by var/make_sidebar.py, so it is not edited here.
Most authors never run this by hand: the "Google Docs to pull request" workflow does.

It reads:
  - the table under the "Module metadata" heading (first two columns: field, value)
  - everything under the "Module content" heading, as the page body

and cleans up what Google's export adds: bold on headings, lists exported as
quotes, backslash escapes, bare URLs, images as inline data. Bullets under a
"Recommendations" (or "Checklist") heading become tickable checklist items.

Usage (from the repository root):
  python3 var/gdoc_to_module.py my-module.md            write the page
  python3 var/gdoc_to_module.py my-module.md --stdout   print the page instead
  python3 var/gdoc_to_module.py my-module.md --force    overwrite an existing page

Exits 1 only when no page can be made (no title, or the template headings are gone).
Everything else is a warning, listed for the reviewer, with a sensible default.
"""
import argparse, base64, difflib, json, pathlib, re, sys
import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent

# Template labels (and plain YAML keys, for people who prefer them) -> field
LABELS = {
    "title": "title", "description": "description",
    "role": "as", "who is it for": "as", "as a": "as", "as": "as",
    "i want to": "want", "want": "want",
    "so that": "so_that", "so_that": "so_that",
    "short task": "task", "task": "task",
    "kind of help": "kind", "kind": "kind",
    "order in the role path": "order", "order": "order",
    "disciplines": "disciplines", "data types": "data_types", "data_types": "data_types",
    "keywords": "keywords",
    "main processes": "cpps_primary", "processes it mainly teaches": "cpps_primary", "cpps_primary": "cpps_primary",
    "other processes": "cpps_other", "other processes it applies": "cpps_other", "cpps": "cpps_other",
    "frameworks": "satisfies", "frameworks cited": "satisfies", "satisfies": "satisfies",
    "related modules": "related", "related_pages": "related",
    "contributors": "contributors", "status": "status",
    "file name": "page_id", "page_id": "page_id",
    "effort": "effort", "time needed": "effort",
}
NAMES = {"title": "Title", "description": "Description", "disciplines": "Disciplines", "keywords": "Keywords",
         "contributors": "Contributors", "status": "Status", "effort": "Time needed", "as": "Who is it for", "want": "I want to", "so_that": "So that", "task": "Short task", "kind": "Kind of help",
         "order": "Order in the role path", "cpps_primary": "Main processes",
         "cpps_other": "Other processes", "satisfies": "Frameworks",
         "related": "Related modules", "data_types": "Data types", "page_id": "File name"}
ROLE_WORDS = {"researcher": "researcher", "researchers": "researcher", "depositor": "researcher",
              "manager": "manager", "repository manager": "manager", "repository managers": "manager",
              "trainer": "trainer", "rdm trainer": "trainer", "rdm trainers": "trainer",
              "anyone": "anyone", "everyone": "anyone", "all": "anyone", "every role": "anyone"}
KINDS = {"how-to": "how-to", "how to": "how-to", "get it done": "how-to",
         "tutorial": "tutorial", "learn by doing": "tutorial",
         "reference": "reference", "look it up": "reference",
         "explanation": "explanation", "understand why": "explanation"}
# Guidance sentences printed in the template body; never part of a module page.
TEMPLATE_GUIDANCE = {
    "one action per bullet, starting with a verb. on the website these become a checklist readers can tick.",
}
CHECKLIST_HEADINGS = re.compile(r"recommendation|checklist|to do|steps", re.I)

errors, warnings = [], []


def unescape(s):
    """Undo Google's backslash escapes in a metadata value."""
    return re.sub(r"\\([\\`*_{}\[\]()#+\-.!:|>~<\"'=$&])", r"\1", s)


def clean_value(s):
    s = unescape(s).strip()
    s = re.sub(r"\*\*(.*?)\*\*", r"\1", s)          # bold
    s = re.sub(r"(?<!\w)\*(.*?)\*(?!\w)", r"\1", s)  # italics
    s = re.sub(r"<br\s*/?>", " ", s)
    s = re.sub(r"\[([^\]]+)\]\((?:mailto:)?[^)]*\)", r"\1", s)   # chips and links -> their text
    return s.strip()


def is_placeholder(s):
    return bool(re.fullmatch(r"\[.*\]", s.strip()))


def split_list(s):
    return [x.strip() for x in re.split(r"[,;\n]", s) if x.strip()]


def load_cpps():
    return json.loads((ROOT / "_data/cpps.json").read_text())["cpps"]


def cpp_ids(s, field, cpps):
    """CPP ids from what an author typed: 'CPP-010', '10', 'cpp 10', or the process name."""
    labels = {c["label"].lower(): c["id"] for c in cpps}
    valid = {c["id"] for c in cpps}
    out = []
    for part in split_list(s):
        m = re.search(r"(?:cpp[\s\-_]*)?(\d{1,3})", part, re.I)
        if m:
            cid = f"CPP-{int(m.group(1)):03d}"
            if cid in valid:
                out.append(cid)
            else:
                warnings.append(f"'{field}': `{part}` is not one of WP1's 30 processes; left out")
            continue
        name = part.lower().strip()
        hit = labels.get(name) or next((v for k, v in labels.items() if name in k or k in name), None)
        if not hit:
            close = difflib.get_close_matches(name, labels.keys(), n=1, cutoff=0.75)
            hit = labels[close[0]] if close else None
        if hit:
            out.append(hit)
            if name not in labels:
                warnings.append(f"'{field}': read `{part}` as {hit} {next(c['label'] for c in cpps if c['id'] == hit)}; check this is right")
        else:
            warnings.append(f"'{field}': no process matches `{part}`; left out (use the name or number from the WP1 list)")
    return list(dict.fromkeys(out))


def pick(value, table, default=None):
    """First option whose keywords appear in what the author wrote (a word, a phrase, or v2 dropdown text)."""
    v = re.sub(r"[^a-z0-9 ]", " ", value.lower())
    for key, words in table:
        if any(re.search(rf"\b{w}", v) for w in words):
            return key
    return default


ROLE_PICK = [("anyone", ["any", "every", "all roles", "all"]),
             ("trainer", ["train", "teach", "educat", "instruct"]),
             ("manager", ["manag", "curat", "repositor", "archiv", "steward", "operator"]),
             ("researcher", ["research", "depositor", "scientist", "phd", "pi\\b", "principal"])]
KIND_PICK = [("how-to", ["how", "get it done", "guide", "steps"]),
             ("tutorial", ["tutorial", "learn", "walkthrough"]),
             ("reference", ["reference", "look it up", "list", "checklist", "lookup"]),
             ("explanation", ["explan", "understand", "why", "background", "concept"])]
FW_PICK = [("cts-2023", ["cts 2023", "coretrustseal 2023", "2023 2025"]),
           ("cts-2026", ["cts", "coretrustseal", "core trust seal"]),
           ("nestor", ["nestor", "din"]),
           ("iso-16363", ["iso", "16363", "tdr checklist"]),
           ("oais", ["oais", "14721"]),
           ("premis", ["premis"]),
           ("eosc-tf-fm", ["eosc", "fair", "tf fm", "metrics"])]


def slug(title):
    s = re.sub(r"[–—].*$", "", title)                # drop a subtitle after a dash
    s = re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")
    return s[:48].rstrip("_") or "untitled_module"


def find_heading(lines, name):
    pat = re.compile(r"^#{1,6}\s*\**\s*" + re.escape(name) + r"\s*\**\s*$", re.I)
    for i, line in enumerate(lines):
        if pat.match(line.strip()):
            return i
    return None


def parse_table(lines):
    rows = []
    for line in lines:
        t = line.strip()
        if not t.startswith("|"):
            if rows:
                break
            continue
        cells = [c.strip() for c in re.split(r"(?<!\\)\|", t.strip("|"))]
        if all(re.fullmatch(r":?-{2,}:?", c) for c in cells if c):
            continue
        rows.append(cells)
    return rows


def load_roles():
    roles = {}
    for r in yaml.safe_load((ROOT / "_data/roles.yml").read_text()):
        roles[r["id"]] = {"folder": r["url"].strip("/"), "type": r["type"], "label": r["plural"]}
    roles["anyone"] = {"folder": "getting_started", "type": "Getting_started", "label": "Getting started"}
    return roles


def find_module(page_id):
    hits = list((ROOT / "pages").glob(f"*/{page_id}.md"))
    return hits[0] if hits else None


# ---------------------------------------------------------------- body
def clean_body(lines, page_id):
    images = {}
    keep = []
    for line in lines:                                # reference-style images Google appends at the end
        m = re.match(r"^\[(image\d+)\]:\s*<?(data:image/(\w+);base64,[^>\s]+)>?\s*$", line.strip())
        if m:
            images[m.group(1)] = (m.group(2), m.group(3))
        else:
            keep.append(line)
    lines = keep

    out, in_checklist, levels = [], False, []
    for line in lines:
        m = re.match(r"^(#{1,6})\s", line)
        if m:
            levels.append(len(m.group(1)))
    shift = max(0, 2 - min(levels)) if levels else 0  # the page title is the only h1

    dropped = 0
    for raw in lines:
        line = raw.rstrip()
        plain = re.sub(r"^[>\s]*(?:[*\-+]|\d+[.)])?\s*", "", unescape(line)).strip()
        if plain.strip("*_ ").lower() in TEMPLATE_GUIDANCE:       # also when styled bold/italic
            continue
        if re.fullmatch(r"\[[^\]]{3,}\]", plain):       # a whole line still on its [template text]
            dropped += 1
            continue
        # lists exported as quotes ("> * item") when the Doc list is indented
        line = re.sub(r"^(\s*)>\s?(?=\s*(?:[*\-+]|\d+[.)])\s)", r"\1", line)
        line = re.sub(r"^(\s*)>\s?(?=\s*(?:☐|☑|☒|\\?\[[ xX]?\\?\]))", r"\1", line)
        h = re.match(r"^(#{1,6})\s+(.*)$", line)
        if h:
            text = re.sub(r"\*\*(.*?)\*\*", r"\1", h.group(2)).strip().strip("*").strip()
            text = unescape(text)
            level = min(6, len(h.group(1)) + shift)
            out.append(f"{'#' * level} {text}")
            in_checklist = bool(CHECKLIST_HEADINGS.search(text))
            continue
        li = re.match(r"^(\s*)(?:[*\-+])\s+(.*)$", line)
        box = re.match(r"^(\s*)(?:[*\-+]\s+)?(?:☐|\\?\[ ?\\?\])\s*(.*)$", line)
        done = re.match(r"^(\s*)(?:[*\-+]\s+)?(?:☑|☒|\\?\[[xX]\\?\])\s*(.*)$", line)
        if done:
            line = f"{done.group(1)}- [ ] {done.group(2)}"   # published checklists start unticked
        elif box:
            line = f"{box.group(1)}- [ ] {box.group(2)}"
        elif li:
            line = f"{li.group(1)}- {'[ ] ' if in_checklist and not li.group(1) else ''}{li.group(2)}"
        out.append(line)

    if dropped:
        warnings.append(f"{dropped} line(s) of the content were still template text and were left out")
    text = "\n".join(out)
    # Undo escapes that don't change meaning mid-line (keep \* \# \- \. that could start markup)
    text = re.sub(r"(?<!^)(?<!\n)\\([_:\[\]>~'\"=!()&])", r"\1", text)
    # Inside a URL a backslash never means anything ("www\.example.org" in Google's export)
    text = re.sub(r"https?\\?:\S+", lambda m: re.sub(r"\\(?=[^\w\s])", "", m.group(0)), text)
    # Bare URLs -> autolinks (kramdown doesn't link bare URLs)
    text = re.sub(r"(?<![<(\[\w])(https?://[^\s<>)\]]+?)([.,;]?)(?=\s|$)", r"<\1>\2", text)
    # Images that Google inlined as data -> files next to the site's images
    img_dir = ROOT / "assets/img/modules"
    for n, (key, (data, ext)) in enumerate(sorted(images.items()), 1):
        name = f"{page_id}-{n}.{ 'jpg' if ext == 'jpeg' else ext}"
        img_dir.mkdir(parents=True, exist_ok=True)
        (img_dir / name).write_bytes(base64.b64decode(data.split(",", 1)[1]))
        text = text.replace(f"![][{key}]", f"![]({{{{ '/assets/img/modules/{name}' | relative_url }}}})")
        warnings.append(f"image saved as assets/img/modules/{name}; add alt text in the page")
    # Sections with nothing left under them (template sections the author didn't use) are dropped.
    parts = re.split(r"(?m)^(?=#{2,6} )", text)
    lead_in = re.compile(r"^This module builds upon the following supporting frameworks:\s*$", re.M)
    text = "".join(p for p in parts if not re.fullmatch(r"#{2,6} [^\n]*\n\s*", lead_in.sub("", p)))
    text = re.sub(r"[ \t]+$", "", text, flags=re.M)
    text = re.sub(r"\n{3,}", "\n\n", text).strip() + "\n"

    for m in re.finditer(r"(?<!\!)\[([^\]\n]{4,})\](?!\()", text):
        if not re.fullmatch(r"[ xX]", m.group(1)):
            warnings.append(f"template text still in the content: [{m.group(1)[:60]}]")
    return text


# ---------------------------------------------------------------- front matter
def build(meta, roles, cpps):
    """Front matter from the metadata table. Only a missing title stops the page;
    everything else becomes a warning for the reviewer and a sensible default."""
    def get(k):
        v = meta.get(k, "")
        if v and is_placeholder(v):        # rows left on their [placeholder] are simply empty
            return ""
        return v

    fm = {}
    title = get("title").rstrip(".")
    if not title:
        errors.append("Title is empty. Give the module a name in the first row of the metadata table.")
    fm["title"] = title
    if get("description"):
        fm["description"] = get("description")
    fm["page_id"] = slug(get("page_id") or title)

    raw_role = get("as")
    role = pick(raw_role, ROLE_PICK, None) if raw_role else None
    if role is None:
        warnings.append(f"Who is it for {'`' + raw_role + '` not recognised' if raw_role else 'is empty'}; filed under Getting started (for every role)")
        role = "anyone"

    order = get("order")
    if order:
        m = re.search(r"\d+", order)
        if m:
            fm["order"] = int(m.group())
        else:
            warnings.append(f"Order `{order}` has no number; the module goes to the end of its path")

    raw_kind = get("kind")
    kind = pick(raw_kind, KIND_PICK) if raw_kind else None
    if kind:
        fm["kind"] = kind
    else:
        warnings.append(f"Kind of help {'`' + raw_kind + '` not recognised' if raw_kind else 'is empty'}; the page shows no kind badge until it is set")

    story = {"as": role}
    want = re.sub(r"^(as an? [^,]+,\s*)?i want to\s+", "", get("want"), flags=re.I).rstrip(".")
    if want:
        story["want"] = want[0].lower() + want[1:] if not want[:2].isupper() else want
    else:
        warnings.append("'I want to' is empty; the module is listed without its user story")
    task = get("task").rstrip(".")
    if task:
        story["task"] = task
        if len(task) > 45:
            warnings.append(f"Short task is {len(task)} characters; the home page menu works best under 45")
    so_that = re.sub(r"^so that\s+", "", get("so_that"), flags=re.I).rstrip(".")
    if so_that:
        story["so_that"] = so_that
    fm["story"] = story

    for key in ("disciplines", "data_types"):
        fm[key] = split_list(get(key).lower()) or ["all"]
    if get("keywords"):
        fm["keywords"] = split_list(get("keywords"))

    primary = cpp_ids(get("cpps_primary"), "Main processes", cpps)
    other = cpp_ids(get("cpps_other"), "Other processes", cpps)
    allc = sorted(set(primary) | set(other))
    if len(primary) > 3:
        warnings.append(f"'Main processes' lists {len(primary)}; kept the first 3 as main, the rest count as 'applies'")
        primary = primary[:3]
    if allc:
        fm["cpps"] = allc
    if primary:
        fm["cpps_primary"] = primary
    elif allc:
        warnings.append("No main process given; process pages will list this module under 'Also applied in'")

    sat = []
    for part in [p.strip() for p in re.split(r"[;\n]", get("satisfies")) if p.strip()]:
        name, _, codes = part.partition(":")
        fw = pick(name, FW_PICK)
        if not fw:
            warnings.append(f"Framework `{name.strip()}` not recognised; left out")
            continue
        if not codes:                                    # "CoreTrustSeal R14" without a colon
            codes = " ".join(re.findall(r"\b[A-Z]{1,5}-?\d+(?:\.\d+)*\b", name))
        codes = [c for c in re.split(r"[,\s]+", codes) if c]
        sat += [{"framework": fw, "code": c} for c in codes] or [{"framework": fw}]
    if sat:
        fm["satisfies"] = sat

    contributors = split_list(get("contributors"))
    if contributors:
        known = yaml.safe_load((ROOT / "_data/CONTRIBUTORS.yml").read_text()) or {}
        for c in contributors:
            if c not in known:
                warnings.append(f"Contributor `{c}` is not in _data/CONTRIBUTORS.yml yet; add them with their ORCID")
        fm["contributors"] = contributors

    titles = {}
    for f in (ROOT / "pages").glob("*/*.md"):
        try:
            t = (yaml.safe_load(f.read_text(encoding="utf-8").split("---", 2)[1]) or {}).get("title", "")
            titles[slug(str(t))] = f.stem
        except Exception:
            pass
    related = {}
    for rid in split_list(get("related")):
        sid = slug(rid)
        f = find_module(sid) or (find_module(titles[sid]) if sid in titles else None)
        if not f:
            warnings.append(f"Related module `{rid}` not found; left out")
            continue
        typ = next((r["type"] for r in roles.values() if r["folder"] == f.parent.name), None)
        if typ:
            related.setdefault(typ, []).append(f.stem)
    if related:
        fm["related_pages"] = related

    fm["status"] = "ready" if re.search(r"ready|publish|final|done", get("status").lower()) else "draft"
    fm["page_citation"] = True
    return fm, role


def to_yaml(fm):
    def scalar(v):
        return yaml.safe_dump(v, default_flow_style=True, allow_unicode=True, width=10**6, sort_keys=False).strip().removesuffix("\n...").removesuffix("...").strip()
    out = ["---"]
    for k, v in fm.items():
        if k == "story":
            out.append("story:")
            out += [f"  {sk}: {scalar(sv)}" for sk, sv in v.items()]
        elif k == "satisfies":
            out.append("satisfies:")
            out += ["  - " + scalar(s) for s in v]
        elif k == "related_pages":
            out.append("related_pages:")
            out += [f"  {t}: {scalar(ids)}" for t, ids in v.items()]
        else:
            out.append(f"{k}: {scalar(v)}")
    out.append("---")
    return "\n".join(out) + "\n"


def existing_source(path):
    try:
        return (yaml.safe_load(path.read_text(encoding="utf-8").split("---", 2)[1]) or {}).get("gdoc")
    except Exception:
        return None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("export", help="the .md file downloaded from Google Docs")
    ap.add_argument("--stdout", action="store_true", help="print the page instead of writing it")
    ap.add_argument("--force", action="store_true", help="overwrite a page that came from another source")
    ap.add_argument("--source-id", help="Google Doc id; recorded in the page so later exports update the same page")
    a = ap.parse_args()

    lines = pathlib.Path(a.export).read_text(encoding="utf-8").replace("\r\n", "\n").split("\n")
    mi, ci = find_heading(lines, "Module metadata"), find_heading(lines, "Module content")
    if mi is None or ci is None or ci < mi:
        print("error: the headings 'Module metadata' and 'Module content' are missing. Keep both from the template.")
        sys.exit(1)

    meta = {}
    for cells in parse_table(lines[mi + 1:ci])[1:]:          # first row is the header
        if len(cells) < 2:
            continue
        label = re.sub(r"[^a-z0-9_ ]", "", clean_value(cells[0]).lower()).strip()
        field = LABELS.get(label) or ("cpps_primary" if re.fullmatch(r"main process \d", label) else None) \
            or ("cpps_other" if re.fullmatch(r"other process(es)? \d", label) else None)
        value = clean_value(cells[1])
        if field in ("cpps_primary", "cpps_other") and meta.get(field) and not is_placeholder(meta[field]):
            if value and not is_placeholder(value):
                meta[field] += ", " + value                # numbered rows (v2 template) feed one list
        elif field:
            meta[field] = value
        elif label:
            warnings.append(f"unknown metadata row `{cells[0]}` ignored")

    roles = load_roles()
    fm, role = build(meta, roles, load_cpps())
    if a.source_id:
        fm["gdoc"] = a.source_id
    target = ROOT / "pages" / roles[role]["folder"] / f"{fm['page_id']}.md"
    stale = []
    if a.source_id:
        # The same Doc may already have a page under another name or role: replace it.
        stale = [f for f in (ROOT / "pages").glob("*/*.md") if f != target and existing_source(f) == a.source_id]
        # Another Doc already owns this page id: don't overwrite it, pick a free id.
        n = 2
        while target.exists() and existing_source(target) not in (None, a.source_id):
            fm["page_id"] = f"{slug(fm['title'])}_{n}"
            target = target.with_name(f"{fm['page_id']}.md")
            n += 1
        if n > 2:
            warnings.append(f"another Google Doc already has a module with this title; this one is saved as `{fm['page_id']}`. Consider a more specific title")
        if target.exists() and existing_source(target) is None:
            warnings.append(f"this replaces `{target.relative_to(ROOT)}`, which was edited directly in the repository; check the diff")
    elif target.exists() and not a.force and not a.stdout:
        print(f"error: {target.relative_to(ROOT)} exists; use --force to overwrite it")
        sys.exit(1)

    body = clean_body(lines[ci + 1:], fm["page_id"])
    page = to_yaml(fm) + "\n" + body

    for w in warnings:
        print(f"warning: {w}")
    for e in errors:
        print(f"error: {e}")
    if errors:
        sys.exit(1)

    if a.stdout:
        print(page)
        return
    target.write_text(page, encoding="utf-8")
    for f in stale:
        f.unlink()
        print(f"removed {f.relative_to(ROOT)} (same Doc, new name or role)")
    print(f"wrote {target.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
