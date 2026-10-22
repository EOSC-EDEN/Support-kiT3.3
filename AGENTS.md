# AGENTS.md

Guidance for coding agents (and people) working on the EOSC EDEN T3.3 support-kit.
How to run the site and set up the Google Docs pipeline is in `README.md`.
Rules for AI-assisted work (Claude, Qwen and others) are in `AI_CONTRIBUTING.md`.

## What this is

- A Jekyll site on the **ELIXIR Toolkit Theme (ETT) 7.0.0**, built the way RDMkit is.
- Each page is a **module**: a user story ("As a *role*, I want to *task*, so that *benefit*")
  with a Diátaxis kind (tutorial, how-to, reference, explanation), anchored to WP1's 30
  **Core Preservation Processes (CPPs)** and cross-walked to frameworks (CoreTrustSeal,
  nestor, ISO 16363, OAIS, PREMIS, EOSC FAIR metrics).
- Roles: `researcher`, `manager`, `trainer`; `anyone` means every role.
- Authors write in **Google Docs**; a workflow turns finished Docs into pull requests.
  Authors never touch GitHub, Markdown or scripts.

## Rules

1. Work on branch **`ett`**. `main` keeps the old vanilla-JS app until the cut-over. Don't extend the old app.
2. **Ask before** pushing, force-pushing, opening PRs, or changing repository settings, secrets or variables.
3. Commit as the user. No AI co-author trailers in commit messages (the README already notes AI use).
4. **Never override an ETT theme file.** Add new files instead (`_includes/kit-*.html`, `_layouts/module.html`,
   `_layouts/cpp.html`). Styling only in the three `_sass/` hook files and `assets/js/custom.js`.
   Upgrading ETT must stay a version bump.
5. ETT stays pinned: `remote_theme: ELIXIR-Belgium/elixir-toolkit-theme@7.0.0`.
6. Keep the EDEN branding (teal `#008691`, pink `#eb5d81`, ink `#1d2327`). Learn from RDMkit's use of ETT
   mechanisms; don't copy its content, links or look.
7. Modules are **pages, not a collection**: ETT's `type` comes from folder defaults, and related pages,
   sidebar and tiles depend on it.
8. Scripts are Python and live in `var/`.
9. URLs are stable: `/<page_id>` via `permalink: /:basename`. Never rename a file without `redirect_from:`.
10. WP1 data is mirrored, never edited by hand (`_data/cpps.json`, later `_data/indicators.json`).
11. Content checks **report, never block**. One bad module must not stop the site publishing.
12. Never invent `cpps_primary`. If the text doesn't make it obvious, leave it out and ask.

## Layout

```
_config.yml           remote_theme, folder → type/layout defaults, theme_variables
_data/                cpps.json (WP1 mirror), indicators.json, frameworks.yml, roles.yml,
                      sidebars/main.yml (module lists generated), topnav, footer, CONTRIBUTORS
_layouts/             module.html, cpp.html (both extend ETT `page`)
_includes/kit-*.html  story, meta, kind badge, connections, track nav, shared modules, kit-flow
_sass/                EDEN brand and all custom CSS (ETT hook files only)
assets/js/custom.js   home picker and filters, tickable/printable checklists
index.html            home: role/task picker, path cards, filterable story list
pages/<role folder>/  modules; pages/cpps/cpp_0NN.md are generated
var/                  check_modules, make_sidebar, sync_cpps, make_cpp_pages,
                      gdoc_to_module, gdocs_sync, suggest_anchors, tests/
.github/workflows/    jekyll.yml, gdocs-to-pr.yml (hourly), sync-cpps.yml (weekly)
```

Folder defaults: `getting_started`, `researchers`, `repository_managers`, `rdm_trainers` → layout `module`;
`cpps` → layout `cpp`, `toc: false`.

## Commands

```
bundle exec jekyll serve --livereload        # gems in vendor/bundle (.bundle/config)
python3 var/check_modules.py [--strict]      # front-matter report
python3 var/make_sidebar.py                  # regenerate sidebar module lists (CI does this)
python3 var/sync_cpps.py [--summary FILE]    # mirror WP1 CPPs, regenerate pages/cpps/
python3 var/tests/test_gdoc_to_module.py     # run after any converter change
python3 var/suggest_anchors.py page.md       # suggest CPPs for a module (suggestions only)
```

## Module front matter

```yaml
---
title: Preparing deposits – file formats and technical data quality   # text before " – " is the menu label
description: One sentence for cards and search.
page_id: preparing_deposits        # = file name, no hyphens; also the URL
order: 1                           # position in the role path
kind: how-to                       # tutorial | how-to | reference | explanation
story:
  as: researcher                   # researcher | manager | trainer | anyone
  want: prepare my files for deposit, with sustainable formats, documentation and basic checks
  task: prepare my files for deposit   # ≤ 45 chars, home-page picker
  so_that: the dataset stays accessible, understandable and reusable
disciplines: [all]
data_types: [all]
keywords: [deposit]
cpps: [CPP-001, CPP-010]           # every process it applies (≤ 12)
cpps_primary: [CPP-010]            # 1–3 it mainly teaches; subset of cpps
satisfies:
  - {framework: cts-2026, code: R14}
contributors: [Anna-Lena Flügel]   # keys of _data/CONTRIBUTORS.yml
related_pages:
  Repository_managers: [reviewing_deposits]
status: draft                      # draft | ready
page_citation: true
gdoc: <doc id>                     # set by the converter, don't edit
nav_title: Preparing deposits      # optional
effort: 20 min                     # optional
---
```

