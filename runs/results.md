4965 passages, 500 questions, graph of 5844 entities and 11748 relations

## Held-out questions

### All (400 questions)

| Metric | k | Vector | Graph |
|---|---|---|---|
| Both gold passages in top k | 2 | 191/400 | 192/400 |
| Both gold passages in top k | 5 | 292/400 | 322/400 |
| Both gold passages in top k | 10 | 331/400 | 371/400 |
| Gold passages found (recall) | 2 | 71.8% | 71.9% |
| Gold passages found (recall) | 5 | 85.8% | 89.5% |
| Gold passages found (recall) | 10 | 91.1% | 96.1% |
| Answer text in top k | 2 | 244/369 | 245/369 |
| Answer text in top k | 5 | 301/369 | 316/369 |
| Answer text in top k | 10 | 330/369 | 349/369 |

### Bridge: the answer is one hop from the entity named (312 questions)

| Metric | k | Vector | Graph |
|---|---|---|---|
| Both gold passages in top k | 2 | 113/312 | 114/312 |
| Both gold passages in top k | 5 | 205/312 | 235/312 |
| Both gold passages in top k | 10 | 243/312 | 283/312 |
| Gold passages found (recall) | 2 | 65.4% | 65.5% |
| Gold passages found (recall) | 5 | 81.9% | 86.7% |
| Gold passages found (recall) | 10 | 88.6% | 95.0% |
| Answer text in top k | 2 | 189/312 | 189/312 |
| Answer text in top k | 5 | 244/312 | 259/312 |
| Answer text in top k | 10 | 273/312 | 292/312 |

### Comparison: two named entities (88 questions)

| Metric | k | Vector | Graph |
|---|---|---|---|
| Both gold passages in top k | 2 | 78/88 | 78/88 |
| Both gold passages in top k | 5 | 87/88 | 87/88 |
| Both gold passages in top k | 10 | 88/88 | 88/88 |
| Gold passages found (recall) | 2 | 94.3% | 94.3% |
| Gold passages found (recall) | 5 | 99.4% | 99.4% |
| Gold passages found (recall) | 10 | 100.0% | 100.0% |
| Answer text in top k | 2 | 55/57 | 56/57 |
| Answer text in top k | 5 | 57/57 | 57/57 |
| Answer text in top k | 10 | 57/57 | 57/57 |

## Tune questions (used to pick the graph settings)

### All (100 questions)

| Metric | k | Vector | Graph |
|---|---|---|---|
| Both gold passages in top k | 2 | 54/100 | 55/100 |
| Both gold passages in top k | 5 | 74/100 | 82/100 |
| Both gold passages in top k | 10 | 82/100 | 91/100 |
| Gold passages found (recall) | 2 | 76.0% | 77.0% |
| Gold passages found (recall) | 5 | 87.0% | 91.0% |
| Gold passages found (recall) | 10 | 91.0% | 95.5% |
| Answer text in top k | 2 | 69/94 | 71/94 |
| Answer text in top k | 5 | 78/94 | 84/94 |
| Answer text in top k | 10 | 82/94 | 88/94 |

## Rerun cost

| Step | Seconds |
|---|---|
| Embed passages and questions | 460.2 |
| Build entity graph | 0.7 |
| Vector search, all questions | 0.5 |
| Graph retrieval, all questions | 3.2 |
| Total | 464.6 |

API tokens: 0. Money: US$0. Everything runs on this machine.
