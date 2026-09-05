# Day 1 Guide — Setup

**Maps to:** `docs/phases.md` → Phase 0 (Setup part; literature review can happen in parallel/evenings, it doesn't block any of this).

**Goal by end of today:** A GitHub repo exists with the exact structure below, and `docker compose up` successfully starts MySQL + Neo4j + ticketing-service (Spring Boot) + inference-service (FastAPI), with both `/api/health` and `/health` returning `UP`.

---

## Step 0 — Install Prerequisites

Install these on your machine before anything else:

| Tool | Version | Check with |
|---|---|---|
| Java (JDK) | 17 | `java -version` |
| Maven | 3.9+ | `mvn -version` |
| Python | 3.10+ | `python3 --version` |
| Docker Desktop | latest | `docker --version` and `docker compose version` |
| Git | latest | `git --version` |

- **Windows:** Install Java via [Adoptium Temurin 17](https://adoptium.net/), Maven via their installer or `choco install maven`, Docker Desktop from docker.com (enable WSL2 backend when prompted).
- **Mac:** `brew install openjdk@17 maven python git`, then Docker Desktop from docker.com.
- **Linux:** `sudo apt install openjdk-17-jdk maven python3 python3-pip git`, then Docker Engine + Compose plugin per Docker's official Ubuntu install guide.

Do not proceed to Step 1 until all five `Check with` commands above run without error.

---

## Step 1 — Create the GitHub Repository

```bash
# On GitHub.com: create a new empty repository named "graphtriage"
# (no README/gitignore from GitHub's side — we already have our own)

# Locally:
mkdir graphtriage && cd graphtriage
git init
git branch -M main
git remote add origin https://github.com/<your-username>/graphtriage.git
```

Now copy in every file from this delivered project structure into this `graphtriage/` folder (the structure is described in `README.md` at the root, and every file has already been created for you — `ticketing-service/`, `inference-service/`, `docs/`, etc.).

```bash
git add .
git commit -m "chore: initial project scaffold (Day 1)"
git push -u origin main
```

---

## Step 2 — Prepare Your Environment File

```bash
cp .env.example .env
```

Open `.env` and change at least the passwords (`MYSQL_ROOT_PASSWORD`, `MYSQL_PASSWORD`, `NEO4J_AUTH`/`NEO4J_PASSWORD`) to something real — even for local dev, don't leave them as `changeme_*`, since these same values will later map to hosting secrets on Day 10.

**Note:** `.env` is already in `.gitignore` — never commit it.

---

## Step 3 — Start Everything With Docker Compose

```bash
docker compose up --build
```

What happens:
1. MySQL container starts and creates the `graphtriage` database.
2. Neo4j container starts (Browser UI on port 7474, Bolt protocol on 7687).
3. `ticketing-service` builds (Maven downloads dependencies — this step needs internet access and will take a few minutes the first time) and starts on port 8080.
4. `inference-service` builds (pip installs FastAPI/uvicorn — fast, no heavy ML libraries yet per `requirements.txt`) and starts on port 8000.

Leave this terminal running. Open a **second terminal** for the verification step.

---

## Step 4 — Verify Everything Is Actually Working

```bash
# Spring Boot ticketing-service
curl http://localhost:8080/api/health
```
Expected response:
```json
{"service":"ticketing-service","status":"UP","timestamp":"...","inferenceServiceUrl":"http://inference-service:8000"}
```

```bash
# FastAPI inference-service
curl http://localhost:8000/health
```
Expected response:
```json
{"service":"inference-service","status":"UP","timestamp":"...","neo4j_uri_configured":"bolt://neo4j:7687"}
```

```bash
# Neo4j Browser - open in your actual browser, not curl
# http://localhost:7474
# Login with: neo4j / <the password you set in NEO4J_AUTH>
```

```bash
# MySQL - confirm the database exists
docker exec -it graphtriage-mysql mysql -u root -p -e "SHOW DATABASES;"
# enter MYSQL_ROOT_PASSWORD when prompted - you should see 'graphtriage' listed
```

If all four checks pass, **Day 1 is complete.**

---

## Step 5 — Log It in memory.md

Open `docs/memory.md` and add a line under **Section 4 (Changelog)**:

```
| <today's date> | Day 1 complete: repo scaffolded, Docker Compose stack (MySQL, Neo4j,
ticketing-service, inference-service) verified healthy end-to-end. |
```

This takes two minutes now and saves real time later when writing the thesis methodology section.

---

## Troubleshooting

| Problem | Likely Cause | Fix |
|---|---|---|
| `ticketing-service` fails to build | No internet access for Maven to reach Maven Central | Check your network/firewall; corporate networks sometimes block Maven Central — try a mobile hotspot to confirm |
| `mysql` container keeps restarting | Password mismatch between `.env` and an old volume | `docker compose down -v` (removes volumes) then `docker compose up --build` again |
| Port already in use (8080/8000/3306/7474/7687) | Another local service is using that port | Stop the conflicting service, or change the port mapping in `docker-compose.yml` |
| `curl` returns connection refused | Containers still starting | Wait 30-60 seconds after `docker compose up`, especially on first run |

---

## What's Next

Once Day 1 is verified, move to **Day 2** (`docs/phases.md` → Phase 1): synthetic dataset generation and loading into MySQL. Ask for the Day 2 scripts the same way once you're ready.
