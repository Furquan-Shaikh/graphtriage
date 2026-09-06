# Project Memory — GraphTriage

**Related Documents:** prd.md, architecture.md, rules.md, phases.md, design.md

This is the **living memory** of the project — a running log of decisions, status, and open questions. Update this file whenever a meaningful decision is made, a design deviates from the original plan, or a phase completes. If an AI coding assistant is used across multiple sessions, this file should be given to it first, so it always has full context of where the project currently stands.

---

## 1. Purpose

- Preserve context across a multi-month project so nothing has to be "re-explained from scratch" later.
- Record *why* decisions were made, not just *what* was decided — this is invaluable both for defending choices to the mentor and for writing the methodology/discussion sections of the paper.
- Track current status at a glance.

---

## 2. Project Snapshot

| Field | Value |
|---|---|
| Project Name | GraphTriage |
| Domain | AIOps / Software Engineering + AI |
| Core Idea | Knowledge-graph based explainable ticket triage and root-cause linking |
| Current Phase | Phase 7 — Backend Integration (see `phases.md`) — Phase 0-6 / Sprint Days 1-6 complete |
| Target Outcome | Working prototype + thesis + paper submission to a Scopus/SCI-indexed venue |
| Plagiarism Target | Below 30% on final report |

*(Update the "Current Phase" row as the project progresses.)*

---

## 3. Key Decisions Log (Architecture Decision Record style)

Use this format for every significant decision:

```
### Decision: <short title>
Date: <date>
Context: <what problem/question prompted this decision>
Decision: <what was decided>
Rationale: <why this option was chosen over alternatives>
Alternatives Considered: <other options and why they were rejected>
```

**Example (already made in the planning stage):**

```
### Decision: Chose GraphTriage over other candidate project ideas
Date: Project kickoff
Context: Five candidate AIOps project ideas were evaluated (GraphTriage, SecuGuard,
SelfHeal-RL, ContractGuard, SmartTest) for feasibility and publishability.
Decision: Proceed with GraphTriage.
Rationale: Best balance of novelty (knowledge-graph + explainability + real-system
integration is under-explored), buildability (leverages existing backend ticketing
system knowledge), and publishability (clear baseline-comparison story).
Alternatives Considered: SecuGuard (strong niche but narrower scope), SelfHeal-RL
(higher infra complexity), ContractGuard (harder dataset acquisition), SmartTest
(more saturated literature, harder to stand out).
```

*(Add new decision entries below this line as the project proceeds — e.g., dataset choice, GNN architecture choice, any scope change.)*

```
### Observation: TF-IDF + Logistic Regression baseline achieves 100% accuracy
on root-cause classification
Date: Sprint Day 4
Context: While training the required baseline classifier (docs/phases.md
Phase 4), the TF-IDF + Logistic Regression model scored 100% accuracy and
100% macro-F1 on both the validation and test splits for root-cause category
prediction.
Root Cause: generate.py (Day 2) uses category-specific text templates with
largely non-overlapping vocabulary (e.g. only "deadlock" tickets mention
"circular wait"/"thread deadlock"; only "null-pointer-exception" tickets
mention "NullPointerException"). This makes the categories trivially
separable by keyword presence alone.
Implication: The root-cause classification task cannot meaningfully
demonstrate the GNN model's (Day 5) value over the baseline on this dataset,
since there is no accuracy headroom left. This is a genuine limitation of
the synthetic dataset and must be disclosed plainly in the thesis/paper
(Limitations section), not hidden.
Mitigation / Path Forward: The resolution-time regression baseline (Step 4,
same day) is NOT affected by this issue, since resolution_time_hours is
sampled with continuous random noise per ticket even within a category
(see generate.py). The primary "baseline vs. GNN" comparison story for the
paper will center on resolution-time prediction (MAE) and on the
graph-based explainability/similarity-retrieval contributions, rather than
on root-cause classification accuracy.
Alternatives Considered: Regenerating the Day 2 dataset with noisier,
less template-distinctive text (e.g. shared vocabulary/paraphrased
templates across categories) — deferred rather than done immediately, to
avoid re-doing completed Day 2/3 work mid-sprint; worth revisiting if time
allows before the final evaluation phase (Phase 9).
```

