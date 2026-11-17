#!/usr/bin/env python3
"""Glue between a Google Drive folder and the "Google Docs to pull request" workflow.

Authors never run this. GitHub Actions calls it:

  gdocs_sync.py list              which Docs to process (prints `docs=<json>` for $GITHUB_OUTPUT)
  gdocs_sync.py convert DOC_ID    export one Doc as Markdown, turn it into a module page,
                                  print outputs for the pull-request step
  gdocs_sync.py comment DOC_ID    add a comment to the Doc (text on stdin), anchored to the
                                  Title cell, so authors get feedback where they write
  gdocs_sync.py mark DOC_ID       one comment per point to check, anchored to the table cell
                                  (and the words) it is about

Environment:
  GDRIVE_SA_KEY         service-account JSON key (GitHub secret). The ready folder is shared
                        with that account as Commenter. Without a key, a single Doc can still be
                        converted if it is shared as "anyone with the link can view".
  GDRIVE_READY_FOLDER   ID of the "ready for the kit" Drive folder (GitHub variable)
  DOC_INPUT             optional Doc link or ID from a manual run
  EVENT                 github.event_name; scheduled runs pick up Docs edited in the last 75 minutes
                        and Docs the kit has not seen yet (no page, no open pull request)
"""
import datetime as dt, json, os, pathlib, re, subprocess, sys, tempfile, urllib.request, uuid

ROOT = pathlib.Path(__file__).resolve().parent.parent
RECENT_MINUTES = 75   # scheduled runs are hourly; overlap a little so nothing is missed


ISSUES = pathlib.Path(os.environ.get("RUNNER_TEMP") or tempfile.gettempdir()) / "gdocs-issues.json"


def _service(name, version):
    key = os.environ.get("GDRIVE_SA_KEY", "").strip()
    if not key:
        return None
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    creds = service_account.Credentials.from_service_account_info(
        json.loads(key), scopes=["https://www.googleapis.com/auth/drive"])
    return build(name, version, credentials=creds, cache_discovery=False)


def drive():
    return _service("drive", "v3")


# --- Anchored comments (Google Docs API insertComment) ---------------------------------
# The Drive API can only add comments that are not attached to any text; those never show in
# the margin. The Docs API can anchor a comment to a text range, so each point to check sits
# on the cell (and the words) it is about. Needs the Google Docs API enabled in the project.

# Which table row a converter message is about: (words in the message, row labels in the Doc).
ROWS = [("'main processes'", {"main processes", "processes it mainly teaches", "main process 1"}),
        ("no main process", {"main processes", "processes it mainly teaches", "main process 1"}),
        ("'other processes'", {"other processes", "other processes it applies"}),
        ("who is it for", {"who is it for", "role"}),
        ("kind of help", {"kind of help"}),
        ("'i want to'", {"i want to"}),
        ("short task", {"short task"}),
        ("order `", {"order in the role path", "order"}),
        ("framework `", {"frameworks", "frameworks cited"}),
        ("contributor `", {"contributors"}),
        ("related module `", {"related modules"}),
        ("title", {"title"})]


def _norm(s):
    return re.sub(r"[^a-z0-9 ]", "", s.lower()).strip()


def row_for(msg):
    """(row labels, words to highlight) for a converter message, or None if it names no row."""
    low = msg.lower()
    for words, labels in ROWS:
        if words in low:
            m = re.search(r"`([^`]+)`", msg)
            return labels, (m.group(1) if m else None)
    return None


def _runs(content):
    return [(pe["startIndex"], pe["textRun"]["content"])
            for el in content for pe in el.get("paragraph", {}).get("elements", []) if "textRun" in pe]


def _span(runs, needle=None):
    """UTF-16 range of `needle` inside the runs, or of their visible text when there is no needle."""
    chars, pos = [], []
    for start, text in runs:
        i = start
        for ch in text:
            chars.append(ch); pos.append(i)
            i += 2 if ord(ch) > 0xFFFF else 1
    full = "".join(chars)
    if needle:
        k = full.lower().find(needle.lower())
        if k < 0:
            return None
        a, b = k, k + len(needle) - 1
    else:
        stripped = [k for k, ch in enumerate(full) if not ch.isspace()]
        if not stripped:
            return None
        a, b = stripped[0], stripped[-1]
    return pos[a], pos[b] + (2 if ord(full[b]) > 0xFFFF else 1)


