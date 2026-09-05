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
| Current Phase | Phase 0 — Setup & Literature Review (see `phases.md`) |
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

---

## 4. Changelog

| Date | Change |
|---|---|
| Project kickoff | PRD, architecture, rules, phases, and design documents created and approved as the project foundation |

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
