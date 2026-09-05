# System Architecture — GraphTriage

**Related Documents:** prd.md, rules.md, phases.md, design.md, memory.md

---

## 1. Architecture Overview

GraphTriage is composed of five logical layers: **Ingestion**, **Knowledge Graph**, **ML/Intelligence**, **Serving (API)**, and **Presentation (Dashboard)**.

```
                        ┌───────────────────────────────────────────┐
                        │              PRESENTATION LAYER            │
                        │   Web Dashboard (ticket view + prediction  │
                        │      + explanation visualization)          │
                        └───────────────────▲─────────────────────────┘
                                            │ REST/JSON
                        ┌───────────────────┴─────────────────────────┐
                        │                SERVING LAYER                 │
                        │        Spring Boot REST API (Java)           │
                        │  /tickets  /predict  /similar  /explain      │
                        └───────────────────▲─────────────────────────┘
                                            │ internal call / gRPC / REST
                        ┌───────────────────┴─────────────────────────┐
                        │             ML / INTELLIGENCE LAYER          │
                        │  ┌───────────────┐  ┌──────────────────┐    │
                        │  │ NLP Embedding │  │  GNN Model        │    │
                        │  │ (Sentence-BERT│─▶│ (PyTorch Geometric│    │
                        │  │  )            │  │  root-cause +     │    │
                        │  └───────────────┘  │  resolution-time  │    │
                        │                     │  prediction heads)│    │
                        │                     └─────────┬─────────┘    │
                        │                               │              │
                        │                     ┌─────────▼─────────┐    │
                        │                     │  Explainability    │   │
                        │                     │  (SHAP / attention)│   │
                        │                     └────────────────────┘   │
                        └───────────────────▲─────────────────────────┘
                                            │ read/write graph
                        ┌───────────────────┴─────────────────────────┐
                        │             KNOWLEDGE GRAPH LAYER            │
                        │                Neo4j Graph DB                │
                        │  Nodes: Ticket, Service, Bug, Fix, Component │
                        │  Edges: RAISED_ON, CAUSED_BY, FIXED_BY,      │
                        │         DEPENDS_ON, SIMILAR_TO               │
                        └───────────────────▲─────────────────────────┘
                                            │ ETL / sync
                        ┌───────────────────┴─────────────────────────┐
                        │               INGESTION LAYER                │
                        │   Ticketing Microservice(s) (Spring Boot)    │
                        │        + MySQL (system of record)            │
                        └───────────────────────────────────────────────┘
```

---

## 2. Component Breakdown

| Component | Responsibility | Technology |
|---|---|---|
| Ticketing Microservice | Source of truth for raw ticket data (create/update/close tickets) | Spring Boot, MySQL |
| ETL / Sync Service | Reads new/updated tickets from MySQL and updates the knowledge graph | Python or Java scheduled job |
| Knowledge Graph Store | Stores structured relationships between tickets, services, bugs, fixes | Neo4j |
| Embedding Service | Converts ticket text into dense vector embeddings | Python, Sentence-Transformers |
| GNN Model Service | Learns from the graph + embeddings to predict root cause, service, resolution time | Python, PyTorch Geometric |
| Explainability Module | Produces human-readable explanations per prediction | Python, SHAP / attention-weight extraction |
| Prediction API | Exposes predictions and explanations over REST | Spring Boot (Java) calling into a Python inference service |
| Inference Microservice | Hosts the trained ML model for serving predictions | Python (FastAPI or Flask), used internally by the Spring Boot API |
| Dashboard | Visual interface for mentor/demo presentation | Simple web frontend (HTML/JS or React) |

> **Note on Java/Python boundary:** Since the student's core strength is Java/Spring Boot, the recommended pattern is: **Spring Boot owns the public API and business logic**, and internally calls a small **Python inference microservice** (FastAPI) that wraps the trained ML model. This keeps the ML code isolated, testable, and swappable, while showcasing both Java backend skills and ML skills — which is valuable both for the academic evaluation and for the "systems" contribution of the paper.