def locate(doc, labels, needle=None):
    """(tabId, start, end) for a metadata row: the needle in the value cell, else the value, else the label."""
    tab = doc["tabs"][0] if doc.get("tabs") else None
    body = (tab["documentTab"]["body"] if tab else doc["body"])["content"]
    tab_id = tab["tabProperties"]["tabId"] if tab else None
    for el in body:
        for row in el.get("table", {}).get("tableRows", []):
            cells = row["tableCells"]
            if len(cells) < 2 or _norm("".join(t for _, t in _runs(cells[0]["content"]))) not in labels:
                continue
            value = _runs(cells[1]["content"])
            hit = (needle and _span(value, needle)) or _span(value) or _span(_runs(cells[0]["content"]))
            return (tab_id, *hit) if hit else None
    return None


def _open_bot_comments(svc, did):
    texts, token = set(), None
    while True:
        r = svc.comments().list(fileId=did, fields="nextPageToken, comments(content, resolved, author(me))",
                                includeDeleted=False, pageToken=token, pageSize=100).execute()
        texts |= {c.get("content", "").strip() for c in r.get("comments", [])
                  if c.get("author", {}).get("me") and not c.get("resolved")}
        token = r.get("nextPageToken")
        if not token:
            return texts


def _anchored(docs, did, doc, text, where):
    tab_id, start, end = where
    rng = {"startIndex": start, "endIndex": end, **({"tabId": tab_id} if tab_id else {})}
    docs.documents().batchUpdate(documentId=did, body={"requests": [
        {"insertComment": {"content": text[:2000], "range": rng}}]}).execute()


def doc_id(text):
    m = re.search(r"/d/([A-Za-z0-9_-]{20,})", text or "")
    return m.group(1) if m else (text or "").strip()


def out(name, value):
    """Write a GitHub step output, multi-line safe."""
    value = str(value)
    if "\n" in value:
        tag = f"EOF_{uuid.uuid4().hex}"
        print(f"{name}<<{tag}\n{value}\n{tag}")
    else:
        print(f"{name}={value}")


def cmd_list():
    try:
        _list()
    except Exception as e:   # e.g. Drive API disabled, folder not shared with the service account
        print(f"::error::Google Drive refused the request: {e}. Check that the Drive API is enabled for the "
              "service account's project and that the ready folder (and any Doc you named) is shared with it.",
              file=sys.stderr)
        sys.exit(1)


def _list():
    svc = drive()
    single = os.environ.get("DOC_INPUT", "").strip()
    if single:
        did = doc_id(single)
        name = did
        if svc:
            name = svc.files().get(fileId=did, fields="name", supportsAllDrives=True).execute()["name"]
        print(f"1 Doc to process: {name}", file=sys.stderr)
        out("docs", json.dumps([did]))
        return
    folder = os.environ.get("GDRIVE_READY_FOLDER", "").strip()
    if not svc or not folder:
        print("No service-account key or folder configured; nothing to scan.", file=sys.stderr)
        out("docs", "[]")
        return
    q = f"'{folder}' in parents and mimeType='application/vnd.google-apps.document' and trashed=false"
    docs, token = [], None
    while True:
        r = svc.files().list(q=q, fields="nextPageToken, files(id, name, modifiedTime)", pageToken=token,
                             includeItemsFromAllDrives=True, supportsAllDrives=True).execute()
        docs += r.get("files", [])
        token = r.get("nextPageToken")
        if not token:
            break
    if os.environ.get("EVENT") == "schedule":
        # A Doc needs a run if it was edited recently, or if the kit has never seen it.
        # The second case catches Docs written earlier and only now moved into the folder
        # (moving a Doc does not change its modified time), and Docs still waiting on a fix.
        since = dt.datetime.now(dt.timezone.utc) - dt.timedelta(minutes=RECENT_MINUTES)
        known = known_docs()
        docs = [d for d in docs
                if dt.datetime.fromisoformat(d["modifiedTime"].replace("Z", "+00:00")) > since or d["id"] not in known]
    print(f"{len(docs)} Doc(s) to process", file=sys.stderr)
    for d in docs:
        print(f"  {d['id']}  {d['name']}", file=sys.stderr)
    # Plain IDs only: GitHub drops a job output that contains any part of a secret, and a
    # multi-line JSON key makes lines like "{" secret, so an output with braces would vanish.
    out("docs", json.dumps([d["id"] for d in docs]))


