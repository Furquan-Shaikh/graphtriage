"""
GraphTriage — Test the Similarity Explainer (Day 6, Step 2 verification)

Usage:
    cd inference-service/training
    python3 test_similarity_explainer.py --mysql-port 3307
"""

import argparse
import os
import sys

import numpy as np
from dotenv import load_dotenv

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.explainability.similarity_explainer import SimilarityExplainer  # noqa: E402
from build_graph_dataset import fetch_labels, get_mysql_connection  # noqa: E402


def load_env():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    load_dotenv(os.path.join(repo_root, ".env"))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mysql-host", type=str, default="localhost")
    parser.add_argument("--mysql-port", type=int, default=3307)
    parser.add_argument("--embeddings", type=str, default="../../data/generated/embeddings.npz")
    parser.add_argument("--save-path", type=str, default="../../data/generated/similarity_explainer.joblib")
    args = parser.parse_args()

    load_env()

    embeddings_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), args.embeddings)
    data = np.load(embeddings_path)
    ticket_ids = data["ticket_ids"]
    embeddings = data["embeddings"]

    conn = get_mysql_connection(args)
    cursor = conn.cursor()
    categories_and_res = fetch_labels(cursor)
    cursor.close()
    conn.close()
    categories = {tid: v[0] for tid, v in categories_and_res.items()}
    resolution_times = {tid: v[1] for tid, v in categories_and_res.items()}

    explainer = SimilarityExplainer(k=5)
    explainer.fit(ticket_ids, embeddings, categories, resolution_times)

    # --- Mode 1: explain an existing ticket ---
    example_id = int(ticket_ids[0])
    result = explainer.explain_by_ticket_id(example_id)
    print(f"=== Mode 1: Explain existing Ticket #{example_id} (category: {result['category']}) ===")
    for neighbor in result["similar_past_tickets"]:
        print(
            f"  -> Ticket #{neighbor['ticket_id']} | category={neighbor['category']} | "
            f"resolution={neighbor['resolution_time_hours']}h | similarity={neighbor['similarity']}"
        )

    # --- Mode 2: explain a "brand new" ticket (simulate with a slightly perturbed embedding) ---
    fake_new_embedding = embeddings[10] + np.random.normal(0, 0.01, embeddings.shape[1])
    result2 = explainer.explain_by_embedding(fake_new_embedding, new_ticket_label="incoming_ticket_demo")
    print("\n=== Mode 2: Explain a brand-new (simulated) incoming ticket ===")
    for neighbor in result2["similar_past_tickets"]:
        print(
            f"  -> Ticket #{neighbor['ticket_id']} | category={neighbor['category']} | "
            f"resolution={neighbor['resolution_time_hours']}h | similarity={neighbor['similarity']}"
        )

    # --- Verify save/load ---
    save_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), args.save_path)
    explainer.save(save_path)
    reloaded = SimilarityExplainer.load(save_path)
    result_reloaded = reloaded.explain_by_ticket_id(example_id)
    assert result_reloaded["similar_past_tickets"] == result["similar_past_tickets"]
    print(f"\nSaved explainer -> {save_path}")
    print("Save/load round-trip verified: neighbors match after reload.")


if __name__ == "__main__":
    main()
