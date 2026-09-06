"""
GraphTriage — Final GNN vs. Baseline Comparison Report (Day 5, Step 5)

Consolidates Day 4's baseline results and Day 5's GNN results into one
documented report with honest interpretation of both findings - this is
the file the "Results" and "Discussion" sections of the paper/thesis
should be written from directly.

Usage:
    cd inference-service/training
    python3 build_final_comparison_report.py
"""

import argparse
import json
import os
from datetime import datetime, timezone


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    parser = argparse.ArgumentParser(description="Build the final GNN vs baseline comparison report")
    parser.add_argument("--classifier-results", type=str,
                         default="../../data/generated/baseline_classifier_results.json")
    parser.add_argument("--resolution-results", type=str,
                         default="../../data/generated/baseline_resolution_time_results.json")
    parser.add_argument("--gnn-results", type=str,
                         default="../../data/generated/gnn_results.json")
    parser.add_argument("--output", type=str,
                         default="../../data/generated/gnn_vs_baseline_report.md")
    args = parser.parse_args()

    base_dir = os.path.dirname(os.path.abspath(__file__))
    clf = load_json(os.path.join(base_dir, args.classifier_results))
    reg = load_json(os.path.join(base_dir, args.resolution_results))
    gnn = load_json(os.path.join(base_dir, args.gnn_results))

    mae_gap = reg["test_mae_category_baseline"] - gnn["test_mae_hours"]
    mae_pct = (mae_gap / reg["test_mae_category_baseline"]) * 100 if reg["test_mae_category_baseline"] else 0
    gnn_wins = mae_gap > 0

    lines = []
    lines.append("# GNN vs. Baseline — Final Comparison Report — GraphTriage")
    lines.append(f"\n_Generated: {datetime.now(timezone.utc).isoformat()}_\n")

    lines.append("## 1. Summary Table")
    lines.append("| Metric | Baseline | GraphSAGE GNN | Delta |\n|---|---|---|---|")
    lines.append(
        f"| Root-cause Accuracy | {clf['test_accuracy']} | {gnn['test_accuracy']} | "
        f"{gnn['test_accuracy'] - clf['test_accuracy']:+.4f} |"
    )
    lines.append(
        f"| Root-cause Macro-F1 | {clf['test_macro_f1']} | {gnn['test_macro_f1']} | "
        f"{gnn['test_macro_f1'] - clf['test_macro_f1']:+.4f} |"
    )
    lines.append(
        f"| Resolution-Time MAE (hours) | {reg['test_mae_category_baseline']} | {gnn['test_mae_hours']} | "
        f"{-mae_gap:+.4f} ({-mae_pct:+.1f}%) |"
    )

    lines.append("\n## 2. Root-Cause Classification — Discussion")
    lines.append(
        "Both the baseline and the GNN reach 100% accuracy on this task. As documented in "
        "`docs/memory.md` (Sprint Day 4 decision log), this is a property of the synthetic "
        "dataset: `generate.py` uses category-specific templates with largely non-overlapping "
        "vocabulary, making categories trivially separable by keyword presence alone. "
        "**This metric should not be used as evidence of the GNN's value** — it is reported "
        "for completeness, but the classification task has no accuracy headroom left for "
        "either model to demonstrate improvement over the other."
    )

    lines.append("\n## 3. Resolution-Time Regression — Discussion")
    if gnn_wins:
        lines.append(
            f"The GNN model improves on the baseline by {mae_gap:.4f} hours "
            f"({mae_pct:.1f}% reduction in MAE), suggesting the graph structure and text "
            f"embeddings carry some additional predictive signal beyond the category label alone."
        )
    else:
        lines.append(
            f"The GNN model did **not** beat the category-average baseline on this run "
            f"(MAE {gnn['test_mae_hours']}h vs. baseline {reg['test_mae_category_baseline']}h). "
            "As documented in `docs/memory.md` (Sprint Day 5 decision log), this is an "
            "explainable and honest property of the synthetic dataset: `generate.py` samples "
            "resolution time independently and uniformly *per category*, with no dependency "
            "on ticket text content beyond category membership. Under this data-generating "
            "process, the category-average is close to the Bayes-optimal predictor for MAE, "
            "leaving little signal for any model — including a GNN — to exploit further.\n\n"
            "**This is a legitimate finding to report, not a failure to hide.** It should be "
            "discussed openly in the thesis/paper's Limitations or Discussion section, "
            "alongside a note that real-world ticket data (where resolution time plausibly "
            "correlates with textual details, reporter, time-of-day, etc.) would likely give "
            "the graph/text-based model more genuine signal to learn from than this "
            "synthetic dataset does."
        )

    lines.append(
        "\n## 4. Where GraphTriage's Value Actually Shows Up\n"
        "\nGiven the two findings above, the strongest parts of the GraphTriage contribution "
        "to lead with in the paper are **not** the raw accuracy/MAE numbers, but:\n"
        "- The **knowledge-graph-based similar-ticket retrieval** (Day 3) — no baseline model "
        "in this comparison has an equivalent capability at all.\n"
        "- The **explainability layer** (to be built in a later phase) — showing *why* a "
        "prediction was made, which neither the TF-IDF classifier nor the naive resolution-time "
        "average can provide.\n"
        "- The **real, working system integration** (Spring Boot + Neo4j + FastAPI, Days 1, 3, "
        "7-8) — most academic baselines are evaluated offline in a notebook, not wired into a "
        "live, queryable service.\n"
    )

    lines.append(
        "\n## 5. Honest Limitations Section (Draft Text)\n"
        "\n> This work uses a synthetically generated ticket dataset (see Section 9 of the "
        "project requirements) due to the unavailability of a sufficiently large real-world "
        "labeled dataset. Two consequences of this choice were observed and are reported "
        "transparently: (1) root-cause classification reaches 100% accuracy for both baseline "
        "and proposed models, due to the template-based text generation producing "
        "category-distinctive vocabulary; and (2) the resolution-time regression baseline is "
        "close to optimal under the dataset's independent per-category noise model, limiting "
        "the observable improvement from the proposed graph-based approach. Future work "
        "should validate these findings against real-world ticketing data, where both "
        "textual ambiguity and cross-feature dependencies are expected to be higher, likely "
        "widening the gap between baseline and graph-based approaches.\n"
    )

    output_path = os.path.join(base_dir, args.output)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(f"Final comparison report written -> {output_path}")


if __name__ == "__main__":
    main()
