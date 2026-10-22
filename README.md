# EOSC EDEN Support-kit — ELIXIR Toolkit Theme demo

> **Branch:** this site lives on `ett` until it replaces the old app on `main`. See AGENTS.md.

Plain Jekyll site on the ELIXIR Toolkit Theme (pinned `@7.0.0`), structured like RDMkit.
Nothing in the theme is overridden: everything EDEN-specific is a new file.

- `_config.yml`: sections by folder (`type` and `layout` come from `defaults`), branding variables
- `_data/`: navigation, footer, contributors (ORCID), frameworks, `cpps.json` (mirrored from WP1)
- `_layouts/module.html`, `_layouts/cpp.html`: extend ETT's `page` layout
- `_includes/kit-*.html`: story line, kind badge, CPP chips, CPP panel, crosswalk, prev/next, status
- `_sass/`: EDEN teal `#008691` and pink `#eb5d81`, Lexend + Inter
- `assets/js/custom.js`: landing-page filters and CPP highlighting
- `var/sync_cpps.py`: mirrors WP1's CPPs into `_data/cpps.json` and regenerates `pages/cpps/`
  (via `var/make_cpp_pages.py`); `.github/workflows/sync-cpps.yml` runs it every Monday and opens a PR on changes

Run locally (Ubuntu/Debian):

```bash
sudo apt install ruby-full ruby-dev build-essential zlib1g-dev libyaml-dev
bundle config set --local path vendor/bundle   # already set in .bundle/config
bundle install
bundle exec jekyll serve --livereload           # http://127.0.0.1:4000
```

Gems install into `vendor/bundle` (no sudo, excluded from the build).
 Deploy with the
GitHub Actions workflow from `elixir-toolkit-theme-example` (`.github/workflows/jekyll.yml`).

Draft content: the user stories and kinds were drafted from the articles and need author sign-off.

## Linking modules to Core Preservation Processes

- `cpps`: every WP1 process the module applies.
- `cpps_primary`: the 1–3 processes it mainly teaches (each must also be in `cpps`).
  CPP pages list these first under "Start here"; the rest are grouped by role
  under "Also applied in", so a process cited by dozens of modules stays readable.
- `story.task`: a short label (under ~45 characters) for the home-page picker.

Run `python3 var/check_modules.py` before committing; CI runs it before every build.

## Writing a module in Google Docs (no code needed)

1. Copy the Google Doc "EDEN Support-kit – module template (v2)" (File > Make a copy).
   "EDEN Support-kit – example module (Preparing deposits)" shows one filled in.
2. Fill in the metadata table and write under "Module content". Share with colleagues for comments as usual.
3. When it is ready, move the Doc into the Drive folder **EDEN Support-kit – ready for the kit**.

Within the hour a pull request appears in this repository, and the author gets a comment
in the Doc with its link. Later edits to the Doc update the same pull request. Reviewers
merge it; the author never touches GitHub.

**What blocks, what doesn't.** Only a Doc with no title (or with the template's two
section headings deleted) is held back, with a comment telling the author. Everything
else goes through with a sensible default and is listed in the pull request under
"Points to check" (label `needs-attention`) and in the author's comment:

| In the Doc | What happens |
|---|---|
| Role empty or unclear | Filed under Getting started (for every role) |
| Kind of help empty | No kind badge until it is set |
| "I want to" empty | Listed without its user story |
| Process typed as a name ("virus scan") | Matched to CPP-007 Virus Scanning, flagged so the reviewer can confirm |
| Unknown process, framework or related module | Left out, flagged |
| More than 3 main processes | First 3 kept as main, the rest count as "applies" |
| Same title as another Doc's module | Saved as `<page_id>_2`, flagged |
| Title or role changed later | The old page is replaced (the Doc id is stored as `gdoc:` in the page) |

`var/check_modules.py` also only reports: findings show up as annotations on the build,
and one module with a problem never stops the site from publishing. Run it with
`--strict` if you want it to fail locally.

### Dropdowns in the template (2 minutes, done once in the template)

Copies inherit dropdowns, and the converter reads the chosen text. In the template, click the
value cell and use Insert > Dropdown, then save each as a preset so it can be reused:

| Row | Options |
|---|---|
| Role | Researcher · Repository manager · RDM trainer · Every role |
| Kind of help | Get it done (how-to) · Learn by doing (tutorial) · Look it up (reference) · Understand why (explanation) |
| Main process 1, 2, 3 | the 30 WP1 processes as "010 · File Format Validation" (one row each; leave unused rows on the placeholder) |
| Status | Draft · Ready for review |

Rows called "Main process 1/2/3" (or "Other process 1/2/…") are combined into one list, so the
template can offer one dropdown per process. Typed values still work: names, numbers, "CPP-010",
"CoreTrustSeal R14" are all understood.

### Google Docs to pull request: setup (once, by a repository admin)

1. **Service account.** In Google Cloud console: create a project, enable the *Google Drive API*,
   create a service account, and add a JSON key.
2. **Share the folder** "EDEN Support-kit – ready for the kit" with the service account's
   e-mail address as **Commenter** (it reads the Docs and leaves feedback comments).
3. **GitHub secret** `GDRIVE_SA_KEY`: the whole JSON key (Settings > Secrets and variables > Actions).
4. **GitHub variable** `GDRIVE_READY_FOLDER`: the folder ID, the last part of its URL.
5. **Allow Actions to open pull requests:** Settings > Actions > General > Workflow permissions >
   "Allow GitHub Actions to create and approve pull requests".
6. Optional: a secret `KIT_BOT_TOKEN` (fine-grained token, or a GitHub App token, with
   contents and pull-requests write) so the site build check also runs on these pull requests.
   Pull requests opened with the default token don't trigger other workflows.

Test it with Actions > Google Docs to pull request > Run workflow, pasting one Doc link.
Without the service account, a manual run still works for a Doc shared as
"anyone with the link can view".

### By hand

```bash
python3 var/gdoc_to_module.py ~/Downloads/my-module.md            # writes pages/<role>/<page_id>.md
python3 var/gdoc_to_module.py ~/Downloads/my-module.md --stdout   # preview without writing
python3 var/make_sidebar.py                                       # refresh the sidebar for local preview
```

The converter maps the table to front matter, cleans Google's Markdown export (bold headings,
lists exported as quotes, backslash escapes, bare URLs, inline images) and turns the bullets
under "Recommendations" into a checklist. The sidebar's module lists are generated from the
pages by `var/make_sidebar.py` (CI runs it before each build), so new modules never need a
sidebar edit and parallel pull requests don't conflict.
