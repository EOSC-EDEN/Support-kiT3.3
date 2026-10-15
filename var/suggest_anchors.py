#!/usr/bin/env python3
"""Suggest which WP1 anchors (Core Preservation Processes, later re-use fitness indicators)
a module relates to, with the sentence that triggered each suggestion.

Suggestions only: nothing is written into a module. Authors and reviewers decide. Output is
a SSSOM-style mapping table, so every link records how it was made (lexical match, embedding
match, or a person) and how confident it is.

Method (retrieve, explain, let a person decide):
  1. Each anchor is a document: label (weighted), short definition, and WP1's description,
     purpose, inputs and outputs (`text` in _data/cpps.json).
  2. A module is split into passages: its title + user story, then each paragraph and bullet.
     References ("More information") are left out; they name sources, not tasks.
  3. Every passage is scored against every anchor. An anchor's score is mostly its best
     passage (one clear sentence is strong evidence) plus a little of its average.
  4. Below a threshold the tool abstains: no suggestion is better than a weak one.

Backends:
  tfidf       default, no downloads, runs anywhere (scikit-learn)
  embeddings  sentence embeddings if `model2vec` or `sentence-transformers` is installed and the
              model can be downloaded (e.g. minishlab/potion-base-8M, BAAI/bge-small-en-v1.5).
              Handles vocabulary mismatch ("my files" vs "the TDA's Files") far better.

Usage (repository root):
  python3 var/suggest_anchors.py pages/researchers/preparing_deposits.md    one module, readable
  python3 var/suggest_anchors.py --all --audit                              compare with current tags
  python3 var/suggest_anchors.py --all --sssom suggestions.sssom.tsv        mapping table
  python3 var/suggest_anchors.py FILE --markdown                            block for a PR body
"""
import argparse, json, pathlib, re, sys
import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
SETS = [  # anchor sets; indicators join when _data/indicators.json has a list
    {"id": "cpps", "file": "_data/cpps.json", "list": "cpps", "field": "cpps", "primary": "cpps_primary",
     "name": "Core Preservation Processes", "prefix": "eden.cpp"},
    {"id": "indicators", "file": "_data/indicators.json", "list": "indicators", "field": "indicators",
     "primary": "indicators_primary", "name": "Re-use fitness indicators", "prefix": "eden.ind"},
]
THRESHOLD = {"tfidf": 0.035, "embeddings": 0.45}   # abstain below; tune on curated tags (see --audit)


def load_anchors():
    out = []
    for s in SETS:
        p = ROOT / s["file"]
        if not p.exists():
            continue
        items = json.loads(p.read_text())[s["list"]] or []
        for a in items:
            doc = " ".join([(a.get("label", "") + " ") * 3, (a.get("shortDefinition") or a.get("definition") or "") * 2,
                            a.get("text", "")])
            out.append({"set": s["id"], "id": a["id"], "label": a.get("label", ""), "doc": doc})
    return out


def module_passages(path):
    t = path.read_text(encoding="utf-8")
    fm = yaml.safe_load(t.split("---", 2)[1]) or {}
    body = re.sub(r"(?ms)^## More information.*", "", t.split("---", 2)[2])
    story = fm.get("story") or {}
    head = f"{fm.get('title', '')}. {story.get('want', '')}. {story.get('so_that', '')}"
    parts = [head] + [re.sub(r"^\s*-\s*(\[[ x]\]\s*)?", "", p).strip()
                      for p in re.split(r"\n\s*\n|\n(?=\s*- )", body)]
    parts = [re.sub(r"[#*_`>]|\[([^\]]*)\]\([^)]*\)", r"\1", p).strip() for p in parts]
    return fm, [p for p in parts if len(p) > 25]


class Scorer:
    def __init__(self, anchors, corpus, backend):
        self.anchors, self.backend = anchors, backend
        if backend == "embeddings":
            self.model = self._model()
            self.A = self._embed([a["doc"] for a in anchors])
        else:
            from sklearn.feature_extraction.text import TfidfVectorizer
            self.vec = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), sublinear_tf=True)
            self.vec.fit([a["doc"] for a in anchors] + corpus)
            self.A = self.vec.transform([a["doc"] for a in anchors])

    def _model(self):
        try:
            from model2vec import StaticModel
            return ("m2v", StaticModel.from_pretrained("minishlab/potion-base-8M"))
        except Exception:
            from sentence_transformers import SentenceTransformer
            return ("st", SentenceTransformer("BAAI/bge-small-en-v1.5"))

    def _embed(self, texts):
        import numpy as np
        kind, m = self.model
        E = m.encode(texts) if kind == "m2v" else m.encode(texts, normalize_embeddings=True)
        return E / (np.linalg.norm(E, axis=1, keepdims=True) + 1e-9)

    def score(self, passages):
        import numpy as np
        if self.backend == "embeddings":
            S = self._embed(passages) @ self.A.T
        else:
            from sklearn.metrics.pairwise import cosine_similarity
            S = cosine_similarity(self.vec.transform(passages), self.A)
        return 0.7 * S.max(0) + 0.3 * S.mean(0), S.argmax(0)


