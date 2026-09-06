# Baseline Model Report — GraphTriage

_Generated: 2026-09-06T02:18:04.882583+00:00_

These are the baseline results that Day 5's Graph Neural Network model must be compared against. Per `docs/prd.md` Section 10 and `docs/phases.md` Phase 4, a paper without a documented baseline comparison is very hard to publish — this file is that documentation.

## 1. Root-Cause Classification Baseline
**Model:** TF-IDF + Logistic Regression (baseline)

- Train / Val / Test sizes: 837 / 179 / 184
- Validation Accuracy: **1.0** | Macro-F1: **1.0**
- Test Accuracy: **1.0** | Macro-F1: **1.0**

**Important caveat (must be stated in the paper's Limitations section):** This baseline reaches 100% accuracy because the synthetic dataset's ticket text is generated from category-specific templates with largely non-overlapping vocabulary (see `docs/memory.md` decision log, Sprint Day 4). This means root-cause classification accuracy is **not** a meaningful axis for comparing the GNN model against this baseline — there is no headroom left. The GNN's contribution should instead be demonstrated via the resolution-time regression task (Section 2 below) and the knowledge-graph explainability/similarity-retrieval capabilities, which this baseline has no equivalent for at all.

## 2. Resolution-Time Regression Baseline
**Model:** Category-average baseline (resolution time)

- Train / Val / Test sizes: 837 / 179 / 184
- Validation MAE — category-average: **1.2h** | global-average: 3.024h
- Test MAE — category-average: **1.25h** | global-average: 2.897h

**This is the primary number Day 5's GNN regression head needs to beat.** Unlike classification, resolution times carry continuous random noise per ticket even within a category (see `generate.py`), so this baseline has genuine, non-zero error and real headroom for improvement.

### Per-Category Average Resolution Time (from Train Split)
| Category | Avg Resolution Time (h) |
|---|---|
| authentication-failure | 2.547 |
| cache-invalidation-bug | 3.625 |
| config-error | 2.137 |
| connection-pool-exhaustion | 5.465 |
| data-corruption | 8.593 |
| deadlock | 7.09 |
| disk-space-exhaustion | 1.844 |
| memory-leak | 16.46 |
| null-pointer-exception | 3.882 |
| race-condition | 6.892 |
| rate-limit-exceeded | 1.561 |
| third-party-api-failure | 4.704 |
| timeout | 4.01 |

## 3. What Day 5 Needs to Report

For a credible comparison in the paper/thesis, the Day 5 GNN evaluation should report, side-by-side with the numbers above:
- Root-cause prediction accuracy/F1 (expected to also be very high, given the dataset caveat above — report it, but do not lean on it as the novelty claim)
- Resolution-time MAE on the same test split (**this is the headline comparison number**)
- Qualitative examples of graph-based explanations that the baseline models have no equivalent of at all