```
### Observation: Resolution-time GNN may not beat the category-average baseline
Date: Sprint Day 5
Context: In an initial GNN training run, test MAE (1.2593h, on synthetic
test embeddings) came out slightly worse than the Day 4 category-average
baseline (1.25h) - a -0.7% "improvement".
Root Cause: generate.py (Day 2) samples resolution_time_hours independently
and uniformly per category (random.uniform(rlo, rhi)), with no dependency
on ticket text content beyond category. This makes the category-average a
near-Bayes-optimal predictor for MAE under this specific data-generating
process - there is little to no additional signal left for any model
(GNN included) to exploit.
Implication: If the real-embeddings GNN run (on the student's machine)
also fails to clearly beat the baseline MAE, this is an honest, explainable
property of the synthetic dataset design - not a bug - and should be
discussed plainly in the thesis/paper's Limitations/Discussion section,
alongside the Day 4 classification-saturation finding.
Mitigation / Path Forward: If a clearer "GNN beats baseline" story is
needed for publication strength, consider enriching generate.py (Day 2) so
resolution_time_hours also depends partly on some text-derivable signal
(e.g. severity keywords, detail magnitude) before Phase 9 (Evaluation) -
not required for the Day 1-10 build sprint itself.
```

```
### Decision: Explainability uses SHAP (on baseline model) + graph similarity,
not GAT attention weights
Date: Sprint Day 6
Context: docs/design.md Section 3.3 originally envisioned attention-weight-based
graph-path explanations, which requires a GAT (Graph Attention Network).
Day 5 used GraphSAGE (no built-in attention) for simplicity/speed in the
lightweight sprint.
Decision: Built explainability from two components instead: (1) SHAP applied
to the Day 4 baseline TF-IDF+LogisticRegression classifier, for word-level
contribution explanations; (2) a k-NN similarity-based explainer reusing the
Day 5 embedding space, for "similar past tickets" graph-style explanations.
Both are combined into one JSON-shaped output matching design.md's original
intent.
Rationale: SHAP does not apply cleanly to a GNN's message-passing node
features (they're entangled with neighbors' features), so using it on the
baseline's clean bag-of-words features gives a genuinely correct, not
approximated, word-level explanation. The similarity explainer covers the
structural/relational explanation GAT attention would have provided, and
additionally works for brand-new tickets (not just ones already in the
graph), which plain GAT attention would not support as directly.
Alternatives Considered: Switching the Day 5 model from GraphSAGE to GAT to
get native attention weights - deferred as unnecessary extra complexity for
the lightweight sprint, since the SHAP + similarity combination already
satisfies the "explain every prediction" requirement (prd.md FR-7) without
it.
```

```
### Decision: Changed MySQL host port from 3306 to 3307 in docker-compose.yml
Date: Sprint Day 1
Context: On first `docker compose up`, the MySQL container failed to start with a
port-bind error ("ports are not available: ... 0.0.0.0:3306"). This is a common
Windows issue where a locally installed MySQL service (or XAMPP/WAMP) already
occupies port 3306 on the host machine.
Decision: Changed the host-side port mapping for the mysql service to "3307:3306"
in docker-compose.yml, while keeping the container-internal port at 3306.
Rationale: The ticketing-service connects to MySQL internally via the Docker
network using the hostname "mysql" and port 3306 (see SPRING_DATASOURCE_URL in
docker-compose.yml), so this change has zero effect on inter-service
communication — it only changes how the database is reached from the host
machine (e.g., via a local MySQL client/Workbench, now on port 3307).
Alternatives Considered: Manually stopping the conflicting local MySQL service
via Windows Services — rejected as the default fix since it requires admin
access and could affect other local projects that depend on that local MySQL
instance.
```

```
### Decision: Added a `dataset_split` column to the `ticket` table
Date: Sprint Day 2
Context: The synthetic dataset (generate.py) is divided into train/val/test
(split_dataset.py, stratified by root-cause category), but the original
design.md schema had no way to record which split a loaded ticket belongs to.
Decision: Added `dataset_split VARCHAR(10) DEFAULT NULL` to the `ticket` table
(see data/generator/schema.sql), storing 'train' / 'val' / 'test'.
Rationale: Model training (Day 5) and final evaluation (Day 9) both need to
reliably pull the correct subset of tickets from MySQL/the knowledge graph.
Storing the split as a column is simpler and less error-prone than
re-deriving it later from separate CSV files once everything lives in MySQL.
design.md Section 1 has been updated to match this schema.
Alternatives Considered: Keeping split membership only in the CSV files —
rejected because once data is loaded into MySQL and later synced into Neo4j
(Day 3), there would be no reliable way to look up which split a given
ticket ID belongs to.
```


---

## 4. Changelog

