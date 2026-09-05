"""
GraphTriage — Train/Validation/Test Split (Day 2, Step 3)

Reads data/generated/tickets_raw.csv (produced by generate.py) and splits it
into three files:
  - tickets_train.csv (70%) - used to train models (Day 4-5)
  - tickets_val.csv   (15%) - used to tune hyperparameters / early stopping
  - tickets_test.csv  (15%) - held out, only used for final evaluation (Day 9)

The split is shuffled but reproducible (same --seed = same split every time),
and is stratified by root_cause_category so that rare categories still appear
in all three splits in roughly the same proportion as the full dataset —
otherwise a category with few examples could end up entirely in one split.

Usage:
    cd data/generator
    python3 split_dataset.py --input ../generated/tickets_raw.csv --seed 42
"""

import argparse
import csv
import os
import random
from collections import defaultdict


def read_tickets(path):
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)
    return fieldnames, rows


def stratified_split(rows, train_frac=0.70, val_frac=0.15, seed=42):
    """Group rows by root_cause_category, shuffle each group independently,
    then slice each group into train/val/test at the same proportions.
    This keeps every category represented in all three splits."""
    random.seed(seed)

    groups = defaultdict(list)
    for row in rows:
        groups[row["root_cause_category"]].append(row)

    train, val, test = [], [], []

    for category, group_rows in groups.items():
        shuffled = group_rows[:]
        random.shuffle(shuffled)

        n = len(shuffled)
        n_train = round(n * train_frac)
        n_val = round(n * val_frac)
        # whatever remains goes to test, so rounding never drops a row
        n_test = n - n_train - n_val

        train.extend(shuffled[:n_train])
        val.extend(shuffled[n_train:n_train + n_val])
        test.extend(shuffled[n_train + n_val:])

    # Shuffle the final combined lists too, so rows aren't grouped by category
    random.shuffle(train)
    random.shuffle(val)
    random.shuffle(test)

    return train, val, test


def write_csv(rows, fieldnames, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description="Split GraphTriage tickets into train/val/test")
    parser.add_argument("--input", type=str, default="../generated/tickets_raw.csv")
    parser.add_argument("--output-dir", type=str, default="../generated")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--train-frac", type=float, default=0.70)
    parser.add_argument("--val-frac", type=float, default=0.15)
    args = parser.parse_args()

    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_path = os.path.join(base_dir, args.input)
    output_dir = os.path.join(base_dir, args.output_dir)

    fieldnames, rows = read_tickets(input_path)
    train, val, test = stratified_split(rows, args.train_frac, args.val_frac, args.seed)

    write_csv(train, fieldnames, os.path.join(output_dir, "tickets_train.csv"))
    write_csv(val, fieldnames, os.path.join(output_dir, "tickets_val.csv"))
    write_csv(test, fieldnames, os.path.join(output_dir, "tickets_test.csv"))

    total = len(train) + len(val) + len(test)
    print(f"Total tickets: {total}")
    print(f"  train: {len(train)} ({len(train)/total:.1%}) -> tickets_train.csv")
    print(f"  val:   {len(val)} ({len(val)/total:.1%}) -> tickets_val.csv")
    print(f"  test:  {len(test)} ({len(test)/total:.1%}) -> tickets_test.csv")


if __name__ == "__main__":
    main()