---

## 3. Data Flow

**3.1 Ingestion & Graph Construction (offline / periodic)**
1. New ticket created in the Ticketing Microservice → stored in MySQL.
2. ETL job reads new/updated tickets.
3. ETL job creates/updates graph nodes (Ticket, Service, Component) and edges (RAISED_ON, DEPENDS_ON) in Neo4j.
4. When a ticket is resolved, its Bug/Fix nodes and CAUSED_BY / FIXED_BY edges are added.

**3.2 Prediction Flow (online, per new ticket)**
1. New ticket text arrives at the Spring Boot API (`POST /tickets`).
2. API stores the ticket in MySQL and triggers graph node creation.
3. API calls the Inference Microservice with the ticket text + ticket ID.
4. Inference Microservice:
   a. Generates an NLP embedding for the ticket text.
   b. Loads the relevant subgraph neighborhood from Neo4j.
   c. Runs the GNN model to predict root cause / responsible service and resolution time.
   d. Runs the explainability module to generate supporting evidence (top contributing similar tickets, top contributing graph paths/features).
5. Inference Microservice returns prediction + explanation as JSON.
6. Spring Boot API stores the prediction (for audit/evaluation) and returns it to the caller/dashboard.

**3.3 Similarity Retrieval Flow**
1. Client calls `GET /tickets/{id}/similar`.
2. Inference Microservice computes embedding similarity (and/or graph-based proximity) against historical tickets.
3. Top-K similar tickets returned with similarity scores and short justifications.

---

## 4. Technology Stack

| Layer | Technology | Notes |
|---|---|---|
| Backend API | Java 17, Spring Boot 3.x | REST controllers, service layer, JWT auth (reusing existing expertise) |
| Relational DB | MySQL 8.x | System of record for tickets, users, services |
| Graph DB | Neo4j 5.x (Community Edition) | Knowledge graph storage and traversal (Cypher queries) |
| ML/Inference Service | Python 3.10+, FastAPI | Hosts embedding + GNN + explainability logic |
| NLP Embeddings | Sentence-Transformers (e.g., `all-MiniLM-L6-v2` or similar) | Converts ticket text to vectors |
| Graph Learning | PyTorch, PyTorch Geometric (PyG) | GNN model (e.g., GraphSAGE or GAT) |
| Explainability | SHAP, and/or native GNN attention weights (if using GAT) | Generates per-prediction explanations |
| Containerization | Docker, Docker Compose | Local multi-service orchestration |
| API Testing | Postman / cURL | Manual and scripted API verification |
| Version Control | Git + GitHub | Source control, per rules.md |
| Frontend (Dashboard) | HTML/CSS/JS (or lightweight React) | Simple internal demo dashboard, not production-grade |

---

## 5. Knowledge Graph Schema (High-Level)

**Node Types:**
- `Ticket` — properties: id, title, description, created_at, status, priority
- `Service` — properties: name, owning_team
- `Component` — properties: name, service_id
- `Bug` — properties: id, category, severity
- `Fix` — properties: id, description, resolution_time_hours
- `Developer` (optional, if data available) — properties: id, name, team

**Relationship Types:**
- `(Ticket)-[:RAISED_ON]->(Service)`
- `(Ticket)-[:INVOLVES]->(Component)`
- `(Ticket)-[:CAUSED_BY]->(Bug)`
- `(Bug)-[:FIXED_BY]->(Fix)`
- `(Service)-[:DEPENDS_ON]->(Service)`
- `(Ticket)-[:SIMILAR_TO {score: float}]->(Ticket)` — computed/updated periodically from embeddings
- `(Fix)-[:RESOLVED_BY]->(Developer)` (optional)

Full property lists and Cypher creation scripts are specified in `design.md`.

---

## 6. ML Pipeline Architecture

