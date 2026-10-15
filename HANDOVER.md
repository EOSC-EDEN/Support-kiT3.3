# Handover: EOSC EDEN T3.3 Support-kit on the ELIXIR Toolkit Theme

For Claude Code, working in `EOSC-EDEN/support-kit3.3`. Read this file before changing anything.
It covers what was decided, what is in this package, how the parts fit together, what is
untested, and the work still to do, in order.

---

## 1. Context in five lines

- **Project.** EOSC EDEN (grant 101188015, 2025–2027). Task T3.3 builds a *support-kit*: practical guidance that helps communities adopt EDEN's digital-preservation framework.
- **Content model.** Each page is a **module** written as a user story ("As a *role*, I want to *task*, so that *benefit*"). It has a Diátaxis kind (how-to, tutorial, reference or explanation) and is anchored to WP1's 30 **Core Preservation Processes (CPPs)**, and later also to WP1's 74 **re-use fitness indicators** (§5b). It cross-walks to frameworks: CoreTrustSeal, nestor, ISO 16363, OAIS, PREMIS and EOSC FAIR metrics.
- **Roles.** Collapsed to three: `researcher` (depositor), `manager` (repository manager) and `trainer` (RDM trainer). `anyone` marks modules for every role.
- **Stack decision.** The existing vanilla-JS app on `main` is being **replaced** by a Jekyll site on the **ELIXIR Toolkit Theme (ETT) 7.0.0**, built the way RDMkit is. A vanilla-JS feature branch was rejected; don't extend `app.js`.
- **Authors write in Google Docs.** A GitHub workflow turns finished Docs into pull requests. Authors never use GitHub, Markdown or scripts.

## 2. Ground rules

1. **Branch: `ett`.** All support-kit work goes on `ett`. `main` keeps the old app until the cut-over in §9. Create `ett` from `main` if it doesn't exist (§8, step 1).
2. **Ask before pushing, force-pushing, opening PRs, or changing repository settings, secrets or variables.** The owner has stopped unrequested pushes before.
3. **Never override an ETT theme file.** Add new files instead: `_includes/kit-*.html`, `_layouts/module.html`, `_layouts/cpp.html`. Styling goes only in the three ETT hook files in `_sass/` and in `assets/js/custom.js`. RSQkit got stuck on ETT 6.0.0 because of overrides, so this rule is what keeps upgrades a version bump.
4. **ETT stays pinned:** `remote_theme: ELIXIR-Belgium/elixir-toolkit-theme@7.0.0`.
5. **Modules are pages, not a collection.** ETT's `type` comes from folder defaults, and `related_pages`, the sidebar and tiles depend on it.
6. **Scripts are Python and live in `var/`**, as in RDMkit and RSQkit.
7. **URLs are stable.** A page's URL is `/<page_id>`, set by `permalink: /:basename`. Never rename a file without a redirect (`jekyll-redirect-from` is installed).
8. **WP1 data is mirrored, never edited.** `_data/cpps.json` comes from `EOSC-EDEN/wp1-cpp-descriptions`.
9. **Content checks report, they never block.** One module with a problem must not stop the site from publishing.

## 3. What is in this package

The zip `eden-support-kit-ett-demo.zip` unpacks to `demo-site/`. Its contents are what goes onto `ett`:

```
_config.yml            ETT config: remote_theme, folder→type defaults, plugins, theme_variables, repository
Gemfile, .bundle/      ETT-example Gemfile; .bundle/config installs gems into vendor/bundle (no sudo)
.github/workflows/
  jekyll.yml           build on ett/main; checks + sidebar before build; deploy gated by KIT_DEPLOY
  gdocs-to-pr.yml      hourly: Google Docs in the "ready" folder → one PR per Doc
  sync-cpps.yml        weekly (Mon 05:23 UTC): WP1 CPPs → PR `bot/sync-cpps` with a change summary
_data/
  cpps.json            30 CPPs from WP1 (commit 09d93cc), with relationships and framework mappings
  indicators.json      WP1 M1.2 re-use fitness indicators: source + 3 pillars + metric counts; list still empty (§5b)
  frameworks.yml       framework ids (cts-2023, cts-2026, nestor, iso-16363, oais, premis, eosc-tf-fm)
  roles.yml            the three roles: id, plural label, ETT type, url, icon, blurb
  sidebars/main.yml    sidebar; sections with `folder:` have their module lists GENERATED
  topnav.yml, footer.yml, CONTRIBUTORS.yml (name → ORCID), tool_and_resource_list.yml (empty, RDMkit-style)
_layouts/module.html   extends ETT `page`: story subtitle, meta line, content, "Anchored to", prev/next
_layouts/cpp.html      extends ETT `page`: one CPP page; modules that teach / apply it, relations, mappings
_includes/kit-*.html   audience, story, meta, kind badge, connections, track nav, shared modules, module row, cpp chip,
                       kit-flow (interactive Google Docs → PR → site walkthrough; JS inline, CSS under .kit-flow)
_sass/                 _bootstrap_variables / _custom_variables / _custom_classes (EDEN brand, all custom CSS)
assets/js/custom.js    home picker + filters + list collapsing; tickable, printable checklists on modules
index.html             home: "I'm a … and I want to …" picker, role path cards, filterable user-story list
pages/                 role landing pages, contribute.md (author guide + walkthrough), cpps.md, indicators.md, frameworks.md, modules per role folder, pages/cpps/cpp_0NN.md (30 generated)
var/
  check_modules.py     front-matter report (annotations in CI; --strict to fail locally)
  make_sidebar.py      regenerates sidebar module lists from pages (CI runs it before every build)
  sync_cpps.py         WP1 XML → _data/cpps.json (+ runs make_cpp_pages.py); --summary FILE for the PR body
  make_cpp_pages.py    writes pages/cpps/cpp_0NN.md stubs from _data/cpps.json
  gdoc_to_module.py    Google Docs Markdown export → module page (forgiving; see §6)
  gdocs_sync.py        Drive folder ↔ workflow glue (list / convert / comment); adds anchor suggestions to PR bodies
  suggest_anchors.py   suggests CPPs/indicators from module text, with evidence; --audit, --sssom, --markdown (§5c)
  requirements-gdocs.txt
  tests/               test_gdoc_to_module.py + fixtures/: REAL Google Docs Markdown exports (v1, v2, messy)
README.md              run locally, writing modules, Google Docs pipeline setup
HANDOVER.md            this file
```

