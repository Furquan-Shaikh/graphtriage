# GraphTriage

## Quick Start (Docker, no setup)

Only **Docker Desktop** is needed (on Windows, WSL2 must be enabled). No `.env`, no build, no database setup.

```bash
git clone https://github.com/Furquan-Shaikh/graphtriage.git
cd graphtriage
docker compose up
```

The first run downloads a few GB of images (about 2-5 minutes on a good connection). When the logs show `Graph seed finished.`, open:

- App: http://localhost:8080 (login: `demo_user` / `ChangeMe123!`)
- Knowledge graph (Neo4j Browser): http://localhost:7474 (login: `neo4j` / `demo_neo4j_pass`)

Ports `8080`, `8000`, `3307`, `7474` and `7687` must be free. Images are built for `linux/amd64`.

To stop: `docker compose down` (add `-v` to also wipe the data).

Developers who want to build from source use:
`docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build`


Knowledge-Graph Based Explainable Ticket Triage and Root-Cause Linking System.
M.Tech CSE Final Year Project — AIOps / Software Engineering + AI.

**Full design docs live in `/docs`:**
- `docs/prd.md` — requirements
- `docs/architecture.md` — system architecture
- `docs/rules.md` — coding/dev conventions
- `docs/phases.md` — full timeline + 10-day rapid build sprint
- `docs/design.md` — schemas, API contracts, UI design
- `docs/memory.md` — decision log (update this as you go!)

**Day-by-day build guide:** see `DAY1_GUIDE.md` (Day 1), more will be added as each day is completed.

---

## Project Structure

```
graphtriage/
├── ticketing-service/   # Spring Boot API layer (Java)
├── inference-service/   # Python FastAPI ML/inference layer
├── graph-etl/            # Scripts to sync MySQL -> Neo4j
├── dashboard/            # Demo frontend
├── data/                 # Datasets (not committed if large/sensitive)
├── notebooks/            # Exploration / experiments
├── docs/                 # All planning documents
├── docker-compose.yml
├── .env.example
└── README.md
```

## Prerequisites

- Java 17 (JDK)
- Maven 3.9+
- Python 3.10+
- Docker Desktop (with Docker Compose)
- Git

## Quick Start (Local)

```bash
# 1. Copy environment template and fill in values
cp .env.example .env

# 2. Start everything (MySQL, Neo4j, ticketing-service, inference-service)
docker compose up --build

# 3. Verify services are healthy
curl http://localhost:8080/api/health      # ticketing-service (Spring Boot)
curl http://localhost:8000/health          # inference-service (FastAPI)

# 4. Open Neo4j Browser
# http://localhost:7474  (user: neo4j / password: from .env)
```

See `DAY1_GUIDE.md` for the full step-by-step walkthrough (including install instructions).
