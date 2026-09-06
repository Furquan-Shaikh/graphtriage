"""
GraphTriage — Generate Ticket Embeddings (Day 4, Step 1)

Reads all tickets from MySQL (title + description), computes a Sentence-BERT
embedding for each, and saves them to data/generated/embeddings.npz for reuse
by later steps (embedding sanity-check, Day 5 GNN training).

NOTE: The first run downloads the 'all-MiniLM-L6-v2' model from Hugging Face
(a few hundred MB) — this needs normal internet access. Subsequent runs reuse
the local model cache and work fine offline.

Prerequisites:
    pip install -r ../requirements.txt

Usage:
    cd inference-service/training
    python3 generate_embeddings.py
"""

import argparse
import os
import sys

import mysql.connector
import numpy as np
from dotenv import load_dotenv

# Make the app/ package importable from this training script
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.embeddings.embedder import EMBEDDING_DIM, embed_texts  # noqa: E402


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


def fetch_tickets(cursor):
    cursor.execute(
        "SELECT id, title, description, dataset_split FROM ticket ORDER BY id"
    )
    return cursor.fetchall()


def main():
    parser = argparse.ArgumentParser(description="Generate Sentence-BERT embeddings for all tickets")
    parser.add_argument("--mysql-host", type=str, default="localhost")
    parser.add_argument("--mysql-port", type=int, default=3307,
                         help="MySQL host port - defaults to 3307 per the Day 1 port-conflict fix")
    parser.add_argument("--output", type=str, default="../../data/generated/embeddings.npz")
    args = parser.parse_args()

    load_env()

    conn = get_mysql_connection(args)
    cursor = conn.cursor()
    rows = fetch_tickets(cursor)
    cursor.close()
    conn.close()

    print(f"Fetched {len(rows)} tickets from MySQL.")

    ticket_ids = np.array([r[0] for r in rows])
    # Combine title + description into one piece of text per ticket to embed
    texts = [f"{r[1]}. {r[2]}" for r in rows]
    splits = np.array([r[3] for r in rows])

    print(
        "Loading Sentence-BERT model and generating embeddings "
        "(first run downloads the model from Hugging Face - needs internet)..."
    )
    embeddings = embed_texts(texts)
    print(f"Generated embeddings with shape {embeddings.shape} (expected dim: {EMBEDDING_DIM})")

    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), args.output)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    np.savez(output_path, ticket_ids=ticket_ids, embeddings=embeddings, splits=splits)

    print(f"Saved embeddings -> {output_path}")


if __name__ == "__main__":
    main()
