"""
GraphTriage — Graph Dataset Builder for GNN Training (Day 5, Step 1)

Builds a PyTorch Geometric `Data` object for GNN training:
  - Node features (x): the Sentence-BERT embeddings from Day 4
    (data/generated/embeddings.npz)
  - Graph structure (edge_index): k-nearest-neighbor edges computed from
    embedding cosine similarity — this is the practical, lightweight-sprint
    implementation of the SIMILAR_TO relationship described in
    docs/design.md Section 2. (A fuller version would also persist these as
    SIMILAR_TO edges in Neo4j itself; deferred here to keep Day 5 scoped —
    see docs/memory.md decision log.)
  - Labels: root_cause_category (for classification) and
    resolution_time_hours (for regression), fetched from MySQL
  - Masks: train/val/test, taken directly from the dataset_split column
    set back on Day 2

Usage:
    cd inference-service/training
    python3 build_graph_dataset.py --mysql-port 3307
"""

import argparse
import os

import mysql.connector
import numpy as np
import torch
from dotenv import load_dotenv
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import LabelEncoder


def load_env():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    load_dotenv(os.path.join(repo_root, ".env"))


def get_mysql_connection(args):
    return mysql.connector.connect(
        host=args.mysql_host,
        port=args.mysql_port,
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE"),
    )


def fetch_labels(cursor):
    """Returns {ticket_id: (category, resolution_time_hours)}"""
    cursor.execute(
        """
        SELECT t.id, b.category, f.resolution_time_hours
        FROM ticket t
        JOIN bug b ON b.ticket_id = t.id
        JOIN fix f ON f.bug_id = b.id
        """
    )
    return {row[0]: (row[1], row[2]) for row in cursor.fetchall()}


def build_knn_edge_index(embeddings, k=5):
    """Connect each ticket to its k most similar OTHER tickets (cosine similarity).
    Returns a (2, num_edges) array, made symmetric (undirected) for GraphSAGE."""
    nn = NearestNeighbors(n_neighbors=k + 1, metric="cosine").fit(embeddings)
    _, indices = nn.kneighbors(embeddings)

    edges = set()
    for i, neighbors in enumerate(indices):
        for j in neighbors:
            if j != i:
                edges.add((i, j))
                edges.add((j, i))  # make undirected

    edge_index = np.array(list(edges)).T  # shape (2, num_edges)
    return edge_index


def main():
    parser = argparse.ArgumentParser(description="Build PyTorch Geometric graph dataset for GNN training")
    parser.add_argument("--mysql-host", type=str, default="localhost")
    parser.add_argument("--mysql-port", type=int, default=3307)
    parser.add_argument("--embeddings", type=str, default="../../data/generated/embeddings.npz")
    parser.add_argument("--output", type=str, default="../../data/generated/graph_dataset.pt")
    parser.add_argument("--k", type=int, default=5, help="Number of nearest neighbors per ticket")
    args = parser.parse_args()

    load_env()

    # --- Load embeddings (Day 4 output) ---
    embeddings_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), args.embeddings)
    data = np.load(embeddings_path)
    ticket_ids = data["ticket_ids"]
    embeddings = data["embeddings"].astype(np.float32)
    splits = data["splits"]
    print(f"Loaded {len(ticket_ids)} ticket embeddings, dim={embeddings.shape[1]}")

    # --- Fetch labels from MySQL, aligned to embeddings order ---
    conn = get_mysql_connection(args)
    cursor = conn.cursor()
    labels = fetch_labels(cursor)
    cursor.close()
    conn.close()

    categories = [labels[tid][0] for tid in ticket_ids]
    resolution_hours = np.array([labels[tid][1] for tid in ticket_ids], dtype=np.float32)

    label_encoder = LabelEncoder()
    category_ids = label_encoder.fit_transform(categories)
    print(f"Encoded {len(label_encoder.classes_)} root-cause categories: {list(label_encoder.classes_)}")

    # --- Build k-NN similarity edges ---
    print(f"Building k-NN graph edges (k={args.k})...")
    edge_index = build_knn_edge_index(embeddings, k=args.k)
    print(f"Graph has {edge_index.shape[1]} directed edges (undirected pairs, so /2 unique links)")

    # --- Build train/val/test masks from the dataset_split column ---
    train_mask = splits == "train"
    val_mask = splits == "val"
    test_mask = splits == "test"
    print(f"Split sizes -> train: {train_mask.sum()}  val: {val_mask.sum()}  test: {test_mask.sum()}")

    # --- Package everything for Step 2 (model) / Step 3 (training) ---
    graph_data = {
        "x": torch.tensor(embeddings, dtype=torch.float),
        "edge_index": torch.tensor(edge_index, dtype=torch.long),
        "y_category": torch.tensor(category_ids, dtype=torch.long),
        "y_resolution": torch.tensor(resolution_hours, dtype=torch.float),
        "train_mask": torch.tensor(train_mask, dtype=torch.bool),
        "val_mask": torch.tensor(val_mask, dtype=torch.bool),
        "test_mask": torch.tensor(test_mask, dtype=torch.bool),
        "ticket_ids": torch.tensor(ticket_ids, dtype=torch.long),
        "category_classes": list(label_encoder.classes_),
    }

    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), args.output)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    torch.save(graph_data, output_path)
    print(f"\nSaved graph dataset -> {output_path}")


if __name__ == "__main__":
    main()
