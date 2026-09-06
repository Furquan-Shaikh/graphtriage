# GNN vs. Baseline — Final Comparison Report — GraphTriage

_Generated: 2026-09-06T07:16:43.288758+00:00_

## 1. Summary Table
| Metric | Baseline | GraphSAGE GNN | Delta |
|---|---|---|---|
| Root-cause Accuracy | 1.0 | 1.0 | +0.0000 |
| Root-cause Macro-F1 | 1.0 | 1.0 | +0.0000 |
| Resolution-Time MAE (hours) | 1.25 | 1.2984 | +0.0484 (+3.9%) |

## 2. Root-Cause Classification — Discussion
Both the baseline and the GNN reach 100% accuracy on this task. As documented in `docs/memory.md` (Sprint Day 4 decision log), this is a property of the synthetic dataset: `generate.py` uses category-specific templates with largely non-overlapping vocabulary, making categories trivially separable by keyword presence alone. **This metric should not be used as evidence of the GNN's value** — it is reported for completeness, but the classification task has no accuracy headroom left for either model to demonstrate improvement over the other.

## 3. Resolution-Time Regression — Discussion
The GNN model did **not** beat the category-average baseline on this run (MAE 1.2984h vs. baseline 1.25h). As documented in `docs/memory.md` (Sprint Day 5 decision log), this is an explainable and honest property of the synthetic dataset: `generate.py` samples resolution time independently and uniformly *per category*, with no dependency on ticket text content beyond category membership. Under this data-generating process, the category-average is close to the Bayes-optimal predictor for MAE, leaving little signal for any model — including a GNN — to exploit further.

**This is a legitimate finding to report, not a failure to hide.** It should be discussed openly in the thesis/paper's Limitations or Discussion section, alongside a note that real-world ticket data (where resolution time plausibly correlates with textual details, reporter, time-of-day, etc.) would likely give the graph/text-based model more genuine signal to learn from than this synthetic dataset does.

## 4. Where GraphTriage's Value Actually Shows Up

Given the two findings above, the strongest parts of the GraphTriage contribution to lead with in the paper are **not** the raw accuracy/MAE numbers, but:
- The **knowledge-graph-based similar-ticket retrieval** (Day 3) — no baseline model in this comparison has an equivalent capability at all.
- The **explainability layer** (to be built in a later phase) — showing *why* a prediction was made, which neither the TF-IDF classifier nor the naive resolution-time average can provide.
- The **real, working system integration** (Spring Boot + Neo4j + FastAPI, Days 1, 3, 7-8) — most academic baselines are evaluated offline in a notebook, not wired into a live, queryable service.


## 5. Honest Limitations Section (Draft Text)

> This work uses a synthetically generated ticket dataset (see Section 9 of the project requirements) due to the unavailability of a sufficiently large real-world labeled dataset. Two consequences of this choice were observed and are reported transparently: (1) root-cause classification reaches 100% accuracy for both baseline and proposed models, due to the template-based text generation producing category-distinctive vocabulary; and (2) the resolution-time regression baseline is close to optimal under the dataset's independent per-category noise model, limiting the observable improvement from the proposed graph-based approach. Future work should validate these findings against real-world ticketing data, where both textual ambiguity and cross-feature dependencies are expected to be higher, likely widening the gap between baseline and graph-based approaches.

