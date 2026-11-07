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
| Both found by this method only | 2 | 1 | 2 |
| Both found by this method only | 5 | 8 | 38 |
| Both found by this method only | 10 | 4 | 44 |
| Sign test p, two-sided, on the pairs above | 2 | | 1 |
| Sign test p, two-sided, on the pairs above | 5 | | 9.2e-06 |
| Sign test p, two-sided, on the pairs above | 10 | | 1.5e-09 |

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
| Both found by this method only | 2 | 1 | 2 |
| Both found by this method only | 5 | 7 | 37 |
| Both found by this method only | 10 | 4 | 44 |
| Sign test p, two-sided, on the pairs above | 2 | | 1 |
| Sign test p, two-sided, on the pairs above | 5 | | 5.3e-06 |
| Sign test p, two-sided, on the pairs above | 10 | | 1.5e-09 |

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
| Both found by this method only | 2 | 0 | 0 |
| Both found by this method only | 5 | 1 | 1 |
| Both found by this method only | 10 | 0 | 0 |
| Sign test p, two-sided, on the pairs above | 2 | | 1 |
| Sign test p, two-sided, on the pairs above | 5 | | 1 |
| Sign test p, two-sided, on the pairs above | 10 | | 1 |

## Tune questions (used to pick the graph settings)

### All (100 questions)

| Metric | k | Vector | Graph | Walk |
|---|---|---|---|---|
| Both gold passages in top k | 2 | 54/100 | 55/100 | 50/100 |
| Both gold passages in top k | 5 | 74/100 | 82/100 | 83/100 |
| Both gold passages in top k | 10 | 82/100 | 91/100 | 91/100 |
| Gold passages found (recall) | 2 | 76.0% | 77.0% | 73.5% |
| Gold passages found (recall) | 5 | 87.0% | 91.0% | 91.5% |
| Gold passages found (recall) | 10 | 91.0% | 95.5% | 95.5% |
| Answer text in top k | 2 | 69/94 | 71/94 | 70/94 |
| Answer text in top k | 5 | 78/94 | 84/94 | 85/94 |
| Answer text in top k | 10 | 82/94 | 88/94 | 89/94 |
| Both found by this method only | 2 | 0 | 1 | |
| Both found by this method only | 5 | 2 | 10 | |
| Both found by this method only | 10 | 0 | 9 | |
| Sign test p, two-sided, on the pairs above | 2 | | 1 | |
| Sign test p, two-sided, on the pairs above | 5 | | 0.039 | |
| Sign test p, two-sided, on the pairs above | 10 | | 0.0039 | |

Walk is the graph walk alone, without fusing it with the vector ranking.

## Rerun cost

| Step | Seconds |
|---|---|
| Embed passages and questions | 518.0 |
| Build entity graph | 1.0 |
| Vector search, all questions | 0.4 |
| Graph retrieval, all questions | 2.0 |
| Total | 521.4 |

API tokens: 0. Money: US$0. Everything runs on this machine.
