# Contributing with AI tools

AI assistants help build and maintain this kit. This page says how we use them, so the
results stay trustworthy. It is also the project's disclosure of AI use.

## Tools we use

- **Claude** (Anthropic), mostly through Claude Code, for code, workflows and documentation.
- **Qwen** (Alibaba), including Qwen Coder models, which can run locally or self-hosted
  (for example with Ollama or vLLM). Prefer these when the text must not leave our machines.
- **Others** are fine (GPT, Gemini, Mistral, GitHub Copilot and so on) under the same rules.

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
4. **Mind what you paste.** Don't send secrets, tokens, personal data or unpublished module
   drafts to a hosted model unless the data owner agrees. Use a local or EU-hosted model
   when in doubt.
5. **Licensing.** Generated content must fit the kit's licences (CC BY 4.0 for content). Don't
   ask a model to reproduce copyrighted text, and don't paste such text in.
6. **Same checks as human work.** Run `python3 var/check_modules.py`, the converter tests after
   converter changes, and build the site (`bundle exec jekyll build`) before opening a PR.
7. **Small, reviewable changes.** One purpose per pull request; no unrequested rewrites or
   new dependencies.
8. **Keep the authors' voice.** Modules are written by their authors in Google Docs. A model
   may help edit, but the author signs off on the content.

## Disclosure

This file is the project-level disclosure, so commits don't carry AI co-author trailers.
When a large part of a pull request was generated, say so briefly in its description
(which tool, for what).
