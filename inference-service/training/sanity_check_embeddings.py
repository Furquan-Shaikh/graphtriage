"""
GraphTriage — Embedding Sanity Check (Day 4, Step 2)

Loads the embeddings generated in Step 1 (data/generated/embeddings.npz) and
checks a basic but important assumption: tickets from the SAME root-cause
category should be more similar to each other (in embedding space) than
tickets from DIFFERENT categories. If that's not true, the embeddings aren't
capturing anything meaningful, and everything built on top of them (Day 5
onward) would be on shaky ground.

Usage:
    cd inference-service/training
    python3 sanity_check_embeddings.py --mysql-port 3307
"""

import argparse
import os
import random

import mysql.connector
import numpy as np
from dotenv import load_dotenv


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


def fetch_ticket_categories(cursor):
    """Returns a dict: {ticket_id: root_cause_category}"""
    cursor.execute("SELECT ticket_id, category FROM bug")
    return dict(cursor.fetchall())


def cosine_similarity(a, b):
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def main():
    parser = argparse.ArgumentParser(description="Sanity-check GraphTriage ticket embeddings")
    parser.add_argument("--mysql-host", type=str, default="localhost")
    parser.add_argument("--mysql-port", type=int, default=3307)
    parser.add_argument("--embeddings", type=str, default="../../data/generated/embeddings.npz")
    parser.add_argument("--pairs-per-comparison", type=int, default=2000,
                         help="How many random pairs to sample for each of the within/across comparisons")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    random.seed(args.seed)
    load_env()

    # Load embeddings
    embeddings_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), args.embeddings)
    data = np.load(embeddings_path)
    ticket_ids = data["ticket_ids"]
    embeddings = data["embeddings"]
    print(f"Loaded {len(ticket_ids)} embeddings, dim={embeddings.shape[1]}")

    id_to_index = {tid: i for i, tid in enumerate(ticket_ids)}

    # Fetch categories from MySQL
    conn = get_mysql_connection(args)
    cursor = conn.cursor()
    ticket_to_category = fetch_ticket_categories(cursor)
    cursor.close()
    conn.close()

    # Group ticket indices by category
    category_to_indices = {}
    for tid, category in ticket_to_category.items():
        if tid in id_to_index:
            category_to_indices.setdefault(category, []).append(id_to_index[tid])

    categories = list(category_to_indices.keys())
    print(f"Found {len(categories)} categories across {len(ticket_to_category)} labeled tickets.")

    # --- Within-category similarity ---
    within_sims = []
    for _ in range(args.pairs_per_comparison):
        cat = random.choice(categories)
        indices = category_to_indices[cat]
        if len(indices) < 2:
            continue
        i, j = random.sample(indices, 2)
        within_sims.append(cosine_similarity(embeddings[i], embeddings[j]))

    # --- Across-category similarity ---
    across_sims = []
    for _ in range(args.pairs_per_comparison):
        cat_a, cat_b = random.sample(categories, 2)
        i = random.choice(category_to_indices[cat_a])
        j = random.choice(category_to_indices[cat_b])
        across_sims.append(cosine_similarity(embeddings[i], embeddings[j]))

    within_avg = float(np.mean(within_sims))
    across_avg = float(np.mean(across_sims))

    print("\n=== Embedding Sanity Check ===")
    print(f"Average cosine similarity WITHIN the same category:  {within_avg:.4f}  (n={len(within_sims)} pairs)")
    print(f"Average cosine similarity ACROSS different categories: {across_avg:.4f}  (n={len(across_sims)} pairs)")
    gap = within_avg - across_avg
    print(f"Gap (within - across): {gap:+.4f}")

    if gap > 0.02:
        print("\nPASS: same-category tickets are meaningfully more similar than "
              "different-category tickets. Embeddings appear to capture real signal.")
    else:
        print("\nWARNING: little to no gap detected. Embeddings may not be capturing "
              "category-level semantic differences well - investigate before Day 5.")

    # --- Per-category breakdown (helps spot any one weak category) ---
    print("\n--- Per-category average within-category similarity ---")
    for cat in sorted(categories):
        indices = category_to_indices[cat]
        if len(indices) < 2:
            continue
        sample_pairs = min(200, len(indices) * (len(indices) - 1) // 2)
        sims = []
        for _ in range(sample_pairs):
            i, j = random.sample(indices, 2)
            sims.append(cosine_similarity(embeddings[i], embeddings[j]))
        print(f"  {cat:<28} avg={np.mean(sims):.4f}  (n_tickets={len(indices)})")

    # --- One concrete nearest-neighbor example ---
    print("\n--- Example: nearest neighbor for one random ticket ---")
    example_idx = random.randrange(len(ticket_ids))
    example_id = ticket_ids[example_idx]
    example_cat = ticket_to_category.get(example_id, "unknown")

    sims_to_example = embeddings @ embeddings[example_idx] / (
        np.linalg.norm(embeddings, axis=1) * np.linalg.norm(embeddings[example_idx])
    )
    sims_to_example[example_idx] = -1  # exclude itself
    nearest_idx = int(np.argmax(sims_to_example))
    nearest_id = ticket_ids[nearest_idx]
    nearest_cat = ticket_to_category.get(nearest_id, "unknown")

    print(f"  Ticket #{example_id} (category: {example_cat})")
    print(f"  -> Nearest neighbor: Ticket #{nearest_id} (category: {nearest_cat}), "
          f"similarity={sims_to_example[nearest_idx]:.4f}")
    print(f"  Same category? {'YES' if example_cat == nearest_cat else 'NO'}")


if __name__ == "__main__":
    main()
