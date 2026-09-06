"""
GraphTriage — GNN Training Loop (Day 5, Step 3)

Trains the GraphSAGE model (app/gnn_model/model.py) on the graph dataset
built in Step 1, using a combined multi-task loss:
  - Classification loss (CrossEntropy) for root-cause category
  - Regression loss (L1/MAE) for resolution time — matches the baseline's
    evaluation metric directly, so training objective and evaluation
    metric are aligned

Since the graph is small (~1200 nodes), this uses full-batch training
(the whole graph fits in memory/one forward pass each epoch) rather than
mini-batch neighbor sampling — appropriate for this dataset size.

Usage:
    cd inference-service/training
    python3 train_gnn.py
"""

import argparse
import json
import os
import sys

import torch
import torch.nn as nn
from sklearn.metrics import accuracy_score, f1_score

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.gnn_model.model import GraphTriageGNN  # noqa: E402


def load_baseline_results(base_dir):
    """Load Day 4 baseline numbers for a side-by-side comparison at the end."""
    results = {}
    for name, path in [
        ("classifier", "../../data/generated/baseline_classifier_results.json"),
        ("resolution", "../../data/generated/baseline_resolution_time_results.json"),
    ]:
        full_path = os.path.join(base_dir, path)
        if os.path.exists(full_path):
            with open(full_path, "r", encoding="utf-8") as f:
                results[name] = json.load(f)
    return results


def evaluate(model, data, mask):
    model.eval()
    with torch.no_grad():
        category_logits, resolution_pred = model(data["x"], data["edge_index"])

        preds = category_logits[mask].argmax(dim=1)
        y_true_cat = data["y_category"][mask]
        acc = accuracy_score(y_true_cat.numpy(), preds.numpy())
        f1 = f1_score(y_true_cat.numpy(), preds.numpy(), average="macro")

        y_pred_res = resolution_pred[mask]
        y_true_res = data["y_resolution"][mask]
        mae = torch.mean(torch.abs(y_pred_res - y_true_res)).item()

    return acc, f1, mae


def main():
    parser = argparse.ArgumentParser(description="Train the GraphTriage GNN model")
    parser.add_argument("--graph-data", type=str, default="../../data/generated/graph_dataset.pt")
    parser.add_argument("--hidden-channels", type=int, default=64)
    parser.add_argument("--epochs", type=int, default=200)
    parser.add_argument("--lr", type=float, default=0.01)
    parser.add_argument("--regression-weight", type=float, default=1.0,
                         help="Weight of the regression loss relative to classification loss")
    parser.add_argument("--patience", type=int, default=30,
                         help="Early stopping patience (epochs without val improvement)")
    parser.add_argument("--output-model", type=str, default="../../data/generated/gnn_model.pt")
    parser.add_argument("--output-results", type=str, default="../../data/generated/gnn_results.json")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    torch.manual_seed(args.seed)

    base_dir = os.path.dirname(os.path.abspath(__file__))
    graph_path = os.path.join(base_dir, args.graph_data)
    data = torch.load(graph_path, weights_only=False)

    print(f"Loaded graph: {data['x'].shape[0]} nodes, {data['edge_index'].shape[1]} directed edges")
    print(f"Train/Val/Test: {data['train_mask'].sum()}/{data['val_mask'].sum()}/{data['test_mask'].sum()}")

    num_categories = len(data["category_classes"])
    model = GraphTriageGNN(
        in_channels=data["x"].shape[1],
        hidden_channels=args.hidden_channels,
        num_categories=num_categories,
    )

    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)
    classification_loss_fn = nn.CrossEntropyLoss()
    regression_loss_fn = nn.L1Loss()  # L1 = MAE, matches the baseline's evaluation metric

    best_val_mae = float("inf")
    best_state = None
    epochs_without_improvement = 0

    print("\nTraining...")
    for epoch in range(1, args.epochs + 1):
        model.train()
        optimizer.zero_grad()

        category_logits, resolution_pred = model(data["x"], data["edge_index"])

        train_mask = data["train_mask"]
        cls_loss = classification_loss_fn(category_logits[train_mask], data["y_category"][train_mask])
        reg_loss = regression_loss_fn(resolution_pred[train_mask], data["y_resolution"][train_mask])
        loss = cls_loss + args.regression_weight * reg_loss

        loss.backward()
        optimizer.step()

        if epoch % 10 == 0 or epoch == 1:
            val_acc, val_f1, val_mae = evaluate(model, data, data["val_mask"])
            print(
                f"Epoch {epoch:3d} | train_loss={loss.item():.4f} "
                f"(cls={cls_loss.item():.4f}, reg={reg_loss.item():.4f}) | "
                f"val_acc={val_acc:.4f} val_f1={val_f1:.4f} val_mae={val_mae:.4f}"
            )

            if val_mae < best_val_mae:
                best_val_mae = val_mae
                best_state = {k: v.clone() for k, v in model.state_dict().items()}
                epochs_without_improvement = 0
            else:
                epochs_without_improvement += 10

            if epochs_without_improvement >= args.patience:
                print(f"Early stopping at epoch {epoch} (no val_mae improvement for {args.patience} epochs)")
                break

    # Restore best checkpoint (by validation MAE) before final test evaluation
    if best_state is not None:
        model.load_state_dict(best_state)

    test_acc, test_f1, test_mae = evaluate(model, data, data["test_mask"])
    print(f"\n=== Final Test Results ===")
    print(f"Test Accuracy: {test_acc:.4f}  |  Test Macro-F1: {test_f1:.4f}  |  Test MAE: {test_mae:.4f} hours")

    # --- Compare against Day 4 baselines ---
    baselines = load_baseline_results(base_dir)
    print("\n=== Comparison vs. Day 4 Baselines ===")
    if "classifier" in baselines:
        b = baselines["classifier"]
        print(f"Classification — Baseline: {b['test_accuracy']:.4f} acc | GNN: {test_acc:.4f} acc")
    if "resolution" in baselines:
        b = baselines["resolution"]
        baseline_mae = b["test_mae_category_baseline"]
        improvement = baseline_mae - test_mae
        pct = (improvement / baseline_mae) * 100 if baseline_mae else 0
        print(
            f"Resolution Time — Baseline MAE: {baseline_mae}h | GNN MAE: {test_mae:.4f}h | "
            f"Improvement: {improvement:+.4f}h ({pct:+.1f}%)"
        )

    # --- Save model + results ---
    model_output_path = os.path.join(base_dir, args.output_model)
    torch.save(
        {"model_state_dict": model.state_dict(), "category_classes": data["category_classes"]},
        model_output_path,
    )
    print(f"\nSaved trained model -> {model_output_path}")

    results = {
        "model": "GraphSAGE GNN (multi-task)",
        "hidden_channels": args.hidden_channels,
        "epochs_run": epoch,
        "test_accuracy": round(test_acc, 4),
        "test_macro_f1": round(test_f1, 4),
        "test_mae_hours": round(test_mae, 4),
    }
    results_output_path = os.path.join(base_dir, args.output_results)
    with open(results_output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"Saved results -> {results_output_path}")


if __name__ == "__main__":
    main()
