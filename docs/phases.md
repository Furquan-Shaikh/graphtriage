# Project Phases & Timeline — GraphTriage

**Related Documents:** prd.md, architecture.md, rules.md, design.md, memory.md

This document breaks the entire project — from scratch to final submission — into sequential phases. Assumed total duration: **~8 months**, typical for an M.Tech final year project (adjust week counts to your institution's actual calendar).

---

## Overview Table

| Phase | Name | Duration | Key Deliverable |
|---|---|---|---|
| 0 | Setup & Literature Review | Weeks 1–3 | Approved PRD, literature survey draft |
| 1 | Dataset Acquisition & Preparation | Weeks 4–6 | Cleaned, labeled dataset |
| 2 | Knowledge Graph Design & Construction | Weeks 7–9 | Working Neo4j graph with real/synthetic data |
| 3 | NLP Embedding Pipeline | Weeks 10–11 | Ticket embedding generation pipeline |
| 4 | Baseline Models | Weeks 12–13 | Baseline classifier + baseline resolution-time estimator |
| 5 | GNN Model Development | Weeks 14–18 | Trained GNN model outperforming baseline |
| 6 | Explainability Layer | Weeks 19–20 | SHAP/attention-based explanation module |
| 7 | Backend Integration (Spring Boot + Inference Service) | Weeks 21–24 | End-to-end working API |
| 8 | Dashboard & Demo | Weeks 25–26 | Working demo UI |
| 9 | Evaluation & Benchmarking | Weeks 27–28 | Final metrics report |
| 10 | Paper & Thesis Writing | Weeks 29–32 | Draft paper + thesis chapters |
| 11 | Review, Plagiarism Check & Final Submission | Weeks 33–34 | Final submitted paper + thesis + demo |

---

## 10-Day Rapid Build Sprint — Mapped to Phases

If the goal is to get a **working, hosted prototype ready for the mentor** quickly (rather than following the full 8-month academic calendar above), the same Phases 0–8 can be compressed into a 10-day sprint. Each sprint day below maps directly to one or more phases from the Overview Table, so the tasks, deliverables, and exit criteria for that day are the ones already defined under the corresponding Phase section further down — nothing new is invented here, it's the same work, compressed.

**Important scope note:** This sprint compresses the *build* phases only (Phase 0 through Phase 8). **Phase 9 (Evaluation & Benchmarking), Phase 10 (Paper & Thesis Writing), and Phase 11 (Final Submission)** are not part of this sprint — they happen after the prototype is live, and their duration depends on the journal's review process, not on build speed. Deep literature review (part of Phase 0) and full hyperparameter tuning (part of Phase 5) are also intentionally lightened during the sprint and should be revisited properly before Phase 10.

| Sprint Day | Sprint Focus | Corresponding Phase(s) | Deliverable | Status |
|---|---|---|---|---|
| Day 1 | Environment & repo setup | Phase 0 (setup part only; literature review deferred) | Repo live, containers running | ✅ Done |
| Day 2 | Dataset creation | Phase 1 | Labeled synthetic dataset in MySQL | ✅ Done |
| Day 3 | Knowledge graph construction | Phase 2 | Populated Neo4j graph | ✅ Done |
| Day 4 | Embeddings + baseline model | Phase 3 + Phase 4 | Embeddings ready, baseline metrics recorded | ✅ Done |
| Day 5 | GNN model | Phase 5 (lightweight version — no full hyperparameter search) | Trained GNN, compared to baseline | ✅ Done |
| Day 6 | Explainability | Phase 6 (simplified version) | Explanation module returning readable output | ✅ Done |
| Day 7 | Backend integration (API) | Phase 7 | End-to-end API working locally | |
| Day 8 | Dashboard | Phase 8 | Working local demo UI | |
| Day 9 | Dockerize + full local test | Phase 7 (hardening/testing tasks) | Fully working local system via Docker Compose | |
| Day 10 | Hosting + demo prep | Not a separate phase — deployment of Phase 7/8 output | Live hosted system, demo script ready | |

**After Day 10:** resume the full timeline at **Phase 9 (Evaluation & Benchmarking)** — the sprint gives you a working system, but the rigorous evaluation, full literature review, and paper/thesis writing (Phases 9–11) still need their own dedicated time before targeting a reputed journal.

---

## Phase 0 — Setup & Literature Review (Weeks 1–3) — *Sprint: Day 1* — ✅ Setup Complete

**Goals:** Establish project foundation and confirm novelty against existing literature.

**Tasks:**
- [ ] Finalize and get mentor sign-off on `prd.md`.
- [x] Set up Git repository with structure from `rules.md` Section 2.
- [x] Set up local dev environment (Java 17, Python 3.10+, Docker, Neo4j, MySQL).
- [ ] Conduct literature review: AIOps ticket triage, knowledge-graph applications in software engineering, GNNs for software systems.
- [ ] Identify 15–25 relevant papers; summarize each in your own words (avoid plagiarism from the start).

**Deliverables:** Approved PRD, initial literature review draft, working local dev environment.

**Exit Criteria:** Mentor approves scope; dev environment runs a "hello world" Spring Boot + Neo4j + Python FastAPI stack together via Docker Compose. — ✅ **Dev environment exit criteria met on Sprint Day 1** (repo on GitHub, all 4 containers healthy, both health endpoints returning UP). Literature review tasks remain open and should continue in parallel with the following sprint days, per `phases.md` original Phase 0 scope.

---

## Phase 1 — Dataset Acquisition & Preparation (Weeks 4–6) — *Sprint: Day 2* — ✅ Complete

**Goals:** Secure a usable, labeled dataset (Option A or B from `prd.md` Section 9).

**Tasks:**
- [x] Decide between internal/real dataset (Option A) vs. public/synthetic dataset (Option B). — Chose Option B (synthetic).
- [x] If Option B: source public issue-tracker data or build a synthetic ticket generator. — Built `data/generator/generate.py`.
- [x] Clean data: remove duplicates, handle missing fields, normalize text. — Not applicable in the same sense as real-world data since the generator produces well-formed records by construction; no cleaning step was needed.
- [x] Define train/validation/test splits. — Stratified 70/15/15 split via `data/generator/split_dataset.py`.

**Deliverables:** Cleaned dataset with documented schema and provenance. — ✅ `data/generated/dataset_report.md`.

**Exit Criteria:** Dataset loaded into MySQL; basic descriptive statistics (ticket counts, class balance, etc.) documented. — ✅ Met on Sprint Day 2 (1200 tickets loaded; see `data/generated/dataset_report.md`).

---

## Phase 2 — Knowledge Graph Design & Construction (Weeks 7–9) — *Sprint: Day 3* — ✅ Complete

**Goals:** Build the graph backbone of the system.

**Tasks:**
- [x] Implement graph schema from `design.md` in Neo4j. — `graph-etl/schema_constraints.cypher` + `setup_constraints.py`.
- [x] Write ETL scripts to populate the graph from MySQL data. — `graph-etl/sync_to_graph.py`.
- [x] Validate graph correctness (spot-check relationships via Cypher queries). — `graph-etl/validate_graph.py`, all counts matched.
- [x] Visualize a sample subgraph to confirm it makes structural sense. — Confirmed visually in Neo4j Browser (Ticket->Service, Ticket->Bug->Fix chains).

**Deliverables:** Populated Neo4j graph reflecting the full dataset. — ✅ 5 Service, 1200 Ticket, 1200 Bug, 1200 Fix nodes; 1200 each of RAISED_ON/CAUSED_BY/FIXED_BY relationships.

**Exit Criteria:** Graph queries return expected relationships (e.g., a ticket correctly links to its service and eventual fix). — ✅ Met on Sprint Day 3.

---

## Phase 3 — NLP Embedding Pipeline (Weeks 10–11) — *Sprint: Day 4* — ✅ Complete

**Goals:** Convert ticket text into usable vector representations.

**Tasks:**
- [x] Set up Sentence-Transformers embedding pipeline. — `inference-service/app/embeddings/embedder.py`.
- [x] Generate and store embeddings for all tickets. — `training/generate_embeddings.py` → `data/generated/embeddings.npz` (1200 × 384-dim).
- [x] Sanity-check embeddings (e.g., confirm semantically similar tickets have high cosine similarity). — `training/sanity_check_embeddings.py`, within/across-category gap = +0.33 on real embeddings.

**Deliverables:** Embedding generation module + stored embeddings for the dataset. — ✅ Done.

**Exit Criteria:** Nearest-neighbor search on embeddings returns intuitively similar tickets for a handful of manual spot checks. — ✅ Met (example: Ticket #40 → nearest neighbor Ticket #964, same category, similarity 0.9965).

---

## Phase 4 — Baseline Models (Weeks 12–13) — *Sprint: Day 4* — ✅ Complete

**Goals:** Establish baseline performance to compare the GNN against later (required for a credible evaluation section).

**Tasks:**
- [x] Train TF-IDF + Logistic Regression / Random Forest classifier for root-cause/service prediction. — `training/train_baseline_classifier.py`, 100% test accuracy (see caveat in `memory.md`).
- [x] Build a naive average-based (or simple regression) baseline for resolution-time estimation. — `training/train_baseline_resolution_time.py`, test MAE 1.25h.
- [x] Record baseline metrics per `prd.md` Section 10. — `training/build_baseline_report.py` → `data/generated/baseline_report.md`.

**Deliverables:** Documented baseline results. — ✅ `data/generated/baseline_report.md`.

**Exit Criteria:** Baseline metrics recorded and reproducible via a script. — ✅ Met on Sprint Day 4.

---

## Phase 5 — GNN Model Development (Weeks 14–18) — *Sprint: Day 5 (lightweight version)* — ✅ Complete

**Goals:** Build and train the core ML contribution of the project.

**Tasks:**
- [x] Implement graph data loader (PyTorch Geometric `Data`/`HeteroData` objects from the Neo4j graph). — `training/build_graph_dataset.py` (k-NN similarity edges from Day 4 embeddings, per docs/memory.md decision log).
- [x] Implement GNN architecture (GraphSAGE or GAT) per `design.md`. — `app/gnn_model/model.py`, 2-layer GraphSAGE with multi-task heads.
- [x] Train root-cause/service prediction head. — `training/train_gnn.py`.
- [x] Train resolution-time regression head. — same script, combined multi-task loss.
- [ ] Tune hyperparameters (learning rate, number of layers, embedding dimension). — Deliberately skipped for the lightweight sprint version (per `phases.md` sprint scope note); revisit before Phase 9 if time allows.
- [x] Compare against Phase 4 baselines. — `training/build_final_comparison_report.py` → `data/generated/gnn_vs_baseline_report.md`.

**Deliverables:** Trained GNN model with documented performance improvement over baseline. — ✅ Trained model saved (`gnn_model.pt`); performance is documented, though it does not show an improvement over baseline (see Exit Criteria).

**Exit Criteria:** GNN outperforms baseline on the target metrics (or, if not, a clearly documented and honestly discussed analysis of why — still valid for a thesis if the investigation is rigorous). — ✅ Met via the honest-analysis path: GNN matched baseline on classification (both saturated at 100%, a known dataset-template limitation) and did not beat baseline on resolution-time MAE (1.2984h vs. 1.25h), with a clear, documented explanation (near-Bayes-optimal category-average under the dataset's independent per-category noise model — see `docs/memory.md` Sprint Day 5 entry).

---

---

## Phase 6 — Explainability Layer (Weeks 19–20) — *Sprint: Day 6 (simplified version)* — ✅ Complete

**Goals:** Make predictions interpretable.

**Tasks:**
- [x] Integrate SHAP for feature-level explanations. — `app/explainability/feature_explainer.py`, applied to the baseline classifier (see `docs/memory.md` decision log for rationale).
- [x] Extract attention weights (if using GAT) for graph-path-level explanations. — Adapted: since Day 5 used GraphSAGE (no native attention), built `app/explainability/similarity_explainer.py` (k-NN graph similarity) instead — covers the same explanatory role.
- [x] Build a simple explanation formatting function (turns raw SHAP/attention output into a readable sentence + supporting graph path). — `app/explainability/combined_explainer.py`.
- [x] Do a small qualitative review: manually check 10–15 explanations for sensibility. — `training/review_explanations.py`, 15/15 correct predictions, 100% neighbor-category agreement.

**Deliverables:** Working explainability module integrated with the prediction pipeline. — ✅ `CombinedExplainer`, tested end-to-end against real data.

**Exit Criteria:** Every prediction can be paired with a human-readable explanation. — ✅ Met; samples documented in `data/generated/explainability_samples.md`.

---

## Phase 7 — Backend Integration (Weeks 21–24) — *Sprint: Days 7 & 9*

**Goals:** Turn the ML pipeline into a real, callable system — this is where prior Spring Boot/JWT experience is most directly leveraged.

**Tasks:**
- [ ] Build/extend the Spring Boot ticketing service with the endpoints defined in `design.md`.
- [ ] Build the Python FastAPI inference service wrapping the trained model + explainability module.
- [ ] Wire Spring Boot → Inference Service internal calls.
- [ ] Implement JWT authentication on the public API.
- [ ] Containerize all services via Docker Compose.
- [ ] Write integration tests covering the full ticket → prediction → explanation flow.

**Deliverables:** Fully working, containerized, end-to-end system.

**Exit Criteria:** A new ticket submitted via the API returns a prediction and explanation within the target latency (per `prd.md` NFRs).

---

## Phase 8 — Dashboard & Demo (Weeks 25–26) — *Sprint: Day 8*

**Goals:** Build a presentable interface for the mentor/evaluation panel.

**Tasks:**
- [ ] Build a simple dashboard showing: ticket list, prediction, similar tickets, and explanation panel.
- [ ] Prepare a scripted demo flow (a few representative tickets to showcase during evaluation).

**Deliverables:** Working demo dashboard.

**Exit Criteria:** A live demo can be run end-to-end without manual intervention.

---

## Phase 9 — Evaluation & Benchmarking (Weeks 27–28) — *Post-sprint: begins after Day 10*

**Goals:** Produce the final, defensible results for the paper/thesis.

**Tasks:**
- [ ] Run full evaluation on the held-out test set.
- [ ] Compute all metrics from `prd.md` Section 10.
- [ ] Conduct the small human evaluation of explanation usefulness.
- [ ] Create result tables/charts for the paper.

**Deliverables:** Final evaluation report with tables and charts.

**Exit Criteria:** Results are statistically sound and clearly presented.

---

## Phase 10 — Paper & Thesis Writing (Weeks 29–32) — *Post-sprint*

**Goals:** Produce the written academic output.

**Tasks:**
- [ ] Write methodology section (based directly on `architecture.md` and `design.md`).
- [ ] Write results/discussion section (based on Phase 9 output).
- [ ] Write related-work/literature-review section (carefully paraphrased, per `rules.md` Section 11).
- [ ] Assemble full thesis document per institution's format.
- [ ] Draft a condensed paper version for journal/conference submission.

**Deliverables:** Draft thesis + draft paper.

**Exit Criteria:** Mentor reviews and approves the draft.

---

## Phase 11 — Review, Plagiarism Check & Final Submission (Weeks 33–34) — *Post-sprint*

**Goals:** Finalize and submit.

**Tasks:**
- [ ] Run plagiarism check on the full thesis and paper (target: below 30%, per `prd.md`).
- [ ] Address any flagged sections by rewriting/paraphrasing further.
- [ ] Final proofreading pass.
- [ ] Submit thesis to college; submit paper to the chosen journal/conference.
- [ ] Prepare final viva/defense presentation.

**Deliverables:** Final submitted thesis, submitted paper, and defense presentation.

**Exit Criteria:** Submission complete; plagiarism score confirmed below target.

---

## Notes on Using This Timeline

- If the M.Tech program's actual timeline is shorter or longer than 8 months, scale phase durations proportionally, but **do not skip Phase 4 (Baselines)** — a paper without baseline comparison is very hard to publish.
- If time runs short, the safest phase to compress is Phase 8 (Dashboard) — a simpler dashboard is acceptable; a missing evaluation (Phase 9) is not.
- If following the **10-Day Rapid Build Sprint** (see the mapping section right after the Overview Table), treat Phases 0–8 as compressed but not skipped — every task listed under each phase still needs to happen, just in a shorter window and with reduced depth (e.g., lighter literature review, no exhaustive hyperparameter search). Phases 9–11 are intentionally left outside the sprint and should be picked back up at full depth once the prototype is live.
