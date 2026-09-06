"""
GraphTriage — Consolidate Baseline Results into a Report (Day 4, Step 5)

Reads the JSON outputs from Step 3 (train_baseline_classifier.py) and
Step 4 (train_baseline_resolution_time.py) and writes a single documented
Markdown report - data/generated/baseline_report.md - that Day 5's GNN
results get compared against, and that plugs directly into the paper's
evaluation section.

Usage:
    cd inference-service/training
    python3 build_baseline_report.py
"""

import argparse
import json
import os
from datetime import datetime, timezone


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    parser = argparse.ArgumentParser(description="Consolidate baseline results into a report")
    parser.add_argument("--classifier-results", type=str,
                         default="../../data/generated/baseline_classifier_results.json")
    parser.add_argument("--resolution-results", type=str,
                         default="../../data/generated/baseline_resolution_time_results.json")
    parser.add_argument("--output", type=str, default="../../data/generated/baseline_report.md")
    args = parser.parse_args()

    base_dir = os.path.dirname(os.path.abspath(__file__))
    clf = load_json(os.path.join(base_dir, args.classifier_results))
    reg = load_json(os.path.join(base_dir, args.resolution_results))

    lines = []
    lines.append("# Baseline Model Report — GraphTriage")
    lines.append(f"\n_Generated: {datetime.now(timezone.utc).isoformat()}_\n")
    lines.append(
        "These are the baseline results that Day 5's Graph Neural Network model "
        "must be compared against. Per `docs/prd.md` Section 10 and `docs/phases.md` "
        "Phase 4, a paper without a documented baseline comparison is very hard to "
        "publish — this file is that documentation.\n"
    )

    lines.append("## 1. Root-Cause Classification Baseline")
    lines.append(f"**Model:** {clf['model']}\n")
    lines.append(f"- Train / Val / Test sizes: {clf['train_size']} / {clf['val_size']} / {clf['test_size']}")
    lines.append(f"- Validation Accuracy: **{clf['val_accuracy']}** | Macro-F1: **{clf['val_macro_f1']}**")
    lines.append(f"- Test Accuracy: **{clf['test_accuracy']}** | Macro-F1: **{clf['test_macro_f1']}**\n")
    lines.append(
        "**Important caveat (must be stated in the paper's Limitations section):** "
        "This baseline reaches 100% accuracy because the synthetic dataset's ticket "
        "text is generated from category-specific templates with largely "
        "non-overlapping vocabulary (see `docs/memory.md` decision log, Sprint Day 4). "
        "This means root-cause classification accuracy is **not** a meaningful axis "
        "for comparing the GNN model against this baseline — there is no headroom "
        "left. The GNN's contribution should instead be demonstrated via the "
        "resolution-time regression task (Section 2 below) and the knowledge-graph "
        "explainability/similarity-retrieval capabilities, which this baseline has "
        "no equivalent for at all.\n"
    )

    lines.append("## 2. Resolution-Time Regression Baseline")
    lines.append(f"**Model:** {reg['model']}\n")
    lines.append(f"- Train / Val / Test sizes: {reg['train_size']} / {reg['val_size']} / {reg['test_size']}")
    lines.append(
        f"- Validation MAE — category-average: **{reg['val_mae_category_baseline']}h** "
        f"| global-average: {reg['val_mae_global_baseline']}h"
    )
    lines.append(
        f"- Test MAE — category-average: **{reg['test_mae_category_baseline']}h** "
        f"| global-average: {reg['test_mae_global_baseline']}h\n"
    )
    lines.append(
        "**This is the primary number Day 5's GNN regression head needs to beat.** "
        "Unlike classification, resolution times carry continuous random noise per "
        "ticket even within a category (see `generate.py`), so this baseline has "
        "genuine, non-zero error and real headroom for improvement.\n"
    )

    lines.append("### Per-Category Average Resolution Time (from Train Split)")
    lines.append("| Category | Avg Resolution Time (h) |\n|---|---|")
    for cat, avg in sorted(reg["category_averages_hours"].items()):
        lines.append(f"| {cat} | {avg} |")

    lines.append(
        "\n## 3. What Day 5 Needs to Report\n"
        "\nFor a credible comparison in the paper/thesis, the Day 5 GNN evaluation "
        "should report, side-by-side with the numbers above:\n"
        "- Root-cause prediction accuracy/F1 (expected to also be very high, given "
        "the dataset caveat above — report it, but do not lean on it as the novelty "
        "claim)\n"
        "- Resolution-time MAE on the same test split (**this is the headline "
        "comparison number**)\n"
        "- Qualitative examples of graph-based explanations that the baseline "
        "models have no equivalent of at all\n"
    )

    output_path = os.path.join(base_dir, args.output)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(f"Baseline report written -> {output_path}")


if __name__ == "__main__":
    main()
