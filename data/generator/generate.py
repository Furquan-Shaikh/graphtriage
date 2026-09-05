"""
GraphTriage — Synthetic Ticket Generator (Day 2, Step 2)

Reads the definitions in config.py (services, root-cause categories, templates)
and generates a set of realistic-looking, fully-labeled tickets, writing them
to data/generated/tickets_raw.csv.

Every generated ticket already has a known root cause, service, priority, and
resolution time (since we generated it) — this is the synthetic "ground truth"
labels that GraphTriage's models will later be trained and evaluated against.

Usage:
    cd data/generator
    python3 generate.py --count 1200 --seed 42
"""

import argparse
import csv
import os
import random
from datetime import datetime, timedelta, timezone

from config import SERVICES, ROOT_CAUSES

FIELDNAMES = [
    "ticket_id",
    "title",
    "description",
    "service_name",
    "root_cause_category",
    "priority",
    "created_at",
    "resolved_at",
    "resolution_time_hours",
    "status",
    "fix_description",
]


def weighted_priority(category_cfg):
    """Pick a priority (LOW/MEDIUM/HIGH) using this category's probability weights."""
    weights = category_cfg["priority_weights"]
    return random.choices(population=list(weights.keys()), weights=list(weights.values()), k=1)[0]


def random_created_at(days_back=180):
    """Pick a random timestamp within the last `days_back` days, so tickets are
    spread out over roughly 6 months rather than all happening 'now'."""
    now = datetime.now(timezone.utc)
    offset_seconds = random.randint(0, days_back * 24 * 3600)
    return now - timedelta(seconds=offset_seconds)


def generate_ticket(ticket_id, category_name, category_cfg):
    service = random.choice(SERVICES)
    priority = weighted_priority(category_cfg)

    dlo, dhi = category_cfg["detail_range"]
    n = random.randint(int(dlo), int(dhi))
    unit = category_cfg["detail_unit"]

    title = random.choice(category_cfg["title_templates"]).format(service=service, n=n, unit=unit)
    description = random.choice(category_cfg["description_templates"]).format(service=service, n=n, unit=unit)

    rlo, rhi = category_cfg["resolution_time_hours"]
    resolution_time_hours = round(random.uniform(rlo, rhi), 2)

    created_at = random_created_at()
    resolved_at = created_at + timedelta(hours=resolution_time_hours)

    fix_description = (
        f"Root cause identified as '{category_name}' on {service}. "
        f"Applied standard remediation and verified recovery."
    )

    return {
        "ticket_id": ticket_id,
        "title": title,
        "description": description,
        "service_name": service,
        "root_cause_category": category_name,
        "priority": priority,
        "created_at": created_at.isoformat(),
        "resolved_at": resolved_at.isoformat(),
        "resolution_time_hours": resolution_time_hours,
        "status": "RESOLVED",
        "fix_description": fix_description,
    }


def generate_dataset(count, seed=42):
    random.seed(seed)
    category_names = list(ROOT_CAUSES.keys())
    tickets = []
    for i in range(1, count + 1):
        category_name = random.choice(category_names)
        category_cfg = ROOT_CAUSES[category_name]
        tickets.append(generate_ticket(i, category_name, category_cfg))
    return tickets


def write_csv(tickets, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(tickets)


def main():
    parser = argparse.ArgumentParser(description="Generate synthetic GraphTriage tickets")
    parser.add_argument("--count", type=int, default=1200, help="Number of tickets to generate")
    parser.add_argument("--seed", type=int, default=42, help="Random seed (same seed = same dataset, reproducible)")
    parser.add_argument("--output", type=str, default="../generated/tickets_raw.csv", help="Output CSV path")
    args = parser.parse_args()

    tickets = generate_dataset(args.count, args.seed)
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), args.output)
    write_csv(tickets, output_path)

    print(f"Generated {len(tickets)} tickets -> {output_path}")


if __name__ == "__main__":
    main()