There are also files outside the zip. Treat them as background, not as the specification:

| File | Status |
|---|---|
| `PORTING.md` (v2) | The original port plan: a 38-row requirements traceability table and phases 0–6. Still useful as a checklist. Where it conflicts with this file, **this file wins**: the schema gained `cpps_primary`, `story.task` and `gdoc`; the sidebar is generated; checks don't block. |
| `DESIGN.md`, `taxonomy.yaml`, `generate_schema.py`, `schema.json` | Early content-model work. **Superseded** by the front matter in §5. `taxonomy.yaml` had placeholder CPP titles; WP1's `cpps.json` is the truth. |
| `support-kit-demo-functionality.patch` | The rejected vanilla-JS branch. Don't apply it. Only `scripts/sync-cpps.mjs` is worth reading, as the reference for the WP1 sync (§8, step 5). |
| `eden-kit-*.html`, `preview-*.png` | Early static mock-ups. Superseded by the ETT demo. |
| Demo build (claude.ai artifact) | A rendered preview of this site. It was built with a LiquidJS stand-in, not Jekyll (§7). |
| `docs-to-kit.html` | Standalone version of the pipeline walkthrough. It is now **built into the kit** as `/contribute` (`_includes/kit-flow.html`), so edit that include, not this file. |

## 4. How the site works

**Sections and roles.** Defaults in `_config.yml`, matched by folder, set `type`, `layout` and `sidebar`:

| Folder | `type` | Layout |
|---|---|---|
| `pages/getting_started/` | `Getting_started` | `module` (modules for every role) |
| `pages/researchers/` | `Researchers` | `module` |
| `pages/repository_managers/` | `Repository_managers` | `module` |
| `pages/rdm_trainers/` | `RDM_trainers` | `module` |
| `pages/cpps/` | `Core_preservation_processes` | `cpp`, `toc: false` |

**Home page (`index.html`, `layout: none`, assembled from ETT includes)**
- The **picker** reads "I'm *[role]* and I want to *[task]*", built from each module's `story.as` and `story.task` (falling back to `story.want`). Choosing a role filters both the task menu and the story list. It is hidden without JS.
- **Find your path** shows four cards (Everyone plus three roles). Each card shows the first four modules in order, a "+N more" link, and a 30-cell strip of the CPPs grouped by WP1 category: dark means taught (`cpps_primary`), light means applied (`cpps`), grey means not yet covered.
- The **user-story list** is grouped by track, with filters for role, kind ("Learn by doing / Get it done / Look it up / Understand why") and process. The filters are stored in the URL query (`?role=&kind=&cpp=`). Long groups show five rows until opened.
- ETT's Lunr search box is on the page.

**Module page (`_layouts/module.html`)**
- The module **title** is the h1, with ETT's section eyebrow above it. The user story is the subtitle.
- A meta line shows the audience ("For every role" with role pills, or "For *role*"), the kind badge with the Diátaxis term as a tooltip, the time needed, "N processes" and a draft/feedback link.
- Under the content, **Anchored to** shows "Teaches" (`cpps_primary`) and "Also applies" (`cpps`) on one side. On the other side it shows the frameworks the module cites (`satisfies`) and, folded away, the WP1 mappings inherited through its processes.
- Previous/next links move within the track (by `order`).
- **Checklists:** `- [ ]` items become tickable. Ticks are stored in localStorage. Each list gets a progress bar, Reset and Print checklist (which prints only the checklists and their headings).