def suggest(path, scorer, top, backend):
    fm, passages = module_passages(path)
    score, best = scorer.score(passages)
    order = sorted(range(len(score)), key=lambda i: -score[i])
    out = []
    for i in order:
        if score[i] < THRESHOLD[backend] or len(out) >= top:
            break
        a = scorer.anchors[i]
        out.append({"set": a["set"], "id": a["id"], "label": a["label"], "score": float(score[i]),
                    "evidence": passages[best[i]][:200]})
    return fm, out, {scorer.anchors[i]["id"]: float(score[i]) for i in range(len(score))}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("modules", nargs="*")
    ap.add_argument("--all", action="store_true", help="every module under pages/")
    ap.add_argument("--backend", choices=["tfidf", "embeddings"], default="tfidf")
    ap.add_argument("--top", type=int, default=5)
    ap.add_argument("--audit", action="store_true", help="compare suggestions with each module's current tags")
    ap.add_argument("--sssom", help="write a SSSOM-style TSV of all suggestions")
    ap.add_argument("--markdown", action="store_true", help="print a block for a pull-request body")
    a = ap.parse_args()

    files = [pathlib.Path(m) for m in a.modules]
    if a.all:
        files = [f for f in sorted((ROOT / "pages").glob("*/*.md")) if f.parent.name not in ("cpps", "indicators")]
    if not files:
        sys.exit("give module files, or --all")
    anchors = load_anchors()
    corpus = [p for f in files for p in module_passages(f)[1]]
    scorer = Scorer(anchors, corpus, a.backend)

    rows = []
    for f in files:
        fm, sugg, allscores = suggest(f, scorer, a.top, a.backend)
        pid = fm.get("page_id", f.stem)
        tagged = set(fm.get("cpps") or []) | set(fm.get("indicators") or [])
        primary = set(fm.get("cpps_primary") or []) | set(fm.get("indicators_primary") or [])
        for s in sugg:
            rows.append((pid, s))
        if a.markdown:
            print("**Suggested anchors** (automatic, for the author and reviewer to confirm or ignore)\n")
            if not sugg:
                print("- No clear match. That is normal for orientation or training modules.")
            for s in sugg:
                mark = " ✓ already tagged" if s["id"] in tagged else ""
                print(f"- **{s['id']} {s['label']}**{mark}, because: “{s['evidence']}”")
            continue
        print(f"\n{pid}" + (f"   tagged: {', '.join(sorted(tagged))}" if tagged else "   (no tags)"))
        if not sugg:
            print("  no suggestion above the threshold (abstains)")
        for s in sugg:
            mark = "✓" if s["id"] in tagged else "+"
            print(f"  {mark} {s['id']} {s['label'][:38]:38} {s['score']:.3f}  “{s['evidence'][:80]}”")
        if a.audit and tagged:
            weak = sorted((allscores.get(t, 0), t) for t in tagged if allscores.get(t, 0) < THRESHOLD[a.backend])
            for sc, t in weak:
                star = " (main)" if t in primary else ""
                print(f"  ? {t}{star}: tagged, but the text gives little support ({sc:.3f}); check the tag or add the missing explanation")

    if a.sssom:
        with open(a.sssom, "w", encoding="utf-8") as fh:
            # Local prefixes until WP1 mints persistent identifiers for CPPs and indicators.
            fh.write("# mapping_set_id: https://eosc-eden.github.io/support-kit/mappings/anchor-suggestions.sssom.tsv\n"
                     "# license: https://creativecommons.org/licenses/by/4.0/\n# curie_map:\n"
                     "#   eden.mod: https://eosc-eden.github.io/support-kit/\n"
                     "#   eden.cpps: https://eosc-eden.github.io/wp1-cpp-descriptions/#\n"
                     "#   eden.indicators: https://doi.org/10.5281/zenodo.21064927#\n"
                     "#   semapv: https://w3id.org/semapv/vocab/\n#   skos: http://www.w3.org/2004/02/skos/core#\n")
            fh.write("subject_id\tsubject_label\tpredicate_id\tobject_id\tobject_label\tmapping_justification\t"
                     "confidence\tmapping_tool\tcomment\n")
            just = "semapv:LexicalSimilarityThresholdMatching" if a.backend == "tfidf" else "semapv:SemanticSimilarityThresholdMatching"
            for pid, s in rows:
                fh.write(f"eden.mod:{pid}\t\tskos:relatedMatch\teden.{s['set']}:{s['id']}\t{s['label']}\t{just}\t{s['score']:.3f}\t"
                         f"suggest_anchors.py/{a.backend}\t{s['evidence'].replace(chr(9), ' ')}\n")
        print(f"\nwrote {len(rows)} suggestion(s) to {a.sssom}", file=sys.stderr)


if __name__ == "__main__":
    main()
