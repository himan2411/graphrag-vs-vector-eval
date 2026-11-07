"""Compare plain vector search with graph retrieval on HotpotQA multi-hop questions.

uv run python eval.py
"""

import json
import re
import string
import time
from collections import defaultdict
from pathlib import Path

import numpy as np
from fastembed import TextEmbedding
from scipy import sparse
from scipy.stats import binomtest

MODEL = "BAAI/bge-small-en-v1.5"
KS = (2, 5, 10)
# Graph settings, picked on the tune split only.
VECTOR_SEEDS = 3
DAMPING = 0.3
RRF_C = 60  # the usual reciprocal rank fusion constant, not tuned
MAX_NAME_TOKENS = 10

HERE = Path(__file__).parent


def tokens(text):
    return re.findall(r"\w+", text.lower())


def entity_names(title):
    """Names an article's subject goes by: 'Pompano Beach, Florida' -> also 'Pompano Beach'."""
    base = re.sub(r"\s*\(.*?\)\s*", " ", title).strip()
    names = {title, base, base.split(",")[0]}
    return {tuple(tokens(n)) for n in names if len(n) >= 4 and tokens(n)}


def find_entities(text, known):
    """Every known entity name that appears in text, matched on whole words."""
    toks = tokens(text)
    found = set()
    for i in range(len(toks)):
        for j in range(i + 1, min(i + MAX_NAME_TOKENS, len(toks)) + 1):
            if tuple(toks[i:j]) in known:
                found.add(tuple(toks[i:j]))
    return found


class Graph:
    """Bipartite graph of passages and entities.

    A passage is ABOUT the entity its title names, and MENTIONS every other
    known entity that appears in its text. Nodes 0..P-1 are passages, the
    rest are entities.
    """

    def __init__(self, corpus):
        self.titles = [p["title"] for p in corpus]
        self.title_id = {t: i for i, t in enumerate(self.titles)}
        about = [entity_names(t) for t in self.titles]
        self.entity_id = {
            e: len(corpus) + i for i, e in enumerate(sorted(set().union(*about)))
        }
        self.relations = []  # (passage, relation, entity), kept for inspection and tests
        for pi, p in enumerate(corpus):
            for e in about[pi]:
                self.relations.append((pi, "about", e))
            for e in find_entities(p["text"], self.entity_id) - about[pi]:
                self.relations.append((pi, "mentions", e))
        n = len(corpus) + len(self.entity_id)
        rows = [pi for pi, _, _ in self.relations]
        cols = [self.entity_id[e] for _, _, e in self.relations]
        adj = sparse.coo_matrix(
            (np.ones(len(rows)), (rows, cols)), shape=(n, n)
        ).tocsr()
        adj = ((adj + adj.T) > 0).astype(float)
        deg = np.asarray(adj.sum(axis=0)).ravel()
        # Column-stochastic transition matrix for a random walk.
        self.transition = adj @ sparse.diags(1.0 / np.maximum(deg, 1))

    def pagerank(self, seeds, iters=50):
        """Personalized PageRank: walk the graph, restart at the seed nodes."""
        restart = np.zeros(self.transition.shape[0])
        for node, w in seeds.items():
            restart[node] += w
        restart /= restart.sum()
        r = restart.copy()
        for _ in range(iters):
            r = DAMPING * (self.transition @ r) + (1 - DAMPING) * restart
        return r

    def walk(self, question, vector_hits, k):
        """Seed the walk with the question's entities and the top vector hits.
        Returns up to k passages the walk reached, best first."""
        seeds = defaultdict(float)
        for e in find_entities(question, self.entity_id):
            seeds[self.entity_id[e]] += 1.0
        for title, score in vector_hits[:VECTOR_SEEDS]:
            seeds[self.title_id[title]] += max(score, 0.0)
        if not sum(seeds.values()):
            return [t for t, _ in vector_hits[:k]]
        r = self.pagerank(seeds)[: len(self.titles)]
        reached = [i for i in np.argsort(-r, kind="stable")[:k] if r[i] > 0]
        return [self.titles[i] for i in reached]

    def retrieve(self, question, vector_hits, k):
        """The walk's ranking fused with the vector ranking."""
        walk_top = self.walk(question, vector_hits, k)
        return fuse([t for t, _ in vector_hits], walk_top)[:k]


def fuse(*rankings):
    """Reciprocal rank fusion: a passage near the top of either list ranks high."""
    scores = defaultdict(float)
    for ranking in rankings:
        for rank, title in enumerate(ranking):
            scores[title] += 1 / (RRF_C + rank + 1)
    return sorted(scores, key=lambda t: -scores[t])


def normalize(s):
    s = "".join(c for c in s.lower() if c not in string.punctuation)
    return " ".join(w for w in s.split() if w not in {"a", "an", "the"})


def score(q, retrieved, texts):
    """Per-k: how many gold passages were found, and whether the answer text is in them."""
    gold = set(q["supporting_titles"])
    out = {}
    for k in KS:
        top = retrieved[:k]
        out[f"both@{k}"] = gold <= set(top)
        out[f"recall@{k}"] = len(gold & set(top)) / len(gold)
        if q["answer"].lower() not in {"yes", "no"}:
            out[f"answer@{k}"] = normalize(q["answer"]) in normalize(
                " ".join(texts[t] for t in top)
            )
    return out


def summarize(rows, method):
    lines = []
    for metric, label in (
        ("both", "Both gold passages in top k"),
        ("recall", "Gold passages found (recall)"),
        ("answer", "Answer text in top k"),
    ):
        cells = []
        for k in KS:
            vals = [
                r[method][f"{metric}@{k}"] for r in rows if f"{metric}@{k}" in r[method]
            ]
            if metric == "recall":
                cells.append(f"{sum(vals) / len(vals):.1%}")
            else:
                cells.append(f"{sum(vals)}/{len(vals)}")
        lines.append((label, cells))
    return lines


