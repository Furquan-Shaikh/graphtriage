"""
GraphTriage — Document Explainability Samples (Day 6, Step 5)

Runs the same explanation generation as review_explanations.py, but writes
a formatted Markdown report instead of just printing to the terminal.
This becomes:
  - Reference material for building the dashboard (Day 8)
  - Ready-to-use example figures/tables for the paper's evaluation section

Usage:
    cd inference-service/training
    python3 build_explainability_samples_doc.py --mysql-port 3307 --n 8
"""

import argparse
import os
import random
import sys
from datetime import datetime, timezone

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
    parser.add_argument("--n", type=int, default=8)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--feature-explainer", type=str,
                         default="../../data/generated/feature_explainer.joblib")
    parser.add_argument("--similarity-explainer", type=str,
                         default="../../data/generated/similarity_explainer.joblib")
    parser.add_argument("--output", type=str,
                         default="../../data/generated/explainability_samples.md")
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

    lines = []
    lines.append("# Explainability Samples — GraphTriage")
    lines.append(f"\n_Generated: {datetime.now(timezone.utc).isoformat()}_\n")
    lines.append(
        "Each example below shows the two explanation mechanisms working together: "
        "SHAP-based keyword contributions (which words drove the prediction) and "
        "graph-based similar-ticket retrieval (which past tickets support it). "
        "See `docs/design.md` Section 11 and `docs/memory.md` Sprint Day 6 for the "
        "design rationale.\n"
    )

    correct = 0
    for ticket_id, title, description, true_category in sample_tickets:
        text = f"{title}. {description}"
        result = explainer.explain(text=text, ticket_id=ticket_id)
        predicted = result["predicted_category"]
        correct += int(predicted == true_category)
        match_label = "✅ Match" if predicted == true_category else "❌ Mismatch"

        lines.append(f"## Ticket #{ticket_id}")
        lines.append(f"**Text:** {text}\n")
        lines.append(f"**True category:** `{true_category}` | **Predicted:** `{predicted}` | {match_label}")
        lines.append(f"**Confidence:** {result['confidence']}\n")
        lines.append("**Top contributing keywords:**")
        for feat in result["top_contributing_features"]:
            lines.append(f"- {feat}")
        lines.append("\n**Similar past tickets:**")
        lines.append("| Ticket ID | Category | Resolution Time (h) | Similarity |")
        lines.append("|---|---|---|---|")
        for n in result["top_similar_past_tickets"]:
            lines.append(
                f"| #{n['ticket_id']} | {n['category']} | {n['resolution_time_hours']} | {n['similarity']} |"
            )
        lines.append("\n---\n")

    lines.append(f"## Summary\n")
    lines.append(f"- Sample size: {len(sample_tickets)}")
    lines.append(f"- Prediction accuracy on this sample: {correct}/{len(sample_tickets)}")
    lines.append(
        "\nThese examples can be used directly as figures/tables in the thesis's "
        "qualitative evaluation section, and as reference content when building the "
        "Day 8 dashboard's explanation panel."
    )

    output_path = os.path.join(base_dir, args.output)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(f"Wrote {len(sample_tickets)} explanation samples -> {output_path}")


if __name__ == "__main__":
    main()
