# Detailed Design — GraphTriage

**Related Documents:** prd.md, architecture.md, rules.md, phases.md, memory.md

This document specifies the concrete schemas, model design, API contracts, and UI layout needed to implement GraphTriage.

---

## 1. Relational Database Schema (MySQL)

```sql
CREATE TABLE service (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    owning_team VARCHAR(100)
);

CREATE TABLE component (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    service_id INT,
    FOREIGN KEY (service_id) REFERENCES service(id)
);

CREATE TABLE ticket (
    id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    service_id INT,
    component_id INT,
    status VARCHAR(30) DEFAULT 'OPEN',
    priority VARCHAR(20),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    resolved_at DATETIME NULL,
    dataset_split VARCHAR(10) DEFAULT NULL, -- 'train' / 'val' / 'test' (added Sprint Day 2)
    FOREIGN KEY (service_id) REFERENCES service(id),
    FOREIGN KEY (component_id) REFERENCES component(id)
);

CREATE TABLE bug (
    id INT PRIMARY KEY AUTO_INCREMENT,
    ticket_id INT NOT NULL,
    category VARCHAR(100),
    severity VARCHAR(20),
    FOREIGN KEY (ticket_id) REFERENCES ticket(id)
);

CREATE TABLE fix (
    id INT PRIMARY KEY AUTO_INCREMENT,
    bug_id INT NOT NULL,
    description TEXT,
    resolution_time_hours FLOAT,
    FOREIGN KEY (bug_id) REFERENCES bug(id)
);

CREATE TABLE prediction_log (
    id INT PRIMARY KEY AUTO_INCREMENT,
    ticket_id INT NOT NULL,
    predicted_service VARCHAR(100),
    predicted_root_cause VARCHAR(150),
    predicted_resolution_hours FLOAT,
    confidence FLOAT,
    explanation TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ticket_id) REFERENCES ticket(id)
);
```

---

## 2. Knowledge Graph Schema (Neo4j)

**Node Labels & Properties:**

```
(:Ticket {id, title, description, status, priority, created_at})
(:Service {id, name, owning_team})
(:Component {id, name})
(:Bug {id, category, severity})
(:Fix {id, description, resolution_time_hours})
```

**Relationships:**

```
(:Ticket)-[:RAISED_ON]->(:Service)
(:Ticket)-[:INVOLVES]->(:Component)
(:Ticket)-[:CAUSED_BY]->(:Bug)
(:Bug)-[:FIXED_BY]->(:Fix)
(:Service)-[:DEPENDS_ON]->(:Service)
(:Ticket)-[:SIMILAR_TO {score}]->(:Ticket)
```

**Sample Cypher — creating a ticket node and linking it:**

```cypher
MERGE (t:Ticket {id: $ticketId})
SET t.title = $title, t.description = $description,
    t.status = $status, t.priority = $priority, t.created_at = $createdAt
MERGE (s:Service {name: $serviceName})
MERGE (t)-[:RAISED_ON]->(s)
```

**Sample Cypher — finding similar tickets on a shared service that led to a known fix:**

```cypher
MATCH (t:Ticket {id: $ticketId})-[:RAISED_ON]->(s:Service)
MATCH (other:Ticket)-[:RAISED_ON]->(s)
MATCH (other)-[:CAUSED_BY]->(b:Bug)-[:FIXED_BY]->(f:Fix)
WHERE other.id <> t.id
RETURN other, b, f
ORDER BY f.resolution_time_hours ASC
LIMIT 5
```

---

## 3. ML Model Design

