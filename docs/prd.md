# Product Requirements Document (PRD)
## GraphTriage — Knowledge-Graph Based Explainable Ticket Triage and Root-Cause Linking System

**Document Version:** 1.0
**Project Type:** M.Tech CSE Final Year Project (Software Engineering + AI / AIOps)
**Status:** Approved for development

---

## 1. Document Control

| Field | Value |
|---|---|
| Document Owner | Student / Project Author |
| Reviewers | Project Mentor / Guide |
| Related Documents | architecture.md, rules.md, phases.md, design.md, memory.md |
| Last Updated | Start of project |

---

## 2. Executive Summary

GraphTriage is an AI-driven ticket triage system for microservice-based software platforms. Instead of treating each incoming support/bug ticket as an isolated piece of text to classify, GraphTriage builds a **knowledge graph** connecting tickets, services, historical bugs, fixes, and components. When a new ticket arrives, the system combines **graph-based reasoning** with **NLP embeddings** to:

1. Retrieve similar historical tickets/incidents.
2. Predict the most likely root cause and responsible service/component.
3. Estimate the expected resolution time.
4. Explain *why* each prediction was made (explainable AI).

The system is designed to be integrated into a real (or realistically simulated) Spring Boot-based microservices ticketing platform, evaluated with real/realistic ticket data, and written up as a research paper targeting a Scopus/SCI-indexed journal.

---

## 3. Problem Statement

In microservice-based systems, incoming tickets (bug reports, incidents, support requests) are typically triaged manually or through simple keyword/text classifiers. This approach has three core weaknesses:

1. **No historical memory** — each ticket is evaluated in isolation, ignoring the fact that many issues are recurrences or variations of past incidents.
2. **No structural context** — text classifiers do not understand *which services* are involved, *how* they depend on each other, or *which team* historically owns a given failure type.
3. **No explainability** — even when a model gets it right, engineers cannot see *why* it made that prediction, which reduces trust and adoption.

This results in slower root-cause identification, inconsistent ticket assignment, and inaccurate resolution-time estimates — all of which affect service reliability (a key AIOps concern) and team productivity.

---

## 4. Goals & Objectives

### Primary Goals
- **G1:** Build a knowledge graph that models the relationships between tickets, services, bugs, fixes, and components.
- **G2:** Build an ML pipeline (NLP embeddings + Graph Neural Network) that uses this graph to predict root cause, responsible service, and resolution time for a new ticket.
- **G3:** Provide human-readable explanations for every prediction (explainable AI layer).
- **G4:** Integrate the system into a working microservices ticketing platform (real or simulated) as a live service, not just an offline notebook experiment.
- **G5:** Produce a research paper suitable for submission to a reputed (Scopus/SCI-indexed) journal or conference.

### Secondary Goals
- **G6:** Provide a demo dashboard for visual presentation to the mentor/evaluators.
- **G7:** Keep the final thesis/report write-up plagiarism score below 30% through original design, code, and evaluation.

---

## 5. Target Users / Stakeholders

| Stakeholder | Interest |
|---|---|
| Project Mentor / Guide | Academic rigor, novelty, feasibility, correctness |
| Student (Developer) | Buildable scope, learning value, publishable outcome |
| (Simulated) Engineering Team | Faster triage, less manual root-cause hunting |
| Journal Reviewers | Novelty, sound methodology, reproducibility, clear evaluation |

---

## 6. Scope

### 6.1 In Scope
- Design and construction of a ticket–service–bug–fix knowledge graph.
- NLP-based ticket text embedding pipeline.
- Graph Neural Network (GNN) model for root-cause / responsible-service prediction.
- Regression model (or GNN prediction head) for resolution-time estimation.
- Explainability layer (SHAP and/or graph-attention-based explanations).
- REST API layer (Spring Boot) exposing triage predictions.
- Integration with a ticketing microservice (real internal system if available, otherwise a realistic simulated one — see Section 9).
- Evaluation against baseline text-classification approaches.
- A demo dashboard (basic web UI) to visualize predictions and explanations.
- Full academic write-up: literature review, methodology, results, discussion.

### 6.2 Out of Scope
- Building a full production-grade, horizontally scalable distributed system.
- Real-time streaming ingestion at large scale (batch/near-real-time is sufficient).
- Multi-tenant support (single-organization/testbed scope only).
- Mobile application front-end.
- Auto-remediation / auto-fixing of tickets (only prediction + explanation, not automated action).

---

## 7. Functional Requirements

| ID | Requirement | Priority | Acceptance Criteria |
|---|---|---|---|
| FR-1 | System shall ingest ticket data (title, description, metadata: service, timestamp, reporter, status) | Must | Tickets stored in MySQL and represented as graph nodes |
| FR-2 | System shall construct a knowledge graph linking Ticket → Service → Bug → Fix → Component | Must | Graph visible/queryable in Neo4j with correct relationships |
| FR-3 | System shall generate NLP embeddings for ticket text | Must | Each ticket has a fixed-size vector embedding stored |
| FR-4 | System shall retrieve top-K similar historical tickets for a new ticket | Must | API returns ranked similar tickets with similarity scores |
| FR-5 | System shall predict the likely root cause / responsible service for a new ticket | Must | Prediction returned with confidence score |
| FR-6 | System shall estimate resolution time for a new ticket | Must | Predicted time (e.g., in hours) returned with confidence interval |
| FR-7 | System shall generate an explanation for each prediction | Must | Explanation includes contributing features/graph paths |
| FR-8 | System shall expose predictions via a REST API | Must | Endpoints documented and testable via Postman |
| FR-9 | System shall provide a dashboard to view ticket, prediction, and explanation together | Should | Web page renders ticket + prediction + explanation |
| FR-10 | System shall log all predictions for later evaluation/audit | Should | Prediction logs stored with timestamps |
| FR-11 | System shall support re-training the model as new labeled tickets arrive | Could | A retraining script/pipeline exists and is documented |