**CPP page (`_layouts/cpp.html`)** is designed for many modules per process:
- A summary line: "N modules teach this process · applied in M more".
- **Start here** lists the modules that teach it.
- **Also applied in** lists the rest, grouped by role in collapsible sections that are folded when there are more than 8.
- A link filters the home list by this process. Related processes and WP1's framework mappings follow.

**Role pages** use ETT's `section-navigation-tiles`, plus "Shared with every role" (`kit-shared.html`).

**Sidebar.** `var/make_sidebar.py` rewrites the `subitems` of every section that has `folder:`. Menu labels use `nav_title`, or else the part of `title` before " – ". CI runs it before each build, so pull requests never edit the sidebar and never conflict on it.

**Liquid conventions** (these caused real bugs):
- Every variable inside a `kit-*` include is prefixed (`kn_`, `km_`, `kb_`, `ks_`, `kt_`, `ka_`, `ksh_`, `mr_`, `cu_`). Include variables leak into the caller.
- `where_exp` must use explicit comparisons (`"p.order != nil"`).
- ETT 7.0.0 has a typo, `{% else % %}`, in `_includes/resource-table-all.html`. Real Jekyll may tolerate it; report it upstream.

## 5. Module front matter (authoritative)

```yaml
---
title: Preparing deposits – file formats and technical data quality   # required; text before " – " is the menu label
description: One sentence for cards and search.
page_id: preparing_deposits        # = file name; no hyphens (ETT); also the URL /preparing_deposits
order: 1                           # position in the role path
kind: how-to                       # tutorial | how-to | reference | explanation
story:
  as: researcher                   # researcher | manager | trainer | anyone
  want: prepare my files for deposit, with sustainable formats, documentation and basic technical checks
  task: prepare my files for deposit   # ≤ 45 chars, home-page picker
  so_that: the dataset stays accessible, understandable and reusable beyond the original project
disciplines: [all]
data_types: [all]
keywords: [deposit, planning]
cpps: [CPP-001, CPP-002, CPP-003, CPP-004, CPP-010, CPP-027, CPP-030]   # every process it applies
cpps_primary: [CPP-010, CPP-001]   # 1–3 it mainly teaches; subset of cpps
satisfies:
  - {framework: cts-2026, code: R14}
  - {framework: eosc-tf-fm}
contributors: [Anna-Lena Flügel]   # keys of _data/CONTRIBUTORS.yml
related_pages:
  Repository_managers: [reviewing_deposits]   # ETT format: type → page_ids
status: draft                      # draft | ready
page_citation: true
gdoc: 1FBlwyqkM-…                  # set by the converter: source Google Doc id (don't edit)
nav_title: Preparing deposits      # optional sidebar label
effort: 20 min                     # optional
---
```

- The body starts with an opening paragraph. Sections are `##`.
- Recommendations are written as `- [ ]` items.
- References are listed under "More information".
- `var/check_modules.py` reports problems such as unknown CPP ids, more than 3 primaries, a primary missing from `cpps`, an unknown role or kind, an unknown framework, or more than 12 CPPs. It only fails with `--strict`.

## 5b. Second anchor: WP1 re-use fitness indicators (to build, same pattern as CPPs)

