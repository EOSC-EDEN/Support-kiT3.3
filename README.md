# EOSC EDEN Support-kit — ELIXIR Toolkit Theme demo

> **Branch:** this site lives on `ett` until it replaces the old app on `main`. See AGENTS.md.
>
> **AI use:** see [AI_CONTRIBUTING.md](AI_CONTRIBUTING.md).

Plain Jekyll site on the ELIXIR Toolkit Theme (pinned `@7.0.0`), structured like RDMkit.
Nothing in the theme is overridden: everything EDEN-specific is a new file.

- `_config.yml`: sections by folder (`type` and `layout` come from `defaults`), branding variables
- `_data/`: navigation, footer, contributors (ORCID), frameworks, `cpps.json` (mirrored from WP1)
- `_layouts/module.html`, `_layouts/cpp.html`: extend ETT's `page` layout
- `_includes/kit-*.html`: user story, meta line, kind badge, CPP chip, "Anchored to" panel, prev/next,
  shared modules, module rows, the Google Docs walkthrough on `/contribute`
- `_sass/`: EDEN teal `#008691` and pink `#eb5d81`, Lexend + Inter
- `assets/js/custom.js`: home-page picker, filters and list collapsing; tickable, printable checklists
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

Publishing: `.github/workflows/pages.yml` puts the old app from `main` at `/` and this site at
`/ett` (https://eosc-eden.github.io/Support-kiT3.3/ett/). `jekyll.yml` only checks the build.

Draft content: the user stories and kinds were drafted from the articles and need author sign-off.

## Linking modules to Core Preservation Processes

- `cpps`: every WP1 process the module applies.
- `cpps_primary`: the 1–3 processes it mainly teaches (each must also be in `cpps`).
  CPP pages list these first under "Start here"; the rest are grouped by role
  under "Also applied in", so a process cited by dozens of modules stays readable.
- `story.task`: a short label (under ~45 characters) for the home-page picker.

Run `python3 var/check_modules.py` before committing; CI runs it before every build.

## Writing a module in Google Docs (no code needed)

1. Copy the Google Doc "EDEN Support-kit – module template" (File > Make a copy).
   "EDEN Support-kit – example module v3 (Checking file formats on ingest)" shows one filled in.
   Both are in the Drive folder "EDEN Support-kit", next to the ready folder.
2. Fill in the metadata table and write under "Module content". Share with colleagues for comments as usual.
3. When it is ready, move the Doc into the Drive folder **EDEN Support-kit – ready for the kit**.

Once the pipeline below is set up, a workflow checks the folder every hour and opens one pull request
per Doc; the author gets a comment in the Doc with its link, and later edits update the same pull
request. Reviewers merge it; the author never touches GitHub. (Not yet run against the real Drive.)

### What the template looks like

One plain table, then the module. No dropdowns: authors write every value in their own words, and
the converter works out what they mean. Text still in `[square brackets]` counts as not filled in,
so optional rows can simply be left alone.

The converter needs two Google Docs headings, **Module metadata** and **Module content**. The
metadata table has the columns *Field*, *Value* and *How to fill it*; only the first two are read.

| Field | Example value | Becomes |
|---|---|---|
| Title | Checking file formats on ingest | `title`, `page_id` (required) |
| Description | One sentence for cards and search | `description` |
| Who is it for | Repository manager | `story.as`: Researcher, Repository manager, RDM trainer or Everyone |
| I want to | check the formats of incoming files before ingest | `story.want` |
| So that | broken files are caught before they are archived | `story.so_that` |
| Kind of help | How-to | `kind`: How-to, Tutorial, Reference or Explanation |
| Main processes | file format identification, 10 | `cpps_primary`: 1–3 processes, names or numbers |
| Other processes | virus scan | `cpps` (optional) |
| Frameworks | CoreTrustSeal R14; nestor | `satisfies` (optional, separated by semicolons) |
| Keywords | formats, ingest | `keywords` (optional) |
| Related modules | Preparing deposits | `related_pages` (optional, titles of other modules) |
| Contributors | @person chips or names | `contributors` |
| Status | Draft or Ready | `status` |

Left out on purpose, so authors have less to fill in: the home-page menu label (taken from
"I want to"), the order in the role path (reviewers set it; new modules go to the end), and
disciplines and data types (default "all"). Reviewers can add these in the pull request.

**Module content** starts with an opening paragraph, then the sections *Considerations*,
*Recommendations* and *More information*. Bullets under *Recommendations* (or *Checklist*, *Steps*)
become a tickable checklist on the site.

Older Docs made from the v1 or v2 template (with rows such as "Role", "Main process 1/2/3" or
"Frameworks cited") still convert.

### What blocks, what doesn't

Only a Doc with no title, or with one of the two headings above deleted, is held back, with a comment
telling the author. Everything else goes through with a default and is listed in the pull request
under "Points to check" (label `needs-attention`) and in the author's comment:

| In the Doc | What happens |
|---|---|
| "Who is it for" empty or unclear | Filed under Getting started (for every role) |
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
Without the service account, a manual run falls back to the Doc's public export link
("anyone with the link can view"); this fallback is untested, treat it as best effort.

### By hand

```bash
python3 var/gdoc_to_module.py ~/Downloads/my-module.md            # writes pages/<role>/<page_id>.md
python3 var/gdoc_to_module.py ~/Downloads/my-module.md --stdout   # preview without writing
python3 var/make_sidebar.py                                       # refresh the sidebar for local preview
```

The converter maps the table to front matter, cleans Google's Markdown export (bold headings,
lists exported as quotes, backslash escapes, bare URLs, inline images saved under
`assets/img/modules/`) and turns the bullets under "Recommendations" into a checklist. The sidebar's module lists are generated from the
pages by `var/make_sidebar.py` (CI runs it before each build), so new modules never need a
sidebar edit and parallel pull requests don't conflict.
