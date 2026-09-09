"""
GraphTriage - inference-service

Hosts the ML/inference layer for GraphTriage:
- NLP embedding generation (Day 4)
- GNN model inference (Day 5) - inductive prediction for brand-new tickets
- Explainability (Day 6) - SHAP keywords + graph-based similar tickets

Day 7: wired up as real, callable endpoints for the Spring Boot
ticketing-service to call internally.
"""

import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.embeddings.embedder import embed_texts
from app.explainability.combined_explainer import CombinedExplainer
from app.gnn_model.predictor import GNNPredictor

# --- Paths to trained artifacts (produced by the training/ scripts on Days 4-6) ---
# Configurable via env vars so Docker (Day 9) can mount the data volume differently
# than local development does.
DATA_DIR = os.getenv("GRAPHTRIAGE_DATA_DIR", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "data", "generated"))

GNN_MODEL_PATH = os.path.join(DATA_DIR, "gnn_model.pt")
GRAPH_DATASET_PATH = os.path.join(DATA_DIR, "graph_dataset.pt")
FEATURE_EXPLAINER_PATH = os.path.join(DATA_DIR, "feature_explainer.joblib")
SIMILARITY_EXPLAINER_PATH = os.path.join(DATA_DIR, "similarity_explainer.joblib")

ml_resources = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load all trained artifacts ONCE at startup, not per-request - this is the
    # standard FastAPI pattern for expensive-to-load ML models.
    print("Loading GraphTriage ML artifacts...")
    ml_resources["predictor"] = GNNPredictor.load(
        model_path=GNN_MODEL_PATH, graph_dataset_path=GRAPH_DATASET_PATH
    )
    ml_resources["combined_explainer"] = CombinedExplainer.load(
        feature_path=FEATURE_EXPLAINER_PATH, similarity_path=SIMILARITY_EXPLAINER_PATH
    )
    print("GraphTriage ML artifacts loaded successfully.")
    yield
    ml_resources.clear()


app = FastAPI(
    title="GraphTriage Inference Service",
    description="ML/inference layer for GraphTriage — embeddings, GNN predictions, explainability.",
    version="0.2.0",
    lifespan=lifespan,
)


class TicketTextRequest(BaseModel):
    text: str


@app.get("/health")
def health():
    return {
        "service": "inference-service",
        "status": "UP",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "neo4j_uri_configured": os.getenv("NEO4J_URI", "not-configured"),
        "models_loaded": "predictor" in ml_resources,
    }


@app.get("/")
def root():
    return {"message": "GraphTriage inference-service is running. See /health and /docs."}


@app.post("/predict")
def predict(request: TicketTextRequest):
    """Predict root-cause category and resolution time for a new ticket's text."""
    if "predictor" not in ml_resources:
        raise HTTPException(status_code=503, detail="Model not loaded yet.")
    result, _ = ml_resources["predictor"].predict(request.text)
    return result


@app.post("/similar")
def similar(request: TicketTextRequest):
    """Find the top-K most similar past tickets for a new ticket's text."""
    if "combined_explainer" not in ml_resources:
        raise HTTPException(status_code=503, detail="Model not loaded yet.")
    embedding = embed_texts([request.text])[0]
    result = ml_resources["combined_explainer"].similarity_explainer.explain_by_embedding(embedding)
    return result


@app.post("/explain")
def explain(request: TicketTextRequest):
    """Full explanation: predicted category + top contributing keywords + similar past tickets."""
    if "combined_explainer" not in ml_resources:
        raise HTTPException(status_code=503, detail="Model not loaded yet.")
    embedding = embed_texts([request.text])[0]
    result = ml_resources["combined_explainer"].explain(text=request.text, embedding=embedding)
    return result

