"""
GraphTriage — Test the Combined Explainer (Day 6, Step 3 verification)

Loads the saved feature + similarity explainers, fetches a real ticket's
text from MySQL, and prints the full combined explanation.

Usage:
    cd inference-service/training
    python3 test_combined_explainer.py --mysql-port 3307 --ticket-id 1
"""

import argparse
import json
import os
import sys

from dotenv import load_dotenv

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.explainability.combined_explainer import CombinedExplainer  # noqa: E402
from train_baseline_classifier import get_mysql_connection  # noqa: E402


def load_env():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    load_dotenv(os.path.join(repo_root, ".env"))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mysql-host", type=str, default="localhost")
    parser.add_argument("--mysql-port", type=int, default=3307)
    parser.add_argument("--ticket-id", type=int, default=1)
    parser.add_argument("--feature-explainer", type=str,
                         default="../../data/generated/feature_explainer.joblib")
    parser.add_argument("--similarity-explainer", type=str,
                         default="../../data/generated/similarity_explainer.joblib")
    args = parser.parse_args()

    load_env()

    conn = get_mysql_connection(args)
    cursor = conn.cursor()
    cursor.execute("SELECT title, description FROM ticket WHERE id = %s", (args.ticket_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()

    if row is None:
        raise SystemExit(f"No ticket found with id={args.ticket_id}")

    title, description = row
    real_text = f"{title}. {description}"
    print(f"Ticket #{args.ticket_id} text: {real_text[:100]}...\n")

    base_dir = os.path.dirname(os.path.abspath(__file__))
    explainer = CombinedExplainer.load(
        feature_path=os.path.join(base_dir, args.feature_explainer),
        similarity_path=os.path.join(base_dir, args.similarity_explainer),
    )

    result = explainer.explain(text=real_text, ticket_id=args.ticket_id)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
