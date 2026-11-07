"""Build data/corpus.jsonl and data/questions.jsonl from the HotpotQA dev set.

Download the source file first (27 MB, pinned revision):
  curl -L -o validation.parquet https://huggingface.co/datasets/hotpotqa/hotpot_qa/resolve/1908d6afbbead072334abe2965f91bd2709910ab/distractor/validation-00000-of-00001.parquet
Then: uv run python prepare_data.py validation.parquet
"""

import json
import random
import sys
from pathlib import Path

import pyarrow.parquet as pq

N_QUESTIONS = 500
N_TUNE = 100  # the rest is held out and only scored once
SEED = 7


def main(parquet_path):
    rows = pq.read_table(parquet_path).to_pylist()
    rows = random.Random(SEED).sample(rows, N_QUESTIONS)

    corpus = {}
    questions = []
    for i, r in enumerate(rows):
        for title, sents in zip(r["context"]["title"], r["context"]["sentences"]):
            corpus.setdefault(title, "".join(sents).strip())
        questions.append(
            {
                "id": r["id"],
                "split": "tune" if i < N_TUNE else "test",
                "type": r["type"],
                "question": r["question"],
                "answer": r["answer"],
                "supporting_titles": sorted(set(r["supporting_facts"]["title"])),
            }
        )

    out = Path(__file__).parent / "data"
    out.mkdir(exist_ok=True)
    with open(out / "corpus.jsonl", "w") as f:
        for title, text in sorted(corpus.items()):
            f.write(
                json.dumps({"title": title, "text": text}, ensure_ascii=False) + "\n"
            )
    with open(out / "questions.jsonl", "w") as f:
        f.writelines(json.dumps(q, ensure_ascii=False) + "\n" for q in questions)
    print(f"{len(questions)} questions, {len(corpus)} passages")


if __name__ == "__main__":
    main(sys.argv[1])
