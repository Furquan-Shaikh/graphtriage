"""
GraphTriage — Baseline Classifier: TF-IDF + Logistic Regression (Day 4, Step 3)

Trains a baseline root-cause-category classifier using TF-IDF text features
+ Logistic Regression. This is the comparison point Day 5's GNN model must
beat - a paper without a baseline comparison is very hard to publish
(see docs/prd.md Section 10 and docs/phases.md Phase 4).

Usage:
    cd inference-service/training
    python3 train_baseline_classifier.py --mysql-port 3307
"""

import argparse
import json
import os

import mysql.connector
from dotenv import load_dotenv
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, f1_score


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
    cursor.execute(
        """
        SELECT t.title, t.description, b.category
        FROM ticket t
        JOIN bug b ON b.ticket_id = t.id
        WHERE t.dataset_split = %s
        """,
        (split_name,),
    )
    rows = cursor.fetchall()
    texts = [f"{title}. {description}" for title, description, _ in rows]
    labels = [category for _, _, category in rows]
    return texts, labels


def main():
    parser = argparse.ArgumentParser(description="Train TF-IDF + Logistic Regression baseline")
    parser.add_argument("--mysql-host", type=str, default="localhost")
    parser.add_argument("--mysql-port", type=int, default=3307)
    parser.add_argument("--output", type=str, default="../../data/generated/baseline_classifier_results.json")
    args = parser.parse_args()

    load_env()
    conn = get_mysql_connection(args)
    cursor = conn.cursor()

    train_texts, train_labels = fetch_split(cursor, "train")
    val_texts, val_labels = fetch_split(cursor, "val")
    test_texts, test_labels = fetch_split(cursor, "test")

    cursor.close()
    conn.close()

    print(f"Train: {len(train_texts)}  Val: {len(val_texts)}  Test: {len(test_texts)}")

    # Fit TF-IDF ONLY on train (never let val/test leak into vocabulary fitting)
    vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2), stop_words="english")
    X_train = vectorizer.fit_transform(train_texts)
    X_val = vectorizer.transform(val_texts)
    X_test = vectorizer.transform(test_texts)

    clf = LogisticRegression(max_iter=1000, random_state=42)
    clf.fit(X_train, train_labels)

    val_preds = clf.predict(X_val)
    test_preds = clf.predict(X_test)

    val_acc = accuracy_score(val_labels, val_preds)
    val_f1 = f1_score(val_labels, val_preds, average="macro")
    test_acc = accuracy_score(test_labels, test_preds)
    test_f1 = f1_score(test_labels, test_preds, average="macro")

    print(f"\nValidation — Accuracy: {val_acc:.4f}  Macro-F1: {val_f1:.4f}")
    print(f"Test       — Accuracy: {test_acc:.4f}  Macro-F1: {test_f1:.4f}")

    print("\nTest set classification report:")
    report_text = classification_report(test_labels, test_preds)
    print(report_text)

    results = {
        "model": "TF-IDF + Logistic Regression (baseline)",
        "train_size": len(train_texts),
        "val_size": len(val_texts),
        "test_size": len(test_texts),
        "val_accuracy": round(val_acc, 4),
        "val_macro_f1": round(val_f1, 4),
        "test_accuracy": round(test_acc, 4),
        "test_macro_f1": round(test_f1, 4),
    }

    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), args.output)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"\nSaved results -> {output_path}")


if __name__ == "__main__":
    main()
