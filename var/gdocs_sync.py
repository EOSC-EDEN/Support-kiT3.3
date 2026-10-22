#!/usr/bin/env python3
"""Glue between a Google Drive folder and the "Google Docs to pull request" workflow.

Authors never run this. GitHub Actions calls it:

  gdocs_sync.py list              which Docs to process (prints `docs=<json>` for $GITHUB_OUTPUT)
  gdocs_sync.py convert DOC_ID    export one Doc as Markdown, turn it into a module page,
                                  print outputs for the pull-request step
  gdocs_sync.py comment DOC_ID    add a comment to the Doc (text on stdin), so authors get
                                  feedback where they write

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


def drive():
    key = os.environ.get("GDRIVE_SA_KEY", "").strip()
    if not key:
        return None
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    creds = service_account.Credentials.from_service_account_info(
        json.loads(key), scopes=["https://www.googleapis.com/auth/drive"])
    return build("drive", "v3", credentials=creds, cache_discovery=False)


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
    svc = drive()
    single = os.environ.get("DOC_INPUT", "").strip()
    if single:
        did = doc_id(single)
        name = did
        if svc:
            name = svc.files().get(fileId=did, fields="name", supportsAllDrives=True).execute()["name"]
        out("docs", json.dumps([{"id": did, "name": name}]))
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
    out("docs", json.dumps([{"id": d["id"], "name": d["name"]} for d in docs]))


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
    out("notes", ("\n\nA few things the reviewers will check (you can fix them here):\n" + "\n".join(f"• {n}" for n in notes[:6])) if notes else "")


def cmd_comment(did):
    text = sys.stdin.read().strip()
    svc = drive()
    if not text or not svc:
        print("nothing to post (no text or no service-account key)", file=sys.stderr)
        return
    # Skip if the bot's latest open comment already says the same thing (hourly runs on an unchanged Doc).
    mine = []
    token = None
    while True:
        r = svc.comments().list(fileId=did, fields="nextPageToken, comments(content, resolved, author(me))",
                                includeDeleted=False, pageToken=token, pageSize=100).execute()
        mine += [c for c in r.get("comments", []) if c.get("author", {}).get("me")]
        token = r.get("nextPageToken")
        if not token:
            break
    if mine and not mine[-1].get("resolved") and mine[-1].get("content", "").strip() == text:
        print("same comment already in the Doc; not repeated", file=sys.stderr)
        return
    svc.comments().create(fileId=did, body={"content": text}, fields="id").execute()
    print("comment added", file=sys.stderr)


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in ("list", "convert", "comment"):
        sys.exit(__doc__)
    {"list": lambda: cmd_list(),
     "convert": lambda: cmd_convert(doc_id(sys.argv[2])),
     "comment": lambda: cmd_comment(doc_id(sys.argv[2]))}[sys.argv[1]]()
