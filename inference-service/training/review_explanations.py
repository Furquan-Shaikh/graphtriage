"""
GraphTriage — Qualitative Review of Explanations (Day 6, Step 4)

Generates combined explanations for a sample of test-set tickets and:
  1. Prints them for manual/qualitative review.
  2. Computes a simple automated sanity metric: what fraction of each
     ticket's "top similar past tickets" share its predicted category —
     a rough proxy for "these explanations look sensible", complementing
     (not replacing) actually reading them.

Usage:
    cd inference-service/training
    python3 review_explanations.py --mysql-port 3307 --n 15
"""

import argparse
import os
import random
import sys

from dotenv import load_dotenv

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.explainability.combined_explainer import CombinedExplainer  # noqa: E402
from train_baseline_classifier import get_mysql_connection  # noqa: E402


def load_env():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    load_dotenv(os.path.join(repo_root, ".env"))


def fetch_test_tickets(cursor, n, seed):
    cursor.execute(
        """
        SELECT t.id, t.title, t.description, b.category
        FROM ticket t
        JOIN bug b ON b.ticket_id = t.id
        WHERE t.dataset_split = 'test'
        """
    )
    rows = cursor.fetchall()
    random.seed(seed)
    return random.sample(rows, min(n, len(rows)))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mysql-host", type=str, default="localhost")
    parser.add_argument("--mysql-port", type=int, default=3307)
    parser.add_argument("--n", type=int, default=15)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--feature-explainer", type=str,
                         default="../../data/generated/feature_explainer.joblib")
    parser.add_argument("--similarity-explainer", type=str,
                         default="../../data/generated/similarity_explainer.joblib")
    args = parser.parse_args()

    load_env()

    conn = get_mysql_connection(args)
    cursor = conn.cursor()
    sample_tickets = fetch_test_tickets(cursor, args.n, args.seed)
    cursor.close()
    conn.close()

    base_dir = os.path.dirname(os.path.abspath(__file__))
    explainer = CombinedExplainer.load(
        feature_path=os.path.join(base_dir, args.feature_explainer),
        similarity_path=os.path.join(base_dir, args.similarity_explainer),
    )

    correct_prediction_count = 0
    same_category_neighbor_fractions = []

    print(f"Reviewing {len(sample_tickets)} random test-set tickets:\n")

    for ticket_id, title, description, true_category in sample_tickets:
        text = f"{title}. {description}"
        result = explainer.explain(text=text, ticket_id=ticket_id)

        predicted = result["predicted_category"]
        neighbors = result["top_similar_past_tickets"]
        same_cat_count = sum(1 for n in neighbors if n["category"] == predicted)
        same_cat_fraction = same_cat_count / len(neighbors) if neighbors else 0

        correct_prediction_count += int(predicted == true_category)
        same_category_neighbor_fractions.append(same_cat_fraction)

        print(f"--- Ticket #{ticket_id} ---")
        print(f"Text: {text[:90]}...")
        print(f"True category: {true_category}  |  Predicted: {predicted}  "
              f"|  {'MATCH' if predicted == true_category else 'MISMATCH'}")
        print(f"Confidence: {result['confidence']}")
        print(f"Top features: {', '.join(result['top_contributing_features'][:3])}")
        print(f"Neighbor category agreement: {same_cat_count}/{len(neighbors)}")
        print()

    n = len(sample_tickets)
    avg_agreement = sum(same_category_neighbor_fractions) / n if n else 0

    print("=== Summary ===")
    print(f"Prediction accuracy on this sample: {correct_prediction_count}/{n}")
    print(f"Average neighbor-category agreement: {avg_agreement:.2%}")
    print(
        "\nInterpretation: high neighbor-category agreement means the graph-based "
        "explanation is internally consistent with the classifier's own prediction — "
        "a good sign the two explanation mechanisms (SHAP + similarity) are telling a "
        "coherent story, not contradicting each other."
    )


if __name__ == "__main__":
    main()
