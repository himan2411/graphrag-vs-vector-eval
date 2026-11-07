"""Checks for the graph and the scoring on a tiny made-up corpus. Run: uv run python test_eval.py"""

from eval import Graph, entity_names, find_entities, score

corpus = [
    {
        "title": "Big Stone Gap (film)",
        "text": "Big Stone Gap is a film directed by Adriana Trigiani.",
    },
    {"title": "Pompano Beach, Florida", "text": "Pompano Beach is a city in Florida."},
    {
        "title": "Adriana Trigiani",
        "text": "Adriana Trigiani is a writer based in Greenwich Village.",
    },
]

assert entity_names("Big Stone Gap (film)") == {
    ("big", "stone", "gap", "film"),
    ("big", "stone", "gap"),
}
assert ("pompano", "beach") in entity_names("Pompano Beach, Florida")
assert find_entities("Who directed Big Stone Gap?", {("big", "stone", "gap")}) == {
    ("big", "stone", "gap")
}

g = Graph(corpus)
assert (0, "mentions", ("adriana", "trigiani")) in g.relations
assert (2, "about", ("adriana", "trigiani")) in g.relations

# Vector search only found the film page. The walk should reach the director's page
# through the film page's mention of her. The unrelated page is never reached, so it
# must not be returned at all.
q = "The director of Big Stone Gap is based in what New York neighborhood?"
top = g.retrieve(q, [("Big Stone Gap (film)", 0.9)], k=3)
assert top == ["Big Stone Gap (film)", "Adriana Trigiani"], top

# No entity in the question and no positive vector score: fall back to vector order.
assert g.retrieve("nothing here", [("Pompano Beach, Florida", -0.1)], k=1) == [
    "Pompano Beach, Florida"
]

texts = {p["title"]: p["text"] for p in corpus}
s = score(
    {
        "supporting_titles": ["Big Stone Gap (film)", "Adriana Trigiani"],
        "answer": "Greenwich Village",
    },
    top,
    texts,
)
assert s["both@2"] and s["recall@2"] == 1.0 and s["answer@2"]
s = score(
    {"supporting_titles": ["Adriana Trigiani"], "answer": "yes"},
    ["Pompano Beach, Florida"],
    texts,
)
assert not s["both@2"] and "answer@2" not in s

print("ok")