### 3.1 Embedding Model
- Model: `sentence-transformers/all-MiniLM-L6-v2` (or similar lightweight model — good balance of speed and quality for a student compute budget).
- Input: concatenated ticket title + description (truncated to model's max token length).
- Output: 384-dimensional dense vector per ticket.

### 3.2 Graph Neural Network
- Framework: PyTorch Geometric.
- Architecture: 2–3 layer **GraphSAGE** (simpler, faster to train) as the primary model; **GAT (Graph Attention Network)** as an optional upgrade if attention-based explainability is desired.
- Node features: text embedding (Section 3.1) concatenated with basic categorical features (priority, service one-hot, etc.).
- Prediction heads (multi-task):
  - **Classification head:** softmax over root-cause categories / responsible services.
  - **Regression head:** predicts resolution time in hours.
- Loss function: weighted sum of cross-entropy (classification head) and mean squared error / mean absolute error (regression head).
- Training: Adam optimizer, learning rate ~1e-3 to 1e-4 (tune per dataset size), early stopping on validation loss.

### 3.3 Explainability
- **SHAP:** applied on the tabular/text-feature side to show which input features (words, priority, service) contributed most to a prediction.
- **Attention weights (if GAT used):** show which neighboring graph nodes (e.g., which past ticket/service) most influenced the prediction — this becomes the "graph path explanation."
- Output format (combined):
```json
{
  "top_contributing_features": ["keyword: timeout", "service: payment-service", "priority: high"],
  "top_similar_past_tickets": [
    {"ticket_id": 482, "similarity": 0.91, "resolved_via": "connection pool fix"}
  ],
  "confidence": 0.83
}
```

---

## 4. API Design (Full Specification)

### 4.1 `POST /api/tickets`
**Request:**
```json
{
  "title": "Payment service timing out under load",
  "description": "Users report checkout failures during peak traffic...",
  "serviceName": "payment-service",
  "priority": "HIGH"
}
```
**Response (201 Created):**
```json
{
  "id": 501,
  "status": "OPEN",
  "createdAt": "2026-09-05T10:00:00Z"
}
```

### 4.2 `GET /api/tickets/{id}/predict`
**Response (200 OK):**
```json
{
  "ticketId": 501,
  "predictedService": "payment-service",
  "predictedRootCause": "connection-pool-exhaustion",
  "predictedResolutionHours": 6.5,
  "confidence": 0.83
}
```

### 4.3 `GET /api/tickets/{id}/similar`
**Response (200 OK):**
```json
{
  "ticketId": 501,
  "similarTickets": [
    {"id": 482, "similarityScore": 0.91, "title": "Checkout failures on payment-service"},
    {"id": 390, "similarityScore": 0.85, "title": "payment-service latency spike"}
  ]
}
```

### 4.4 `GET /api/tickets/{id}/explain`
**Response (200 OK):**
```json
{
  "ticketId": 501,
  "topContributingFeatures": ["keyword: timeout", "service: payment-service", "priority: high"],
  "supportingPastTickets": [
    {"ticketId": 482, "resolvedVia": "connection pool fix"}
  ],
  "confidence": 0.83
}
```

### 4.5 `POST /api/auth/login`
Standard JWT login endpoint, reusing existing Spring Security patterns:
```json
// Request
{ "username": "mentor_demo", "password": "********" }
// Response
{ "token": "eyJhbGciOi..." }
```

---

## 5. UI / Dashboard Design (Wireframe Description)

Since this is a demo dashboard (not a production product), a simple single-page layout is sufficient:

```
┌───────────────────────────────────────────────────────────┐
│  GraphTriage Dashboard                          [Login]     │
├───────────────────────────────────────────────────────────┤
│  Ticket List (left panel)     │   Ticket Detail (right)     │
│  ─────────────────────────    │   ───────────────────────   │
│  #501 Payment timeout   ▶     │   Title, Description         │
│  #500 Auth failures     ▶     │   Predicted Service: ...     │
│  #499 Slow search       ▶     │   Predicted Root Cause: ...  │
│                                │   Resolution Estimate: ...   │
│                                │   Confidence: 83%            │
│                                │   ─────────────────────      │
│                                │   Explanation Panel:         │
│                                │   - Top contributing terms   │
│                                │   - Similar past tickets     │
│                                │   - (Optional) Graph view    │
└───────────────────────────────────────────────────────────┘
```

- **Left panel:** list of tickets (fetched from `GET /api/tickets`).
- **Right panel:** on selecting a ticket, calls `/predict`, `/similar`, and `/explain` in parallel and renders results.
- **Optional enhancement:** embed a small Neo4j graph visualization (e.g., using `neovis.js`) showing the ticket's local subgraph.

---

## 6. Key Sequence Diagram (Textual) — New Ticket Prediction Flow

```
User/Client        Spring Boot API       Inference Service        Neo4j          MySQL
    │                     │                       │                  │              │
    │  POST /tickets      │                       │                  │              │
    │────────────────────▶│                       │                  │              │
    │                     │  INSERT ticket        │                  │              │
    │                     │───────────────────────────────────────────────────────▶│
    │                     │  MERGE ticket node     │                 │              │
    │                     │────────────────────────────────────────▶│              │
    │  GET /predict       │                       │                  │              │
    │────────────────────▶│  call /infer          │                  │              │
    │                     │──────────────────────▶│                  │              │
    │                     │                       │  read subgraph   │              │
    │                     │                       │─────────────────▶│              │
    │                     │                       │◀─────────────────│              │
    │                     │                       │  run GNN model    │             │
    │                     │◀──────────────────────│  return prediction│             │
    │                     │  log prediction        │                  │             │
    │                     │────────────────────────────────────────────────────────▶│
    │◀────────────────────│  return JSON response │                  │              │
```

---

## 7. Design Notes for the Mentor Presentation

When presenting this design document, emphasize three points that reviewers/mentors typically look for:
1. **Clear separation of concerns** (ticketing system vs. ML inference vs. graph store) — shows sound software engineering, not just a script.
2. **Every prediction is explainable** — directly addresses a known gap in AIOps triage tools.
3. **Baselines are built before the main model** — shows methodological rigor expected in a publishable evaluation.