| Date | Change |
|---|---|
| Project kickoff | PRD, architecture, rules, phases, and design documents created and approved as the project foundation |
| Sprint Day 1 | Repo scaffolded and pushed to GitHub; Docker Compose stack (MySQL, Neo4j, ticketing-service, inference-service) verified healthy end-to-end after fixing a MySQL host-port conflict (see Section 3) |
| Sprint Day 2 | Synthetic dataset generated (1200 tickets, 5 services, 13 root-cause categories), stratified 70/15/15 train/val/test split, loaded into MySQL (with new `dataset_split` column, see Section 3), and documented via `data/generated/dataset_report.md` |
| Sprint Day 3 | Knowledge graph built in Neo4j: constraints/indexes applied, Service/Ticket/Bug/Fix nodes synced from MySQL via `graph-etl/sync_to_graph.py`, validated (all MySQL-vs-Neo4j counts matched: 5 services, 1200 tickets/bugs/fixes, 1200 of each relationship type), and visually confirmed in Neo4j Browser |
| Sprint Day 4 | Sentence-BERT embeddings generated for all 1200 tickets (384-dim, confirmed meaningful via within/across-category similarity gap of +0.33 on real data); baseline classifier (TF-IDF + LogReg) trained — 100% accuracy (dataset-limitation caveat logged in Section 3); baseline resolution-time estimator (category-average) trained — test MAE 1.25h, the number Day 5's GNN must beat; both consolidated into `data/generated/baseline_report.md` |
| Sprint Day 5 | GraphSAGE GNN built (k-NN similarity graph from embeddings + multi-task classification/regression heads), trained with early stopping; test results: 100% accuracy (same dataset-ceiling caveat as baseline), resolution-time MAE 1.2984h — did not beat the 1.25h baseline (explainable dataset-noise-model finding, logged in Section 3); full comparison + honest discussion consolidated into `data/generated/gnn_vs_baseline_report.md` |
| Sprint Day 6 | Explainability layer built: SHAP-based `FeatureExplainer` (keyword contributions, using the baseline classifier since SHAP doesn't apply directly to the GNN's message-passing features) + `SimilarityExplainer` (k-NN graph-based similar-ticket retrieval, works for both existing and brand-new tickets) + `CombinedExplainer` merging both into the design.md-specified output shape. Qualitative review on 15 test tickets: 15/15 correct predictions, 100% neighbor-category agreement. Samples documented in `data/generated/explainability_samples.md` |

*(Append one line per significant milestone — e.g., "Phase 2 complete: knowledge graph populated with 1,200 tickets.")*

---

## 5. Open Questions / TODO

- [ ] Confirm dataset source: internal/real ticketing data (Option A) vs. public/synthetic (Option B) — see `prd.md` Section 9.
- [ ] Confirm target journal/conference shortlist for final submission (to align formatting/length requirements early).
- [ ] Confirm GPU/compute availability for GNN training (affects Phase 5 timeline in `phases.md`).
- [ ] Decide whether GAT (attention-based, better explainability) or GraphSAGE (simpler, faster) is the final model — start with GraphSAGE per `design.md`, revisit after Phase 4 baselines.

*(Keep this list current — remove items once resolved, and log the resolution in Section 3 if it was a meaningful decision.)*

---

## 6. Glossary (shared with prd.md, kept here for quick reference during development)

| Term | Meaning |
|---|---|
| AIOps | Artificial Intelligence for IT Operations |
| GNN | Graph Neural Network |
| GraphSAGE | A GNN architecture that generates node embeddings by sampling and aggregating neighbor features |
| GAT | Graph Attention Network — a GNN variant that learns attention weights over neighbors |
| SHAP | SHapley Additive exPlanations — a model explainability technique |
| Root Cause | The underlying reason a ticket/incident occurred |

---

## 7. Ownership & Contact

| Role | Name |
|---|---|
| Student / Developer | (Friend's name) |
| Mentor / Guide | (To be filled in) |
| Supporting Advisor (idea generation & planning) | Furquan |

---

## 8. How to Use This File Going Forward

1. At the start of every work session, skim Sections 2, 3 (latest entries), and 5 to re-orient.
2. At the end of every work session (or at least every phase, per `phases.md`), update Section 2 (status), add to Section 4 (changelog), and log any real decision in Section 3.
3. Never let this file go stale for more than one phase — it is the single source of truth for "what happened and why" across the whole project lifecycle, and will directly make writing the thesis's methodology and discussion chapters much faster.