def known_docs():
    """Doc ids the kit already has: a page on the default branch, or an open gdocs/<id> branch."""
    ids = set()
    for f in (ROOT / "pages").glob("*/*.md"):
        m = re.search(r"^gdoc:\s*(\S+)", f.read_text(encoding="utf-8"), re.M)
        if m:
            ids.add(m.group(1))
    r = subprocess.run(["git", "ls-remote", "--heads", "origin", "gdocs/*"], capture_output=True, text=True, cwd=ROOT)
    ids |= set(re.findall(r"refs/heads/gdocs/(\S+)", r.stdout))
    return ids


def export_markdown(did):
    svc = drive()
    if svc:
        return svc.files().export(fileId=did, mimeType="text/markdown").execute().decode("utf-8")
    url = f"https://docs.google.com/document/d/{did}/export?format=md"
    with urllib.request.urlopen(url, timeout=60) as r:       # works only for link-shared Docs
        return r.read().decode("utf-8")


def cmd_convert(did):
    link = f"https://docs.google.com/document/d/{did}/edit"
    try:
        md = export_markdown(did)
    except Exception as e:
        print(f"::error::Could not read the Doc {did}: {e}. Is it in the ready folder, and is the folder shared with the service account?", file=sys.stderr)
        out("ok", "skip")
        return
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as f:
        f.write(md)
    r = subprocess.run([sys.executable, str(ROOT / "var/gdoc_to_module.py"), f.name, "--source-id", did],
                       capture_output=True, text=True, cwd=ROOT)
    log = (r.stdout + r.stderr).strip()
    print(log, file=sys.stderr)
    problems = [l.split(":", 1)[1].strip() for l in log.splitlines() if l.startswith("error:")]
    notes = [l.split(":", 1)[1].strip() for l in log.splitlines() if l.startswith("warning:")]
    ISSUES.write_text(json.dumps([{"kind": "error", "msg": p} for p in problems]
                                 + [{"kind": "warning", "msg": n} for n in notes]), encoding="utf-8")
    m = re.search(r"^wrote (pages/\S+\.md)$", log, re.M)
    if r.returncode != 0 or not m:
        out("ok", "false")
        text = ("The support-kit could not take this module yet. Please fix this in the Doc; "
                "it is checked again within the hour.\n\n"
                + "\n".join(f"• {p}" for p in (problems or [log.splitlines()[-1] if log else "unknown problem"])))
        out("comment", text)
        return
    page = ROOT / m.group(1)
    import yaml
    fm = yaml.safe_load(page.read_text(encoding="utf-8").split("---", 2)[1])
    out("ok", "true")
    out("attention", "true" if notes else "false")
    out("page", m.group(1))
    out("page_id", fm["page_id"])
    out("title", fm["title"])
    body = [f"Module written in Google Docs: [{fm['title']}]({link})", "",
            f"- Role: `{fm['story']['as']}` · kind: `{fm.get('kind')}` · status: `{fm.get('status')}`",
            f"- Page: `{m.group(1)}`", ""]
    if notes:
        body += ["**Points to check** (the module was converted; these were filled with defaults or left out)", ""] \
            + [f"- {n}" for n in notes] + [""]
    # Lightweight text matching against WP1's process descriptions: a second opinion, never applied.
    sugg = []
    try:
        r2 = subprocess.run([sys.executable, str(ROOT / "var/suggest_anchors.py"), "--json", str(page)],
                            capture_output=True, text=True, cwd=ROOT, timeout=120)
        sugg = [x for x in json.loads(r2.stdout or "[]") if not x.get("already")][:4]
    except Exception as e:
        print(f"suggestions skipped: {e}", file=sys.stderr)
    if sugg:
        body += ["**Possibly related processes** (automatic text match against WP1's descriptions; not applied, "
                 "add them in the Doc if they fit)", ""] \
            + [f"- {x['id']} {x['label']} · score {x['score']:.2f} · matched: {', '.join(x['why'])}" for x in sugg] + [""]
    sug = subprocess.run([sys.executable, str(ROOT / "var/suggest_anchors.py"), str(page), "--markdown"],
                         capture_output=True, text=True, cwd=ROOT)
    if sug.returncode == 0 and sug.stdout.strip():
        body += [sug.stdout.strip(), ""]
    body += ["**Review checklist**", "",
             "- [ ] The user story reads well and the title is the task",
             "- [ ] Main processes (1–3) are right; compare with the suggestions above",
             "- [ ] References have working links",
             "- [ ] Preview looks right (see the build check below)", "",
             "Changes go back into the Google Doc, not into this branch: the next edit to the Doc updates this pull request.",
             "", "_Opened automatically by the Google Docs to pull request workflow._"]
    out("body", "\n".join(body))
    out("notes", ("\n\nA few things the reviewers will check (marked in the Doc where possible; you can fix them here):\n" + "\n".join(f"• {n}" for n in notes[:6])) if notes else "")


