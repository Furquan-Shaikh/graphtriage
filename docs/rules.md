# Development Rules & Conventions — GraphTriage

**Related Documents:** prd.md, architecture.md, phases.md, design.md, memory.md

This document defines the working rules for building GraphTriage — coding standards, workflow, and academic-integrity discipline. Follow these consistently from day one so that the codebase and the thesis write-up stay clean, consistent, and defensible in front of the mentor and journal reviewers.

---

## 1. Purpose of This Document

To ensure that: (a) the codebase remains organized and maintainable across a multi-month solo project, (b) the eventual thesis/paper accurately reflects original, well-documented work, and (c) if an AI coding assistant is used to help implement parts of the system, it is guided by consistent, explicit rules rather than ad-hoc instructions each time.

---

## 2. Repository Structure

```
graphtriage/
├── ticketing-service/          # Spring Boot application (API layer)
│   ├── src/main/java/...
│   ├── src/test/java/...
│   └── pom.xml
├── inference-service/          # Python FastAPI application (ML layer)
│   ├── app/
│   │   ├── embeddings/
│   │   ├── gnn_model/
│   │   ├── explainability/
│   │   └── main.py
│   ├── tests/
│   └── requirements.txt
├── graph-etl/                  # ETL scripts to sync MySQL -> Neo4j
├── dashboard/                  # Frontend demo dashboard
├── data/                       # Raw/processed datasets (never commit large/sensitive files)
├── notebooks/                  # Exploratory analysis, model experimentation
├── docs/                       # prd.md, architecture.md, rules.md, phases.md, design.md, memory.md
├── docker-compose.yml
└── README.md
```

---

## 3. Coding Standards

### 3.1 Java (Spring Boot)
- Follow standard Java naming conventions (PascalCase for classes, camelCase for methods/variables).
- Controllers stay thin — no business logic in `@RestController` classes; delegate to `@Service` classes.
- All external I/O (DB, HTTP calls to inference service) wrapped in a `@Service` or `@Repository` layer, never called directly from controllers.
- Use DTOs for request/response bodies — never expose JPA entities directly over the API.
- All new endpoints must have at least one corresponding unit or integration test.

### 3.2 Python (Inference Service)
- Follow PEP 8 style; use `black` for formatting and `flake8`/`ruff` for linting.
- Keep embedding generation, GNN model code, and explainability code in **separate modules** (no monolithic scripts).
- Every model class/function must have a docstring explaining inputs, outputs, and purpose (this doubles as material for the "Methodology" section of the paper).
- Configuration (model paths, hyperparameters) must live in a config file (e.g., `config.yaml`), not hardcoded.

### 3.3 General
- No hardcoded secrets, passwords, or API keys anywhere in code — use environment variables (see Section 9).
- No commented-out dead code left in commits — delete it (Git history preserves it if needed).

---

## 4. Git Workflow & Branching Strategy

- `main` — always stable/demo-ready.
- `dev` — active integration branch.
- Feature branches: `feature/<short-description>` (e.g., `feature/gnn-training-pipeline`).
- Never commit directly to `main`; merge via pull request (even solo — this creates a clean, reviewable history for the thesis appendix if needed).

## 5. Commit Message Convention

Use a simple conventional format:
```
<type>: <short description>

<optional longer description>
```
Types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `experiment`

Example:
```
feat: add GraphSAGE-based root-cause prediction head

Implements the initial GNN model architecture described in architecture.md
Section 6. Trained on synthetic dataset v1 for smoke testing.
```

---

## 6. Code Review Checklist (self-review, since solo project)

Before merging any feature branch, confirm:
- [ ] Code follows the standards in Section 3.
- [ ] New functionality has at least minimal test coverage.
- [ ] No secrets/credentials committed.
- [ ] Relevant documentation (`design.md` / `memory.md`) updated if the change affects schema, API, or a key decision.
- [ ] No large binary/dataset files committed to Git (use `.gitignore`).

---

## 7. Testing Requirements

| Layer | Testing Approach |
|---|---|
| Spring Boot API | JUnit + Mockito for unit tests; Postman collection for manual/integration testing |
| Inference Service | Pytest for unit tests on embedding, model inference, and explainability functions |
| ML Model | Held-out test set evaluation using metrics defined in prd.md Section 10 |
| End-to-End | At least one full flow test: create ticket → get prediction → get explanation |

---

## 8. Documentation Standards

- Every module/service must have its own `README.md` explaining how to run and test it locally.
- Any architectural decision that deviates from `architecture.md` must be recorded in `memory.md` (decision log) with a short rationale.
- All API endpoints documented (OpenAPI/Swagger annotations in Spring Boot recommended, since this also reuses relevant backend experience).

---

## 9. Environment & Secrets Management

- Use `.env` files (excluded from Git via `.gitignore`) for local secrets (DB passwords, JWT signing key).
- Provide a `.env.example` file with placeholder values so the setup is reproducible for the mentor/evaluators.

---

## 10. Logging & Monitoring Standards

- Use structured logging (e.g., SLF4J in Spring Boot, Python `logging` module in the inference service).
- Log every prediction request with: ticket ID, timestamp, prediction output, confidence score (needed later for the evaluation section of the paper).
- Do not log full ticket text at INFO level if the dataset is sensitive/internal — log ticket ID references only.

---

## 11. Academic Integrity & Plagiarism Rules

These rules exist specifically to keep the final report's plagiarism score below 30% (per prd.md Section 8):

1. **Never copy-paste** sentences from papers, blogs, or documentation directly into the thesis or paper — always paraphrase in your own words and cite the source.
2. **One-quote-max rule for any external text:** if a definition or phrase absolutely must be quoted, keep it short, quoted properly, and cited — do not lean on quotations to fill content.
3. Related-work/literature-review sections are the highest-risk area for accidental plagiarism — write these last, after fully understanding the papers, rather than paraphrasing sentence-by-sentence while reading them.
4. Run the full draft through a plagiarism checker (Turnitin/Grammarly or the tool your institution provides) **before** every major submission milestone (see phases.md), not just once at the end.
5. All code adapted from tutorials/StackOverflow/open-source examples must be clearly attributed in code comments and in the thesis appendix, even though code plagiarism and text plagiarism are usually checked separately.
6. Dataset descriptions, figures, and diagrams should be self-created (or clearly cited if adapted), not copied from source papers.

---

## 12. AI-Assisted Development Rules

If an AI coding assistant (e.g., Claude Code, Copilot, ChatGPT) is used to help implement parts of the system:

1. Treat AI output as a **first draft**, not final code — review and understand every generated function before committing it.
2. Never let the AI assistant write the literature review or paper text verbatim from source papers — use it only to help paraphrase or structure your own understanding.
3. Keep this `rules.md`, `architecture.md`, and `phases.md` as the source of truth/context for any AI assistant working on the codebase, so its suggestions stay consistent with the agreed design.
4. Log any significant AI-assisted design decision in `memory.md`, same as any other decision.
5. Be prepared to explain and defend every part of the system to the mentor — "the AI wrote it" is never an acceptable answer during evaluation.

---

## 13. Definition of Done (per feature/module)

A module is considered "done" only when:
- [ ] It meets its functional requirement(s) from `prd.md`.
- [ ] It has tests passing per Section 7.
- [ ] It is documented per Section 8.
- [ ] It is integrated and demonstrable end-to-end (not just working in isolation).
- [ ] Any deviation from the original design is recorded in `memory.md`.
