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
| Current Phase | Phase 3 — NLP Embedding Pipeline (see `phases.md`) — Phase 0, 1 & 2 / Sprint Days 1-3 complete |
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