```
Ticket Text ──▶ Sentence Embedding (Sentence-BERT)
                        │
                        ▼
        Combine with Graph Structural Features
     (node embeddings from graph, e.g., via GraphSAGE)
                        │
                        ▼
              Fused Representation Vector
                        │
           ┌────────────┼─────────────────┐
           ▼            ▼                 ▼
   Root-Cause /   Resolution-Time   Similar-Ticket
   Service Head   Regression Head    Retrieval (ANN
   (classifier)   (regressor)        search over
                                     embeddings)
           │            │                 │
           ▼            ▼                 ▼
      Explainability Module (SHAP for tabular/text features,
      attention weights for graph contributions)
```

- **Baseline models first** (per phases.md): TF-IDF + Logistic Regression / Random Forest for classification, and a simple average-based estimator for resolution time — used as comparison points required for the paper's evaluation section.
- **Main model:** GNN (GraphSAGE or GAT) operating on the ticket-service-bug-fix graph, combined with text embeddings as node features.

---

## 7. API Layer (Summary — full spec in design.md)

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/tickets` | POST | Create a new ticket |
| `/api/tickets/{id}` | GET | Get ticket details |
| `/api/tickets/{id}/predict` | GET | Get root-cause/service + resolution-time prediction |
| `/api/tickets/{id}/similar` | GET | Get top-K similar historical tickets |
| `/api/tickets/{id}/explain` | GET | Get explanation for the latest prediction |
| `/api/auth/login` | POST | JWT-based authentication (reusing existing Spring Security expertise) |

---

## 8. Deployment Architecture

Local development/demo environment via Docker Compose with the following services:

```yaml
services:
  mysql:            # system of record
  neo4j:            # knowledge graph
  ticketing-service: # Spring Boot app (API layer)
  inference-service:  # Python FastAPI app (ML layer)
  dashboard:          # static/simple frontend
```

All services run on a local Docker network; the Spring Boot service calls the inference service over internal HTTP (e.g., `http://inference-service:8000`).

> **Note (added Sprint Day 1):** On the host machine, MySQL is exposed on port **3307** (not the default 3306), mapped to the container's internal 3306 — this avoids a common conflict with a pre-existing local MySQL installation on Windows. This only affects host-side access (e.g., a local MySQL client); internal service-to-service communication is unaffected since it uses the Docker network hostname `mysql:3306`. See `memory.md` Section 3 for the full decision record.

---

## 9. Scalability & Performance Considerations

- The system is designed for **demo/academic scale** (hundreds to a few thousand tickets), not enterprise scale — this should be explicitly stated as a scope boundary in the paper.
- For future scalability discussion (useful for the "Future Work" section of the paper): batching graph updates, caching embeddings, using approximate nearest-neighbor search (e.g., FAISS) for similarity retrieval at larger scale, and moving to a graph database cluster.

---

## 10. Security Architecture

- JWT-based authentication and role-based access on the Spring Boot API (reusing existing Spring Security experience).
- Inference microservice is **not** exposed publicly — only reachable internally from the Spring Boot service.
- No real/sensitive production data should be used without anonymization if Option A (internal dataset) is chosen.

---

## 11. Explainability Architecture

Two complementary explanation mechanisms:
1. **Feature-level explanation (SHAP):** which words/features in the ticket text and which structural features (e.g., "service X has had 5 similar past incidents") contributed most to the prediction.
2. **Graph-path explanation:** the specific graph path(s) (e.g., Ticket → Service → past Bug → Fix) that most influenced the retrieved similar ticket / predicted root cause.

Both are surfaced together in the `/explain` endpoint response and shown side-by-side in the dashboard.

---

## 12. Failure Modes & Resilience

| Failure | Handling |
|---|---|
| Inference service down | Spring Boot API returns a graceful degraded response (e.g., similarity search only, no ML prediction) with a clear error status |
| Neo4j unavailable | Ticket creation still succeeds in MySQL; graph sync retried via a background job |
| Model prediction low-confidence | Explicitly surface confidence score; below a threshold, mark prediction as "low confidence" instead of hiding uncertainty |