def embed_passages(model, corpus):
    """Embed in length order so each batch pads to similar lengths; that is much faster on CPU."""
    docs = [f"{p['title']}. {p['text']}" for p in corpus]
    order = sorted(range(len(docs)), key=lambda i: len(docs[i]))
    vecs = np.zeros((len(docs), model.embedding_size), dtype=np.float32)
    vecs[order] = np.array(list(model.embed([docs[i] for i in order], batch_size=32)))
    return vecs


def paired(rows, k):
    """Questions where only one method found both gold passages, and an exact
    two-sided sign test on those pairs."""
    vec = sum(r["vector"][f"both@{k}"] and not r["graph"][f"both@{k}"] for r in rows)
    gra = sum(r["graph"][f"both@{k}"] and not r["vector"][f"both@{k}"] for r in rows)
    p = binomtest(gra, vec + gra).pvalue if vec + gra else 1.0
    return vec, gra, p


def print_tables(rows, groups, methods=("vector", "graph")):
    for label, keep in groups:
        subset = [r for r in rows if keep(r)]
        print(f"### {label} ({len(subset)} questions)\n")
        print("| Metric | k | " + " | ".join(m.capitalize() for m in methods) + " |")
        print("|---|---|" + "---|" * len(methods))
        stats = [summarize(subset, m) for m in methods]
        for i, (name, _) in enumerate(stats[0]):
            for j, k in enumerate(KS):
                cells = " | ".join(st[i][1][j] for st in stats)
                print(f"| {name} | {k} | {cells} |")
        pairs = [paired(subset, k) for k in KS]
        for k, (vec, gra, _) in zip(KS, pairs):
            pad = " |" * (len(methods) - 2)
            print(f"| Both found by this method only | {k} | {vec} | {gra} |{pad}")
        for k, (_, _, p) in zip(KS, pairs):
            pad = " |" * (len(methods) - 2)
            print(
                f"| Sign test p, two-sided, on the pairs above | {k} | | {p:.2g} |{pad}"
            )
        print()


def main():
    corpus = [
        json.loads(line)
        for line in (HERE / "data/corpus.jsonl").read_text().splitlines()
    ]
    questions = [
        json.loads(line)
        for line in (HERE / "data/questions.jsonl").read_text().splitlines()
    ]
    titles = [p["title"] for p in corpus]
    texts = {p["title"]: p["text"] for p in corpus}
    timings = {}

    t = time.perf_counter()
    model = TextEmbedding(MODEL)
    doc_vecs = embed_passages(model, corpus)
    q_vecs = np.array(list(model.query_embed([q["question"] for q in questions])))
    timings["Embed passages and questions"] = time.perf_counter() - t

    t = time.perf_counter()
    graph = Graph(corpus)
    timings["Build entity graph"] = time.perf_counter() - t

    rows = []
    vec_time = graph_time = 0.0
    for q, qv in zip(questions, q_vecs):
        t = time.perf_counter()
        sims = doc_vecs @ qv
        order = np.argsort(-sims)[: max(KS)]
        vector_hits = [(titles[i], float(sims[i])) for i in order]
        vec_time += time.perf_counter() - t

        t = time.perf_counter()
        graph_top = graph.retrieve(q["question"], vector_hits, max(KS))
        graph_time += time.perf_counter() - t
        # The walk alone, without fusion: only to show why I kept fusion.
        walk_top = graph.walk(q["question"], vector_hits, max(KS))

        vector_top = [title for title, _ in vector_hits]
        rows.append(
            {
                "id": q["id"],
                "split": q["split"],
                "type": q["type"],
                "question": q["question"],
                "answer": q["answer"],
                "supporting_titles": q["supporting_titles"],
                "vector_top10": vector_top,
                "graph_top10": graph_top,
                "walk_top10": walk_top,
                "vector": score(q, vector_top, texts),
                "walk": score(q, walk_top, texts),
                "graph": score(q, graph_top, texts),
            }
        )
    timings["Vector search, all questions"] = vec_time
    timings["Graph retrieval, all questions"] = graph_time

    runs = HERE / "runs"
    runs.mkdir(exist_ok=True)
    for split in ("test", "tune"):
        lines = [
            json.dumps(r, ensure_ascii=False) + "\n"
            for r in rows
            if r["split"] == split
        ]
        (runs / f"{split}.jsonl").write_text("".join(lines))

    print(
        f"{len(corpus)} passages, {len(questions)} questions, "
        f"graph of {len(graph.entity_id)} entities and {len(graph.relations)} relations\n"
    )
    print("## Held-out questions\n")
    print_tables(
        [r for r in rows if r["split"] == "test"],
        (
            ("All", lambda r: True),
            (
                "Bridge: the answer is one hop from the entity named",
                lambda r: r["type"] == "bridge",
            ),
            ("Comparison: two named entities", lambda r: r["type"] == "comparison"),
        ),
    )
    print("## Tune questions (used to pick the graph settings)\n")
    print_tables(
        [r for r in rows if r["split"] == "tune"],
        (("All", lambda r: True),),
        methods=("vector", "graph", "walk"),
    )
    print("Walk is the graph walk alone, without fusing it with the vector ranking.\n")
    print("## Rerun cost\n")
    print("| Step | Seconds |")
    print("|---|---|")
    for step, secs in timings.items():
        print(f"| {step} | {secs:.1f} |")
    print(f"| Total | {sum(timings.values()):.1f} |")
    print("\nAPI tokens: 0. Money: US$0. Everything runs on this machine.")


if __name__ == "__main__":
    main()
