#!/usr/bin/env python3
"""Write the authors' reference sheet as HTML, from the kit's own data.

    python3 var/make_reference_sheet.py > reference.html

Upload the result to Google Drive as a Google Doc ("EDEN Support-kit – reference sheet"),
replacing the old one, whenever the CPPs, frameworks, modules or contributors change.
"""
import html, json, pathlib, re, yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
e = html.escape
cpps = json.loads((ROOT / "_data/cpps.json").read_text())["cpps"]
frameworks = yaml.safe_load((ROOT / "_data/frameworks.yml").read_text())
contributors = sorted(yaml.safe_load((ROOT / "_data/CONTRIBUTORS.yml").read_text()) or {})
modules = []
for p in sorted((ROOT / "pages").glob("*/*.md")):
    m = re.search(r"^title:\s*(.+)$", p.read_text(encoding="utf-8"), re.M)
    if m and "/cpps/" not in str(p):
        modules.append(m.group(1).strip().strip('"'))

def table(head, rows):
    th = "".join(f"<td><b>{e(h)}</b></td>" for h in head)
    tr = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return f'<table border="1"><tr>{th}</tr>{tr}</table>'

FIELDS = [  # row, required, what to write, example
    ("Title", "Yes", "Task first, under 8 words.", "Checking file formats on ingest"),
    ("Description", "No", "One sentence shown on cards and in search.", "Identify and validate file formats when data arrives."),
    ("Who is it for", "Yes", "One of: Researcher, Repository manager, RDM trainer, Everyone.", "Repository manager"),
    ("I want to", "Yes", "The reader's goal, lower case, without “I want to”.", "check the formats of incoming files before ingest"),
    ("So that", "Yes", "Why it matters to the reader.", "broken files are caught before they are archived"),
    ("Kind of help", "Yes", "One of: How-to, Tutorial, Reference, Explanation (see below).", "How-to"),
    ("Main processes", "Yes", "1 to 3 processes the module mainly teaches. Number or name, separated by commas.", "file format identification, 10"),
    ("Other processes", "No", "Other processes the reader also touches.", "virus scan, ingest"),
    ("Frameworks", "No", "Frameworks the module helps meet, separated by semicolons (see below).", "CoreTrustSeal R14; nestor"),
    ("Keywords", "No", "A few words people might search for, separated by commas.", "file formats, PRONOM"),
    ("Related modules", "No", "Titles of other kit modules (see below).", "Reviewing deposits"),
    ("Contributors", "Yes", "Type @ to pick people, or write names.", "Anna-Lena Flügel"),
    ("Status", "Yes", "Draft while writing; Ready when you move the Doc to the ready folder.", "Ready"),
]
KINDS = [
    ("How-to", "Get it done", "Steps for a task the reader already understands."),
    ("Tutorial", "Learn by doing", "A first, guided walk-through."),
    ("Reference", "Look it up", "Facts and lists to check against."),
    ("Explanation", "Understand why", "Background and reasons."),
]
groups = {}
for c in cpps:
    groups.setdefault(c["logical"], []).append(c)

out = ['<html><body>',
       '<p><b>EDEN Support-kit – reference sheet</b></p>',
       '<p>Everything the module template asks for, and the values the kit understands. Keep it open next to your module. '
       'You can write values in your own words: the kit matches names, numbers and spelling variants, and the reviewers check the rest.</p>',
       '<h1>The table, row by row</h1>',
       table(["Row", "Required", "What to write", "Example"], [(e(a), e(b), e(c), e(d)) for a, b, c, d in FIELDS]),
       '<p>Leave a row on its [placeholder] if it doesn’t apply. Only a missing Title stops a module; anything else is filled with a default and flagged for the reviewers.</p>',
       '<h1>Kind of help</h1>',
       table(["Write", "Shown on the site as", "Use it for"], [(e(a), e(b), e(c)) for a, b, c in KINDS]),
       '<h1>Processes (WP1 Core Preservation Processes)</h1>',
       '<p>Write the number (10, 010 or CPP-010) or the name (file format validation). Full descriptions: '
       '<a href="https://eosc-eden.github.io/wp1-cpp-descriptions/">WP1 CPP descriptions</a>. '
       'The definitions below are WP1’s; TDA means Trustworthy Digital Archive.</p>']
for g, items in groups.items():
    out.append(f"<h2>{e(g)}</h2>")
    out.append(table(["No.", "Name", "What it is"],
                     [(c["id"].split("-")[1], f'<a href="{e(c["url"])}">{e(c["label"])}</a>', e(c["shortDefinition"])) for c in items]))
out += ['<h1>Frameworks</h1>',
        '<p>Name the framework, and the requirement if there is one. Separate several with semicolons.</p>',
        table(["Framework", "Write for example"], [
            (f'<a href="{e(f["url"])}">{e(f["label"])}</a>',
             e({"cts-2023": "CoreTrustSeal 2023 R14", "cts-2026": "CoreTrustSeal R14", "nestor": "nestor",
                "iso-16363": "ISO 16363 4.2", "oais": "OAIS", "premis": "PREMIS", "eosc-tf-fm": "EOSC FAIR metrics"}.get(f["id"], f["label"])))
            for f in frameworks]),
        '<p>“CoreTrustSeal” on its own means the 2026–2028 version; write “CoreTrustSeal 2023” for the earlier one.</p>',
        '<h1>Modules already in the kit</h1>',
        '<p>For the Related modules row.</p><ul>' + "".join(f"<li>{e(t)}</li>" for t in modules) + '</ul>',
        '<h1>Contributors already in the kit</h1>',
        '<p>New names are welcome; the reviewers add them with their ORCID.</p><ul>' + "".join(f"<li>{e(n)}</li>" for n in contributors) + '</ul>',
        '<h1>Writing the module</h1><ul>',
        '<li>Start with an opening paragraph: why the task matters and what the reader has when they finish.</li>',
        '<li>Use Google Docs headings for sections and real bullet lists.</li>',
        '<li>Under Recommendations, write one action per bullet, starting with a verb. On the website these become a checklist readers can tick.</li>',
        '<li>Under More information, one source per bullet; paste links as they are.</li>',
        '<li>Images are fine; add a short description of each in the text.</li></ul>',
        '<h1>What happens after you hand in</h1><ol>',
        '<li>Move the Doc into the folder “EDEN Support-kit – ready for the kit”.</li>',
        '<li>Within the hour you get a comment in the Doc with a link to the review and anything the reviewers will check.</li>',
        '<li>Keep editing the Doc; each change updates the review.</li>',
        '<li>When the reviewers merge it, the module appears on the website.</li></ol>',
        '</body></html>']
print("\n".join(out))
