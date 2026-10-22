# Contributing with AI tools

AI assistants help build and maintain this kit. This page says how we use them, so the
results stay trustworthy. It is also the project's disclosure of AI use.

## Local and public models

What decides which model you may use is **where the text goes**, not which model it is.

**Local models** run on your own machine or on project-controlled servers, so nothing leaves
them. Examples: **Qwen** (including Qwen Coder), Llama, Mistral's open models, DeepSeek, run with
Ollama, LM Studio or vLLM. Use these for anything not yet public: unpublished material, personal data, internal
documents.

**Public models** are hosted services run by a company. Examples: **Claude** (Anthropic; Claude
Code, claude.ai, API), ChatGPT and the OpenAI API, Gemini, GitHub Copilot, Mistral Le Chat, and
Qwen when used through Alibaba Cloud's API. Use them for material that is already public or meant
to be: this repository's code, workflows and published pages. For anything else, ask the data owner
first and check the service's data-use and retention terms.

| | Local | Public |
|---|---|---|
| Data leaves our control | No | Yes |
| Unpublished material, personal data | Yes | Only with the owner's agreement |
| Repository code and published content | Yes | Yes |

Coding agents should read [`AGENTS.md`](AGENTS.md) first: it holds the rules, layout,
commands and front-matter format. Point your tool at it. In Claude Code, a local
`CLAUDE.md` containing `@AGENTS.md` does this; don't commit tool-specific config files.

## Standards

1. **A person is responsible.** Whoever opens the pull request has read and understood every
   line, and can explain it in review. "The model wrote it" is not a reason to merge.
2. **Facts are checked against sources.** Never accept a CPP id, indicator, framework code
   (CoreTrustSeal, nestor, ISO 16363…), reference or URL from a model without checking it
   against `_data/` or the original source. Never invent `cpps_primary`.
3. **Suggestions stay suggestions.** Machine-made links between modules, CPPs and indicators
   (`var/suggest_anchors.py` or any model) are only proposals until a person accepts them.
4. **Mind what you paste.** Never send secrets or tokens to any model. Unpublished material and
   personal data go to local models only, unless the data owner agrees (see above).
5. **Licensing.** Generated content must fit the kit's licences (CC BY 4.0 for content). Don't
   ask a model to reproduce copyrighted text, and don't paste such text in.
6. **Same checks as human work.** Run `python3 var/check_modules.py`, the converter tests after
   converter changes, and build the site (`bundle exec jekyll build`) before opening a PR.
7. **Small, reviewable changes.** One purpose per pull request; no unrequested rewrites or
   new dependencies.

## Disclosure

This file is the project-level disclosure, so commits don't carry AI co-author trailers.
When a large part of a pull request was generated, say so briefly in its description
(which tool, for what).