def cmd_comment(did):
    text = sys.stdin.read().strip()
    svc = drive()
    if not text or not svc:
        print("nothing to post (no text or no service-account key)", file=sys.stderr)
        return
    # Skip if the bot already has the same open comment (hourly runs on an unchanged Doc).
    if text in _open_bot_comments(svc, did):
        print("same comment already in the Doc; not repeated", file=sys.stderr)
        return
    try:                                   # in the margin, on the Title cell
        docs = _service("docs", "v1")
        doc = docs.documents().get(documentId=did).execute()
        where = locate(doc, {"title"})
        if where:
            _anchored(docs, did, doc, text, where)
            print("comment added on the Title cell", file=sys.stderr)
            return
    except Exception as e:
        print(f"::warning::Anchored comment failed ({e}); adding it to the whole Doc instead. "
              "Is the Google Docs API enabled for the service account's project?", file=sys.stderr)
    svc.comments().create(fileId=did, body={"content": text}, fields="id").execute()
    print("comment added", file=sys.stderr)


def cmd_mark(did):
    """One comment per point to check, on the cell it is about. Never fails the run."""
    if not ISSUES.exists() or not drive():
        print("nothing to mark", file=sys.stderr)
        return
    issues = json.loads(ISSUES.read_text(encoding="utf-8"))
    try:
        svc, docs = drive(), _service("docs", "v1")
        doc = docs.documents().get(documentId=did).execute()
        done, posted = _open_bot_comments(svc, did), 0
        for it in issues:
            target = row_for(it["msg"])
            where = target and locate(doc, *target)
            if not where:
                continue                        # names no row: it is in the summary comment and the PR
            text = ("Please fix: " if it["kind"] == "error" else "The reviewers will check this: ") + it["msg"]
            if text in done:
                continue
            _anchored(docs, did, doc, text, where)
            posted += 1
        print(f"{posted} point(s) marked in the Doc", file=sys.stderr)
    except Exception as e:
        print(f"::warning::Could not mark points in the Doc ({e}). They are still listed in the summary "
              "comment and the pull request. Is the Google Docs API enabled for the project?", file=sys.stderr)


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in ("list", "convert", "comment", "mark"):
        sys.exit(__doc__)
    {"list": lambda: cmd_list(),
     "convert": lambda: cmd_convert(doc_id(sys.argv[2])),
     "comment": lambda: cmd_comment(doc_id(sys.argv[2])),
     "mark": lambda: cmd_mark(doc_id(sys.argv[2]))}[sys.argv[1]]()
