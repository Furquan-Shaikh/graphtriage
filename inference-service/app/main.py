"""
GraphTriage - inference-service (Day 1 skeleton)

This is the Python FastAPI service described in architecture.md that will host:
- NLP embedding generation (Day 4)
- GNN model inference (Day 5)
- Explainability (Day 6)

On Day 1 it only exposes a health check so we can confirm the full stack
(Spring Boot + Neo4j + this service) is wired together correctly via Docker Compose.
"""

import os
from datetime import datetime, timezone

from fastapi import FastAPI

app = FastAPI(
    title="GraphTriage Inference Service",
    description="ML/inference layer for GraphTriage — embeddings, GNN predictions, explainability.",
    version="0.1.0",
)


@app.get("/health")
def health():
    return {
        "service": "inference-service",
        "status": "UP",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "neo4j_uri_configured": os.getenv("NEO4J_URI", "not-configured"),
    }


@app.get("/")
def root():
    return {"message": "GraphTriage inference-service is running. See /health and /docs."}
