"""
GraphTriage — Test the SHAP Feature Explainer (Day 6, Step 1 verification)

Fits the FeatureExplainer on the training split, explains a few sample
tickets, and verifies save/load works correctly.

Usage:
    cd inference-service/training
    python3 test_feature_explainer.py --mysql-port 3307
"""

import argparse
import os
import sys

from dotenv import load_dotenv

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.explainability.feature_explainer import FeatureExplainer  # noqa: E402
from train_baseline_classifier import fetch_split, get_mysql_connection  # noqa: E402


def load_env():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    load_dotenv(os.path.join(repo_root, ".env"))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mysql-host", type=str, default="localhost")
    parser.add_argument("--mysql-port", type=int, default=3307)
    parser.add_argument("--save-path", type=str, default="../../data/generated/feature_explainer.joblib")
    args = parser.parse_args()

    load_env()
    conn = get_mysql_connection(args)
    cursor = conn.cursor()
    train_texts, train_labels = fetch_split(cursor, "train")
    test_texts, test_labels = fetch_split(cursor, "test")
    cursor.close()
    conn.close()

    print(f"Fitting explainer on {len(train_texts)} training tickets...")
    explainer = FeatureExplainer(top_k=5)
    explainer.fit(train_texts, train_labels)

    print("\n=== Explaining 3 sample test tickets ===")
    for i in range(3):
        result = explainer.explain(test_texts[i])
        print(f"\nTicket text: {test_texts[i][:80]}...")
        print(f"True category: {test_labels[i]}")
        print(f"Predicted category: {result['predicted_category']}")
        print("Top contributing features:")
        for feat in result["top_contributing_features"]:
            print(f"  {feat['feature']:<20} contribution={feat['contribution']:+.4f}")

    # --- Verify save/load round-trip ---
    save_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), args.save_path)
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    explainer.save(save_path)
    print(f"\nSaved explainer -> {save_path}")

    reloaded = FeatureExplainer.load(save_path)
    result_before = explainer.explain(test_texts[0])
    result_after = reloaded.explain(test_texts[0])
    assert result_before["predicted_category"] == result_after["predicted_category"]
    print("Save/load round-trip verified: predictions match after reload.")


if __name__ == "__main__":
    main()