---

## 8. Non-Functional Requirements

| Category | Requirement |
|---|---|
| Performance | Prediction response time under 2 seconds per ticket (excluding first-time model load) |
| Explainability | Every prediction must have an accompanying explanation — no "black box" outputs |
| Accuracy | Root-cause/service prediction should outperform a plain text-classification baseline (e.g., TF-IDF + Logistic Regression / plain BERT classifier) by a measurable margin |
| Reproducibility | All experiments must be reproducible from documented scripts and a fixed random seed |
| Maintainability | Code organized into clear modules per rules.md and architecture.md |
| Academic Integrity | Final report must score below 30% on plagiarism checks (Turnitin/Grammarly) |
| Portability | System should run locally via Docker Compose without cloud dependency (cloud optional for scaling demo) |

---

## 9. Data Requirements

GraphTriage needs historical ticket data with at least: ticket text (title + description), the service/component involved, the eventual root cause/fix category, and resolution time. Two acquisition paths are supported:

**Option A — Internal/Real System (preferred if available):**
Use anonymized historical tickets from an existing internal ticketing/microservices system (e.g., a Spring Boot-based ticketing platform), if such data is available and permitted for academic use.

**Option B — Public/Synthetic Fallback (if Option A is not available or insufficient in volume):**
- Public issue-tracker datasets (e.g., GitHub Issues from popular open-source microservices repositories, Bugzilla defect datasets, or public bug-report datasets used in Software Engineering research).
- A synthetic dataset generated by simulating a microservices environment (multiple services, injected fault types, generated ticket text via templates + paraphrasing) to ensure a labeled ground truth for root cause and resolution time.

The final dataset choice and its justification must be documented explicitly in the thesis/paper (data provenance is a common reviewer question).

---

## 10. Success Metrics / Evaluation Criteria

| Metric | Applies To | Target |
|---|---|---|
| Precision / Recall / F1 | Root-cause / responsible-service prediction | Outperform baseline by a clear, statistically noted margin |
| Mean Absolute Error (MAE) | Resolution-time estimation | Lower MAE than a naive average/baseline estimator |
| Top-K Retrieval Accuracy | Similar-ticket retrieval | Relevant past ticket appears in top-5 for a high majority of test cases |
| Explanation Usefulness | Explainability layer | Evaluated via a small human evaluation / rubric (e.g., 5-point clarity scale from a few evaluators) |
| System Latency | API/prediction endpoint | Under target response time defined in NFRs |
| Plagiarism Score | Final report | Below 30% |

---

## 11. Assumptions & Dependencies

- Assumes access to a ticketing dataset of reasonable size (minimum few hundred to a few thousand labeled tickets); if not available, synthetic data generation (Option B) is used.
- Assumes a Spring Boot microservices environment (existing or newly built) is available for live integration.
- Assumes access to compute sufficient for training a small-to-medium GNN (a single GPU is helpful but not strictly required for the target dataset scale; CPU training is feasible for a modestly sized graph).
- Assumes mentor approval on scope before implementation begins.

---

## 12. Risks & Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Insufficient real ticket data volume | Weak model training / evaluation | Fall back to Option B synthetic/public dataset; clearly document limitation |
| GNN training complexity underestimated | Timeline slip | Start with a simpler graph-based baseline (e.g., node2vec + classifier) before full GNN, per phases.md |
| Explainability outputs are not convincing | Weak paper contribution | Validate explanations qualitatively early, iterate before final evaluation |
| Plagiarism in literature review | Academic penalty | Follow rules.md citation and paraphrasing discipline; run checks before every major submission |
| Scope creep (trying to build a "real production system") | Timeline slip | Strictly follow the "In Scope / Out of Scope" boundaries in Section 6 |

---

## 13. Academic Deliverables

1. Approved project proposal (this PRD serves as the basis).
2. Working prototype (all modules per architecture.md).
3. Evaluation report with metrics from Section 10.
4. Final thesis/dissertation document.
5. Research paper draft targeting a Scopus/SCI-indexed venue.
6. Live demo for mentor/evaluation panel.

---

## 14. Glossary

| Term | Meaning |
|---|---|
| AIOps | Artificial Intelligence for IT Operations |
| GNN | Graph Neural Network |
| Root Cause | The underlying reason a ticket/incident occurred |
| Knowledge Graph | A graph database representing entities and their relationships |
| Explainability (XAI) | Techniques that make ML model outputs interpretable to humans |
| SHAP | SHapley Additive exPlanations — a model explainability technique |

---

## 15. Related Documents
- `architecture.md` — system architecture and technical design
- `rules.md` — coding standards and development conventions
- `phases.md` — phase-by-phase project timeline
- `design.md` — detailed schema, API, and UI design
- `memory.md` — running decision log and project memory