WP1 has a second set of reference items besides the CPPs. **M1.2, *Report on Metrics for
Information Object Re-Use Fitness*** (WP1 T1.2, CC BY 4.0, DOI
[10.5281/zenodo.21064927](https://doi.org/10.5281/zenodo.21064927), v1 30 June 2026; Zenodo
lists a newer version, so use the latest) defines:

- **74 indicators** in three pillars of a Re-Use Fitness Model:
  - **Content Data Quality (CDQ)**: 33
  - **Technical Data Quality (TDQ)**: 28
  - **Metadata Quality (MDQ)**: 13

  They were derived from ISO 25012 and refined with policies, standards and expert input.
- **618 candidate metrics** (403 generic, 215 data-specific). The report says these are candidates still to be validated, and that EDEN does not endorse them as requirements.
- Files: the report PDF, `EOSC_EDEN_M1-2_candidate-metrics.xlsx` and `EOSC_EDEN_M1-2_sources.xlsx`. There is no machine-readable repository like `wp1-cpp-descriptions` yet.

**Not known yet; check in the spreadsheet before building.** The exact ID scheme (`CDQ-01`?), the fields per indicator, and how metrics map to indicators. Ask the owner for the xlsx files (Zenodo can't be reached from every sandbox). Also confirm with the owner whether these are the same "quality indicators" that T3.2 pilots across seven disciplines; if so, T3.2's metric registry may be the better source.

**Already in the package:**
- `_data/indicators.json` holds the source, the three pillars (id, label, count, icon and a plain-language summary that is the kit's own wording) and the metric counts. Its `indicators: []` list is empty.
- `pages/indicators.md` (URL `/indicators`, linked from the top menu, the sidebar and the home "Explore" links) shows the three pillar cards, how the kit uses indicators, one section per pillar, the candidate-metrics caveat and the source.
- Each pillar section already lists `indicators` entries whose `pillar` matches the pillar's `label`, and links each to `/ind_<id>`. Until the list is filled, it shows a dashed "will be listed here" note.

Filling `indicators` is therefore the only change the page needs. Everything below adds the per-indicator pages and the module links.

**Design: an indicator is an anchor exactly like a CPP.** Generalise, don't copy:

1. **Data.** Add `var/sync_indicators.py`, which reads the M1.2 xlsx and writes `_data/indicators.json` in the same shape as `cpps.json`:
   ```json
   {"source": {"doi": "10.5281/zenodo.21064927", "version": "…", "file": "EOSC_EDEN_M1-2_candidate-metrics.xlsx"},
    "indicators": [{"id": "TDQ-05", "label": "…", "pillar": "Technical Data Quality",
                    "definition": "…", "iso25012": "…", "metrics": [{"id": "…", "text": "…", "scope": "generic|data-specific"}]}]}
   ```
   Keep the ids WP1 uses, and never edit the JSON by hand (same rule as `cpps.json`).
2. **Anchor sets.** Add `_data/anchor_sets.yml`, so templates loop over sets instead of hard-coding CPPs:
   ```yaml
   - {id: cpps, label: Core Preservation Processes, short: Processes, data: cpps, list: cpps,
      field: cpps, primary_field: cpps_primary, group_by: logical, page_prefix: cpp_, layout: cpp}
   - {id: indicators, label: Re-use fitness indicators, short: Indicators, data: indicators, list: indicators,
      field: indicators, primary_field: indicators_primary, group_by: pillar, page_prefix: ind_, layout: indicator}
   ```
   Then make the CPP-specific includes generic, keeping their prefixed variables:
   - `kit-connections.html`: one "Teaches / Also applies" block per set;
   - the home path-card strip: one strip per set, grouped by `group_by`;
   - the process filter becomes one filter per set, or one grouped select;
   - `kit-meta.html`: "N processes · M indicators".

   Rename `_layouts/cpp.html` to a generic `_layouts/anchor.html` that takes the set from front matter, or add `_layouts/indicator.html` that includes the same partials. Keep CPP URLs (`/cpp_0NN`) unchanged.
3. **Pages.** Extend `var/make_cpp_pages.py` (rename it to `make_anchor_pages.py`) to write `pages/indicators/ind_<id>.md` as well. Add a `_config.yml` default for `pages/indicators/` (`type: Re-use_fitness_indicators`, `layout: indicator`, `toc: false`), an index page `pages/indicators.md` grouped by pillar, plus a topnav and sidebar entry. On an indicator page, show the definition, the pillar, the ISO 25012 link, the **candidate metrics** (folded, with the report's "candidate, not endorsed" caveat), and the "In the support-kit" block built for scale, as on CPP pages.
4. **Front matter.** Two optional fields: `indicators: [...]` (every indicator the module helps with) and `indicators_primary: [...]` (1–3 it mainly addresses, a subset). `check_modules.py` validates them against `indicators.json` the same way, and reports rather than blocks.
5. **Google Docs template and converter.**
   - **Template:** add rows "Main indicator 1–3" (dropdowns listing `TDQ-05 · <label>`, grouped by pillar if the dropdown allows) and "Other indicators it supports" (free text).
   - **`gdoc_to_module.py`:** map those labels to `indicators_primary` / `indicators`; generalise `cpp_ids()` into an anchor matcher (id, number or name, fuzzy, flagged) driven by `anchor_sets.yml`.
   - **Tests:** add fixtures to `var/tests/`.

   The template change needs the owner (dropdowns are added by hand in Google Docs).
6. **Why it's worth it.** CPPs say *what the repository does*; indicators say *what makes the data fit for re-use*. A module anchored to both shows researchers how their preparation affects re-use (CDQ, MDQ). It shows managers which checks support which processes (TDQ ↔ CPP-010 and the like). The coverage strips then show gaps on both axes.

## 5c. Suggested links and crosswalks (lightweight ML, people decide)

The kit links three kinds of things: modules, WP1 processes (CPPs) and WP1 indicators, plus external frameworks. Hand-tagging every module against 30 processes and 74 indicators doesn't scale, and authors will miss links. Light, explainable text matching **suggests** links. It never applies them.

**Built (prototype):**
- The corpus is the `text` field of `_data/cpps.json` (filled by `var/sync_cpps.py`). The earlier `build_anchor_corpus.py` / `var/anchors/cpps.json` was unused and has been removed.
- `var/suggest_anchors.py page.md` gives the top processes for a module using TF-IDF (unigrams and bigrams), field weighting and a boost when a process is named outright. Every suggestion lists the words that matched.
  - `--eval` compares against the hand tags.
  - `--crosswalk A B` writes candidate mappings between two sets as **SSSOM** TSV.
- **In the pipeline:** `gdocs_sync.py convert` adds "Possibly related processes", up to four with score and matched words, to the pull request. Reviewers or authors add them in the Doc if they fit.

**Measured, and it's weak:** precision@5 is 0.33 against the hand tags of three modules, too few to tune on. Some misses are the suggester being right: it proposes CPP-019 Data Quality Assessment for preparing deposits, which the hand tags lack. But the scores are low (0.04–0.25) and it picks up archive-speak noise. Treat it as a reviewer aid, not a classifier.

**Next steps, in order:**
1. **Grow the gold set for free.** Every merged module's `cpps` and `cpps_primary` are labels. Keep `--eval` in CI as a report and watch precision@5 as modules arrive.
2. **Add a small sentence-embedding model and blend it with TF-IDF.** TF-IDF can't see that "checksums" relates to "integrity", but an embedding model can.
   - **Model:** a multilingual one also handles modules not written in English. `intfloat/multilingual-e5-small` (about 120 MB) or `sentence-transformers/all-MiniLM-L6-v2` (about 90 MB, English), run on CPU through `fastembed` (ONNX, no PyTorch).
   - **Speed:** cache the anchor vectors in `var/anchors/*.npy`, so suggesting for one module takes milliseconds.
   - **Blend:** `0.7·embedding + 0.3·tfidf`, then tune on the gold set.
   - The model downloads from Hugging Face in Actions; the sandbox this was built in couldn't reach it, so it is untested.
   - Keep `score()` as the only place where the scoring method changes.
3. **An LLM only as an opt-in reviewer aid,** for example a one-paragraph rationale per suggestion. It stays off by default and runs behind a repository secret. Check the data-handling policy first: module drafts may be unpublished.

**Crosswalks as data (the ontology-mapping part):**
- **Format.** Store mappings as [SSSOM](https://mapping-commons.github.io/sssom/) TSV files in `_data/mappings/`, for example `cpp-indicator.sssom.tsv` and `indicator-framework.sssom.tsv`.
  - Predicates come from SKOS: `skos:closeMatch`, `skos:relatedMatch`, `skos:broadMatch`, `skos:narrowMatch`.
  - Provenance comes from SEMAPV: `semapv:LexicalMatching` or `semapv:SemanticSimilarityThresholdMatching` for machine candidates, `semapv:ManualMappingCuration` plus an ORCID in `author_id` for reviewed rows.
- **Workflow.** `suggest_anchors.py --crosswalk cpps indicators` writes the candidates. WP1 or T3.2 experts curate them in a spreadsheet or a PR. **The site uses curated rows only.**
- **Payoff.**
  - Modules **inherit** indicators through their processes, the way they already inherit framework codes through WP1's CPP mappings, so authors tag less.
  - The mappings are a FAIR output in their own right: SSSOM converts to SKOS/JSON-LD for EOSC.
- `check_modules.py` can then flag modules whose text strongly suggests a process they don't link, as a report.

## 5c. Suggesting anchors and crosswalks automatically (light ML, people decide)

Tagging modules with CPPs and, later, indicators by hand doesn't scale, and the audit below shows it drifts. `var/suggest_anchors.py` suggests anchors from a module's own text. It **never writes tags**. Suggestions go into the bot's PR body ("Suggested anchors") with the sentence that triggered each one, and authors or reviewers decide.

**How it works:** retrieve, explain, let a person decide.
- Each CPP is one document: its label, short definition and WP1's description, purpose, inputs and outputs. That text is now stored in `_data/cpps.json` as `text`, filled by `var/sync_cpps.py` (all purposes included, no length cap).
- Each module is split into passages: its title and user story, then each paragraph and bullet. References are left out.
- Every passage is scored against every anchor. An anchor's score is 0.7 × its best passage plus 0.3 × the average, so one clear sentence counts as strong evidence.
- Below a threshold the tool **abstains**. Orientation and training modules rightly get no suggestion.
- Backends:
  - `tfidf` is the default: scikit-learn, no downloads, a fraction of a second in CI.
  - `embeddings` uses `model2vec` (`minishlab/potion-base-8M`, static and CPU-only) or `sentence-transformers` (`BAAI/bge-small-en-v1.5`). Use it when a CI runner can download the model. It handles the vocabulary gap between researcher wording ("my files") and WP1's archive wording ("the TDA validates Files") much better than word overlap.
- Thresholds (`THRESHOLD`) are starting values. Tune them once there are 15–20 modules with tags people agree on.

**Output is a crosswalk record, not just a list.** `--sssom FILE` writes an SSSOM-style table (Simple Standard for Sharing Ontological Mappings). Each link carries `mapping_justification`: `semapv:LexicalSimilarityThresholdMatching` or `SemanticSimilarityThresholdMatching` for the tool, `semapv:ManualMappingCuration` for a person. It also records a confidence, the tool and the evidence sentence. That makes each module–CPP link auditable, and the same format can later hold:
- **CPP ↔ indicator** crosswalks, suggested by the same matcher run between the two sets and curated by WP1;
- **module ↔ framework** links, which today come from `satisfies` plus WP1's CPP mappings.

The predicate is `skos:relatedMatch` for suggestions. Curated links can be typed more precisely (the module teaches, applies, or prepares the producer side for a process).

**First audit** (TF-IDF, current demo content; `python3 var/suggest_anchors.py --all --audit`):
- **Enabling discovery:** the tool confirms CPP-005 and CPP-024, which are the module's main processes. 7 of its 9 tags have little support in the text.
- **Reviewing deposits:** it confirms CPP-010, CPP-012 and CPP-023. It suggests CPP-029 Ingest and CPP-019 Data Quality Assessment, which aren't tagged. 4 of its 14 tags are unsupported.
- **Preparing deposits:** none of its 7 tags is supported by the text, including both main processes (CPP-010, CPP-001). The text is about formats and quality, and the tool suggests CPP-008 File Format Identification and CPP-019 Data Quality Assessment. This supports the "placeholders need author sign-off" note in §8.
- **Navigating the kit and Resources for trainers:** the tool abstains, correctly.

Five modules are far too few to measure precision, so treat this as a sanity check. Re-run the audit as content grows, and report precision@3 against curated tags before relying on scores.

**Next steps, in order:**
1. Keep TF-IDF in the bot PRs now. It's already wired in, and `scikit-learn` has been added to `var/requirements-gdocs.txt`.
2. Add indicators: the script reads `_data/indicators.json` automatically once its list is filled (fields `label`, `definition`, `text`).
3. Try the `embeddings` backend in CI and compare with `--audit`.
4. Optional, only with a decision on data and hosting: re-rank the top 10 with a small instruction-tuned LLM, asked to pick 1–3 and justify them from the module text. This is the retrieve-then-rerank pattern of LLMs4OM and recent OAEI LLM-based matchers. Keep it self-hosted or EU-hosted, keep the output as suggestions, and log it with its own `mapping_tool`.
5. Once there are a few dozen curated links, a few-shot classifier (SetFit) trained on them can replace the thresholds.

## 6. Authoring pipeline: Google Docs → pull request → site

**Google Drive items** (owned by the project owner's Drive; move them to a shared drive when the team is ready):

| Item | ID |
|---|---|
| **Template v2 (use this)**: "EDEN Support-kit – module template (v2)", with dropdowns for Role, Kind of help, Main process 1–3 and Status | `16JsiG9edwKCt3cuaTMEdR3kISEdrFYqT3MPK489iLys` |
| Worked example: "EDEN Support-kit – example module (Preparing deposits)", old v1 table layout but still converts | `1FBlwyqkM-S8QlRBxH58q8z9H-2KLo3ufBdt3yJwDeEc` |
| Ready folder: "EDEN Support-kit – ready for the kit" | `1qTIuQq-G62Bf6-CZgTxH-C4KevIcWnGI` |
| Old template v1: should be trashed or renamed "old" by the owner | `1us82PGa7Na80dTGEmpkTDJH8Vf-3CIpCmq_ZRz8U6G0` |

**Flow** (`.github/workflows/gdocs-to-pr.yml`)
1. **Find (hourly at :17, or a manual run with one Doc link).** Lists the Docs in the ready folder. A Doc is processed if it was edited in the last 75 minutes, or if the kit has never seen it: no page with its `gdoc:` id on `KIT_BRANCH` and no open `gdocs/<docId>` branch. The second rule catches Docs that were moved in (moving doesn't change the modified time) and Docs still waiting on a fix.
2. **Module (matrix, one job per Doc).**
   - `gdocs_sync.py convert` exports the Doc as `text/markdown` through the Drive API and runs `gdoc_to_module.py --source-id <docId>`.
   - **Success:** `peter-evans/create-pull-request@v7` opens or updates a PR from branch `gdocs/<docId>` into `KIT_BRANCH`. The PR body lists "Points to check" and a review checklist, with the labels `from-google-docs` and, when defaults were used, `needs-attention`.
   - The first time a PR is created, the author gets a Doc comment with the link and the points to check.
   - **Failure:** the only failure is a missing title or deleted template headings. The author gets a Doc comment saying what to fix. Identical comments are not repeated.
3. **Merge → site build** (`jekyll.yml`): `check_modules.py`, then `make_sidebar.py`, then the Jekyll build, then deploy (when enabled).

**What `gdoc_to_module.py` handles**
- **Google's export quirks:** bold headings, lists exported as `> *`, backslash escapes (`\_ \[ \: \>`), bare URLs (turned into `<url>`), inline base64 images (saved to `assets/img/modules/<page_id>-N.ext`), template guidance sentences, lines still on `[placeholder]`, and sections left empty.
- **Loose values from authors:**
  - roles and kinds are matched by keyword, which also covers the dropdown texts;
  - CPPs can be given as `CPP-010`, `10`, `010 · File Format Validation` or a name, matched fuzzily and flagged;
  - frameworks by name ("CoreTrustSeal R14 R09", "ISO 16363: 4.2");
  - order as "2nd";
  - status containing "ready";
  - related modules by title or `page_id`;
  - contributors as person chips or `[name](mailto:…)`;
  - "As a …, I want to …" is stripped back to the bare task;
  - rows "Main process 1/2/3" and "Other process N" are merged into one list.
- **Page identity:**
  - The same Doc under a new title or role replaces its old page (it is found by `gdoc:`).
  - A second Doc with the same title gets `<page_id>_2` and a warning.
  - Replacing a page that was hand-edited in the repo is allowed, with a warning.

**One-time setup** (repository admin; ask the owner before touching settings)
1. A Google Cloud service account with the **Drive API** enabled, and a JSON key.
2. Share the ready folder with the service account as **Commenter**.
3. Repository secret `GDRIVE_SA_KEY` (the whole JSON) and repository variable `GDRIVE_READY_FOLDER=1qTIuQq-G62Bf6-CZgTxH-C4KevIcWnGI`.
4. Repository variable `KIT_BRANCH=ett`. Later this becomes `main`, or is deleted, since `ett` is the default.
5. Settings › Actions › General › Workflow permissions: allow GitHub Actions to create and approve pull requests.
6. Optional: secret `KIT_BOT_TOKEN` (a fine-grained PAT or GitHub App token with contents and pull-requests write). PRs opened with `GITHUB_TOKEN` don't trigger `jekyll.yml`, so without it the build check won't run on bot PRs.

## 7. What was verified, and what was not

**Verified in the sandbox**
- The full site renders through a **Node stand-in for Jekyll**: LiquidJS 10 with `jekyllInclude`, markdown-it with task lists, Dart Sass, rendering ETT 7.0.0 unmodified.
- No JS errors.
- No horizontal overflow at 390 px.
- Search works with real keystrokes.
- Filters, the picker, checklist persistence and print mode work.
- A scale test with 64 synthetic modules exercised the CPP pages, path cards and list collapsing.
- The converter was run on **real Google exports**: v1 template, v2 template, filled and empty, plus messy, colliding and renamed Docs.
- `gdocs_sync.py convert` was simulated with a mocked export.
- `actionlint` passes on both workflows.
- `python3 var/tests/test_gdoc_to_module.py` passes (13 checks on real exports). Run it after any converter change, and consider adding it to `jekyll.yml` on pull requests.

**Not verified. Do these first (§8):**
1. **A real `bundle exec jekyll build`.** RubyGems was blocked in the sandbox. Check that:
   - kramdown task lists render as `ul.task-list > li.task-list-item > input`. Both the CSS and `custom.js` already select `.contains-task-list` and `.task-list`;
   - heading IDs suit ETT's `toc.js`; the stand-in stripped leading digits, kramdown's `auto_ids` does the same;
   - ETT's `{% else % %}` typo doesn't break the build;
   - `jekyll-github-metadata` works. It needs `repository:` in `_config.yml`, which is set, plus `JEKYLL_GITHUB_TOKEN` or network access;
   - `sort: "order"` and `where_exp` behave the same as in LiquidJS.
2. **The live Drive → PR run.** It needs the secrets above, and has never run against the real Drive API or GitHub.
3. **Whether the v2 template's dropdowns survived the docx → Google Docs conversion.** The text did. If they are plain text, the owner adds them by hand once (Insert › Dropdown, about two minutes; the options are in the README). The converter works either way.
4. **The public-link fallback** (`/export?format=md` when there is no service-account key). Treat it as best-effort.

**Locally the owner hit two problems, both fixed:**
- `Bundler::PermissionError` writing to `/var/lib/gems`. Fixed by `.bundle/config` (`vendor/bundle`) and `sudo apt install ruby-dev build-essential zlib1g-dev libyaml-dev`.
- "No repo name found". Fixed by `repository: EOSC-EDEN/support-kit3.3` in `_config.yml`.

If `prism` still fails to build, drop `jemoji`: it is unused, and it is what pulls in activesupport and prism.

## 8. Work to do, in order

1. **Create `ett`.** Branch from `main`. Remove the old app files from `ett` only, then copy in `demo-site/` (without `vendor/`). Keep the repository-level files (LICENSE, CITATION.cff and so on).
   - The old app is Markdown articles plus `build-index.mjs`, `index.json`, `app.js` (about 950 lines), `editor.html` and markdown-it.
   - Make one commit with a clear message, then **show the diff summary and ask before pushing**.
2. **Port all content from the old app.**
   - The six demo modules were drawn from the old articles, but probably not all of them were. Diff the old article set against `pages/` and port anything missing into the §5 front matter.
   - Never invent `cpps_primary`. Where the article doesn't make it obvious, leave it out and list it for the owner. The current values in three modules are **placeholders that need author sign-off**:
     - Preparing deposits: CPP-010, CPP-001
     - Reviewing deposits: CPP-010, CPP-002, CPP-007
     - Enabling discovery: CPP-024, CPP-005
3. **Build with real Jekyll** (`bundle install && bundle exec jekyll serve`). Go through §7.1 and compare against the demo artifact. Fix differences in `kit-*` files, never in theme files.
4. **Regenerate the CPP stubs** if needed with `python3 var/make_cpp_pages.py`, and run `var/check_modules.py` and `var/make_sidebar.py`.
5. **~~Add `var/sync_cpps.py`~~ Done.** Parses the per-CPP XML with ElementTree (the old JS regex parser also picked up commented-out relationships, e.g. CPP-006 "Triggers CPP-002"). Writes only when CPP content changes, so WP1 commits that don't touch CPPs open no PR. `sync-cpps.yml` runs weekly; like `gdocs-to-pr.yml`, it needs a copy on the default branch while `ett` isn't default.
6. **Wire up the Google Docs pipeline** (§6 setup). Have the owner run it by hand once with the worked-example link. While `ett` is not the default branch, **schedules don't fire from `ett`**, so propose putting a copy of `gdocs-to-pr.yml` on the default branch. It already checks out `KIT_BRANCH`.
7. **Preview deploys.** `jekyll.yml` builds on `ett` but only deploys when `KIT_DEPLOY=true`. The repository has one Pages site, so deploying from `ett` replaces what `main` publishes. Before turning it on, ask whether that's acceptable now or whether a preview elsewhere is wanted (for example a separate preview repository, or Netlify or Cloudflare Pages on `ett`). If deploying from `ett`, the `github-pages` environment's branch rules must allow `ett`.
8. **Report the ETT typo upstream** (ELIXIR-Belgium/elixir-toolkit-theme, `resource-table-all.html`), once the owner agrees.
9. **Link suggestions (§5c):** keep `--eval` running as modules arrive. Add the embedding model, then indicators to the corpus, then curated SSSOM crosswalks.
10. **Indicators as a second anchor (§5b).** First get the M1.2 spreadsheet from the owner and confirm the ID scheme. Then build in this order: sync script → `indicators.json` → anchor-set generalisation, keeping CPP output byte-identical (diff the built site before and after) → indicator pages → front matter and checks → converter → template rows.
11. **Nice to have,** proposed in design reviews and not built:
   - group role paths by OAIS stage, derived from the primary CPPs' `oais` field;
   - remember the reader's chosen role across pages, with a "Your path: step 2 of 5" bar;
   - a small relationship diagram on CPP pages;
   - a CPP × role coverage matrix on `cpps.md`.

## 9. Cut-over: `ett` becomes `main`

When the owner says the ETT site replaces the old app:
1. Tag the last commit of the old app on `main` (for example `vanilla-final`).
2. Merge `ett` into `main` (or reset `main` to `ett`, if the owner prefers clean history). Add redirects (`redirect_from:`) for any old app URLs that people link to.
3. Set `KIT_BRANCH=main` (or delete it once `main` is the target) and `KIT_DEPLOY=true`. Remove the duplicate scheduled workflow copy if one was added.
4. Make sure Pages deploys from the workflow and the `github-pages` environment allows `main`.
5. Update `github.source.branch` in `_config.yml` (currently `main`, which is already right for after the cut-over), and the edit/issue links if needed.
6. Delete `ett`, or keep it protected for a release or two.

## 10. Open decisions (owners, not code)

- **`cpps_primary` values** for the existing modules need author sign-off (§8, step 2).
- **CoreTrustSeal version:** some modules cite 2023–2025 (`cts-2023`), others 2026–2028 (`cts-2026`). Decide per module.
- **Licensing of contributed content:** CC BY 4.0 is assumed in the footer. Confirm with WP5, especially for external contributions.
- **Discipline and data-type vocabularies:** free text now. Align with T3.2's list when it exists.
- **Hosting after the project:** Codeberg is planned. Forgejo Actions accepts most of these workflows, but `peter-evans/create-pull-request` and GitHub Pages need replacements.
- **Moving the Drive items to a shared drive** owned by the project.
- **Anchor suggestions:** agree with WP1 and WP3 that tool-made links stay suggestions until a person accepts them, and who curates the CPP ↔ indicator crosswalk.
- **Indicators:** confirm the M1.2 indicator IDs and whether module authors should tag indicators from the start or only after the T3.2 pilots. Decide whether candidate metrics are shown at all, given that the report doesn't endorse them.

## 11. References

- WP1 M1.2 re-use fitness indicators and metrics: https://doi.org/10.5281/zenodo.21064927
- WP1 CPP descriptions: https://github.com/EOSC-EDEN/wp1-cpp-descriptions (pages at https://eosc-eden.github.io/wp1-cpp-descriptions/), M1.1 DOI 10.5281/zenodo.16992452
- ETT: https://github.com/ELIXIR-Belgium/elixir-toolkit-theme (7.0.0) · example site: https://github.com/ELIXIR-Belgium/elixir-toolkit-theme-example
- RDMkit (structure and editorial machinery, zero overrides): https://github.com/elixir-europe/rdmkit
- RSQkit (layout extending `page`, quality indicators ≈ CPP pages): https://github.com/EVERSE-ResearchSoftware/RSQKit
- Diátaxis: https://diataxis.fr
- SSSOM (mapping format): https://arxiv.org/abs/2112.07051 · LLMs4OM (LLM ontology matching): https://arxiv.org/abs/2404.10317 · SetFit (few-shot): https://arxiv.org/abs/2209.11055
- EDEN brand colours (from the official logo): teal `#008691`, pink `#eb5d81`, ink `#1d2327`.
