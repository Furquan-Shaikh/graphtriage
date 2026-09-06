"""
GraphTriage — Baseline Resolution-Time Estimator (Day 4, Step 4)

Simplest possible baseline for resolution-time prediction: for each
root-cause category, compute the average resolution time from the TRAIN
split only, then predict that category's average for every ticket in
val/test. This is the "naive baseline" that Day 5's GNN regression head
must beat (per docs/prd.md Section 10 / docs/phases.md Phase 4).

Unlike the classification baseline (Step 3, which hit 100% due to
template-distinctive text - see docs/memory.md decision log), resolution
times have continuous random noise per ticket even within a category
(see generate.py), so this baseline will have real, non-zero error - a
meaningful target for the GNN to improve on.

Usage:
    cd inference-service/training
    python3 train_baseline_resolution_time.py --mysql-port 3307
"""

import argparse
import json
import os
from collections import defaultdict

import mysql.connector
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


def fetch_split(cursor, split_name):
    """Returns list of (category, resolution_time_hours) for the given split."""
    cursor.execute(
        """
        SELECT b.category, f.resolution_time_hours
        FROM ticket t
        JOIN bug b ON b.ticket_id = t.id
        JOIN fix f ON f.bug_id = b.id
        WHERE t.dataset_split = %s
        """,
        (split_name,),
    )
    return cursor.fetchall()


def mae(y_true, y_pred):
    return sum(abs(a - b) for a, b in zip(y_true, y_pred)) / len(y_true)


def main():
    parser = argparse.ArgumentParser(description="Train naive category-average resolution-time baseline")
    parser.add_argument("--mysql-host", type=str, default="localhost")
    parser.add_argument("--mysql-port", type=int, default=3307)
    parser.add_argument("--output", type=str, default="../../data/generated/baseline_resolution_time_results.json")
    args = parser.parse_args()

    load_env()
    conn = get_mysql_connection(args)
    cursor = conn.cursor()

    train_rows = fetch_split(cursor, "train")
    val_rows = fetch_split(cursor, "val")
    test_rows = fetch_split(cursor, "test")

    cursor.close()
    conn.close()

    print(f"Train: {len(train_rows)}  Val: {len(val_rows)}  Test: {len(test_rows)}")

    # --- Category-average baseline (fit on TRAIN only) ---
    category_totals = defaultdict(list)
    for category, hours in train_rows:
        category_totals[category].append(hours)
    category_avg = {cat: sum(vals) / len(vals) for cat, vals in category_totals.items()}

    # Global average, as an even more naive reference point
    global_avg = sum(h for _, h in train_rows) / len(train_rows)

    def evaluate(rows, label):
        y_true = [h for _, h in rows]
        y_pred_category = [category_avg.get(cat, global_avg) for cat, _ in rows]
        y_pred_global = [global_avg for _ in rows]

        mae_category = mae(y_true, y_pred_category)
        mae_global = mae(y_true, y_pred_global)

        print(f"\n{label} set (n={len(rows)}):")
        print(f"  Category-average baseline MAE: {mae_category:.3f} hours")
        print(f"  Global-average baseline MAE:   {mae_global:.3f} hours  (naive reference point)")

        return mae_category, mae_global

    val_mae_cat, val_mae_global = evaluate(val_rows, "Validation")
    test_mae_cat, test_mae_global = evaluate(test_rows, "Test")

    print("\n--- Per-category average resolution time (from TRAIN) ---")
    for cat in sorted(category_avg):
        print(f"  {cat:<28} avg={category_avg[cat]:.2f}h  (n={len(category_totals[cat])})")

    results = {
        "model": "Category-average baseline (resolution time)",
        "train_size": len(train_rows),
        "val_size": len(val_rows),
        "test_size": len(test_rows),
        "val_mae_category_baseline": round(val_mae_cat, 3),
        "val_mae_global_baseline": round(val_mae_global, 3),
        "test_mae_category_baseline": round(test_mae_cat, 3),
        "test_mae_global_baseline": round(test_mae_global, 3),
        "category_averages_hours": {k: round(v, 3) for k, v in category_avg.items()},
    }

    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), args.output)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"\nSaved results -> {output_path}")
    print("\nThis MAE is the number Day 5's GNN regression head needs to beat.")


if __name__ == "__main__":
    main()
