# Graph retrieval vs vector search, on held-out multi-hop questions

I built a GraphRAG system for a client. It turns documents from many knowledge bases into one knowledge graph and answers questions from it. That work is private, so this repo is a small public twin you can rerun: the same idea on open data, scored against plain vector search, with the cost of a rerun.

The question it answers: when the answer needs two documents, and the question names only the first one, does walking an entity graph find the second document more often than vector search does?

## Results (held-out, 400 questions)

| Both gold passages retrieved | Vector search | Graph retrieval |
|---|---|---|
| In top 2 | 191/400 | 192/400 |
| In top 5 | 292/400 | 322/400 |
| In top 10 | 331/400 | 371/400 |

- At top 5, the graph found both passages on 38 questions where vector search did not, and lost 8. At top 10 it was 44 to 4. An exact sign test on those pairs gives p < 0.0001 for both.
- At top 2 there is no difference (2 to 1).
- The gain in finding both passages is all on bridge questions, where the second passage is only reachable through the first. On comparison questions, which name both entities, the two methods are identical (87/88 at top 5).
- The answer string appears in the top 5 passages for 316/369 questions with the graph and 301/369 with vector search. Yes/no answers are left out of that count.

Example from the held-out run: "What citizen was the author of Bimbos of the Death Sun?" Vector search finds the novel's page but not the author's. The novel's page mentions Sharyn McCrumb, so the graph walk reaches her page, which holds the answer.

Full tables, including recall and the tune split: [runs/results.md](runs/results.md). Every question with both top-10 lists: [runs/test.jsonl](runs/test.jsonl).

## Rerun cost

US$0. No API keys, no tokens. Everything runs on a laptop.

The last full run took 465 seconds on an Apple M3 with 16 GB of RAM, shared with other heavy jobs at the time. Embedding the 4,965 passages and 500 questions took 460 seconds. Building the graph took under 1 second, and retrieving for all 500 questions took 4 seconds. The first run also downloads a 63 MB embedding model.

```sh
uv sync
uv run python test_eval.py               # quick check on a tiny made-up corpus
uv run python eval.py | tee runs/results.md
```

## What is compared

- **Data.** 500 questions sampled from the [HotpotQA](https://hotpotqa.github.io/) dev set (distractor setting). Each question needs two Wikipedia paragraphs. All their paragraphs, gold and distractor, are pooled into one corpus of 4,965 passages, and every question searches the whole pool. 100 questions are for tuning and 400 are held out. `prepare_data.py` rebuilds `data/` from the pinned source file.
- **Vector search.** `BAAI/bge-small-en-v1.5` embeddings through fastembed, ranked by cosine similarity.
- **Graph retrieval.** Each passage is about one entity, named by its title. A passage also mentions every other known entity whose name appears in its text. That gives a graph of 5,844 entities and 11,748 relations. For a question, I seed a personalized PageRank with the entities named in the question and the top 3 vector hits, and walk the graph. Then I fuse the walk's ranking with the vector ranking (reciprocal rank fusion).
- **Scoring.** The main score is whether both gold passages are in the top k. I also report recall and whether the reference answer string appears in the retrieved text.

I picked the graph settings (3 vector seeds, damping 0.3, fusion) on the 100 tune questions only, before I ran the held-out set. On the tune split, the walk without fusion did slightly better at top 5 (84 against 82) but worse at top 2 (50 against 55), so I kept fusion.

My first held-out run had a bug: passages the walk never reached could fill the end of its ranking in alphabetical order. I fixed it, added a check for it to `test_eval.py`, and reran everything. The fix changed the held-out results only at top 10, where both passages were found for 371 questions instead of 370.

## Limits

- This scores retrieval, not generated answers. Scoring answers with RAGAS or an LLM judge needs a paid model, and I kept the rerun free. The retrieved passages and reference answers are in `runs/` for anyone who wants to add that step.
- The entities are Wikipedia article titles, matched as exact strings. My client system used a language model to extract entities and typed relations, which finds more kinds of relations than string matching does but costs money per document.
- HotpotQA was built by following Wikipedia links, so a graph of title mentions suits it well. Documents with fewer clean entity names would give a smaller gain.

## Data license

The files in `data/` and `runs/` contain text from HotpotQA (Yang et al., 2018), which comes from Wikipedia and is licensed [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/).