Body: opening paragraph, `##` sections, recommendations as `- [ ]` items, references under "More information".

## Liquid conventions (these caused real bugs)

- Prefix every variable inside a `kit-*` include (`kn_`, `km_`, `kb_`, `ks_`, `kt_`, `ka_`, `ksh_`, `mr_`, `cu_`).
  Include variables leak into the caller.
- `where_exp` needs explicit comparisons: `"p.order != nil"`.
- ETT 7.0.0 has a `{% else % %}` typo in `resource-table-all.html`; Jekyll tolerates it.

## Pipelines

- **WP1 CPPs:** `sync-cpps.yml` runs `var/sync_cpps.py` weekly and opens PR `bot/sync-cpps` only when CPP
  content changed.
- **Google Docs → PR:** `gdocs-to-pr.yml` lists Docs in the "ready" Drive folder, converts each with
  `var/gdoc_to_module.py` and opens one PR per Doc (`gdocs/<docId>`). Failures become a comment in the Doc.
  The converter is deliberately forgiving (Google export quirks, loose roles/kinds/CPP names); keep it so.
- **Pages:** `pages.yml` publishes the old app from `main` at `/` and the kit from `ett` at `/ett`
  (https://eosc-eden.github.io/Support-kiT3.3/ett/). Identical copy needed on `main`. Links must use
  `relative_url`, never a bare `/`.
- Scheduled workflows only fire from the default branch; while `ett` isn't default they need a copy on `main`.

## Google Drive items

Owned by the project owner's Drive (to move to a shared drive later).

| Item | ID |
|---|---|
| Module template v2 (use this; dropdowns for role, kind, main process 1–3, status) | `16JsiG9edwKCt3cuaTMEdR3kISEdrFYqT3MPK489iLys` |
| Worked example "Preparing deposits" (v1 layout, still converts) | `1FBlwyqkM-S8QlRBxH58q8z9H-2KLo3ufBdt3yJwDeEc` |
| "Ready for the kit" folder (`GDRIVE_READY_FOLDER`) | `1qTIuQq-G62Bf6-CZgTxH-C4KevIcWnGI` |
| Old template v1 (to trash or rename "old") | `1us82PGa7Na80dTGEmpkTDJH8Vf-3CIpCmq_ZRz8U6G0` |

## Not verified yet

- The live Drive → PR run against the real Drive API and GitHub (needs the secrets in README).
- Whether the v2 template's dropdowns survived the docx → Google Docs conversion (the converter works either way).
- The public-link fallback (`/export?format=md` without a service-account key): best effort.
- `jekyll-github-metadata` with a token in CI. If `prism` fails to build, drop `jemoji` (unused).

Verified with real Jekyll: the build, task lists, and ETT's `{% else % %}` typo being harmless.

## Cut-over: `ett` becomes `main` (only when the owner says so)

1. Tag the last commit of the old app on `main` (e.g. `vanilla-final`).
2. Merge `ett` into `main` (or reset `main` to `ett` if the owner prefers). Add `redirect_from:` for old app URLs people link to.
3. Set `KIT_BRANCH=main` (or delete it) and `KIT_DEPLOY=true`; delete `pages.yml`. Remove duplicate scheduled workflow copies.
4. Pages deploys from the workflow; the `github-pages` environment must allow `main`.
5. Check `github.source.branch` in `_config.yml` and the edit/issue links.
6. Delete `ett`, or keep it protected for a release or two.

## Open decisions (owners, not code)

- `cpps_primary` in Preparing deposits (CPP-010, CPP-001), Reviewing deposits (CPP-010, CPP-002, CPP-007)
  and Enabling discovery (CPP-024, CPP-005) are placeholders awaiting author sign-off.
- CoreTrustSeal version per module: `cts-2023` or `cts-2026`.
- Licence of contributed content (CC BY 4.0 assumed in the footer); confirm with WP5.
- Discipline and data-type vocabularies: free text until T3.2 has a list.
- Hosting after the project: Codeberg planned; `peter-evans/create-pull-request` and GitHub Pages need replacements.
- Indicators: confirm M1.2 IDs, when authors start tagging them, and whether candidate metrics are shown at all.
- Tool-made anchor links stay suggestions until a person accepts them; who curates the CPP ↔ indicator crosswalk.

## Planned design (don't build without the owner)

- **Re-use fitness indicators** (WP1 M1.2, DOI 10.5281/zenodo.21064927; 74 indicators in pillars CDQ/TDQ/MDQ)
  become a second anchor exactly like CPPs: `var/sync_indicators.py` → `_data/indicators.json`, an
  `_data/anchor_sets.yml` that templates loop over, `indicators` / `indicators_primary` front matter,
  pages `pages/indicators/ind_<id>.md`. Keep CPP output byte-identical. Confirm the ID scheme first.
- **Anchor suggestions** (`var/suggest_anchors.py`, TF-IDF; embeddings optional) only ever *suggest*;
  people decide. Crosswalks are stored as SSSOM TSV in `_data/mappings/`, and the site uses curated rows only.

## References

- WP1 CPPs: https://github.com/EOSC-EDEN/wp1-cpp-descriptions
- ETT: https://github.com/ELIXIR-Belgium/elixir-toolkit-theme · RDMkit: https://github.com/elixir-europe/rdmkit
- Diátaxis: https://diataxis.fr · SSSOM: https://mapping-commons.github.io/sssom/
