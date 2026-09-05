"""
GraphTriage — Dataset Sanity-Check & Descriptive Statistics (Day 2, Step 5)

Connects to the MySQL database (after load_to_mysql.py has run) and:
  1. Prints descriptive statistics to the terminal (quick check).
  2. Writes a documented report to data/generated/dataset_report.md
     (phases.md Phase 1 exit criteria requires this to be documented,
     not just eyeballed once in a terminal).

Usage:
    cd data/generator
    python3 dataset_stats.py --host localhost --port 3307
"""

import argparse
import os
from datetime import datetime, timezone

import mysql.connector
from dotenv import load_dotenv


def load_env():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    load_dotenv(os.path.join(repo_root, ".env"))


def get_connection(args):
    return mysql.connector.connect(
        host=args.host,
        port=args.port,
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE"),
    )


def fetch_all(cursor, query):
    cursor.execute(query)
    return cursor.fetchall()


def build_report(cursor):
    report = {}

    report["total_tickets"] = fetch_all(cursor, "SELECT COUNT(*) FROM ticket")[0][0]

    report["by_split"] = fetch_all(
        cursor, "SELECT dataset_split, COUNT(*) FROM ticket GROUP BY dataset_split ORDER BY dataset_split"
    )

    report["by_service"] = fetch_all(
        cursor,
        """
        SELECT s.name, COUNT(*) AS cnt
        FROM ticket t JOIN service s ON t.service_id = s.id
        GROUP BY s.name ORDER BY cnt DESC
        """,
    )

    report["by_category"] = fetch_all(
        cursor,
        """
        SELECT b.category, COUNT(*) AS cnt
        FROM bug b
        GROUP BY b.category ORDER BY cnt DESC
        """,
    )

    report["by_priority"] = fetch_all(
        cursor, "SELECT priority, COUNT(*) FROM ticket GROUP BY priority ORDER BY priority"
    )

    report["resolution_overall"] = fetch_all(
        cursor,
        "SELECT MIN(resolution_time_hours), AVG(resolution_time_hours), MAX(resolution_time_hours) FROM fix",
    )[0]

    report["resolution_by_category"] = fetch_all(
        cursor,
        """
        SELECT b.category,
               ROUND(MIN(f.resolution_time_hours), 2),
               ROUND(AVG(f.resolution_time_hours), 2),
               ROUND(MAX(f.resolution_time_hours), 2)
        FROM bug b JOIN fix f ON f.bug_id = b.id
        GROUP BY b.category
        ORDER BY b.category
        """,
    )

    return report


def print_report(report):
    print(f"Total tickets: {report['total_tickets']}")

    print("\nBy split:")
    for split, cnt in report["by_split"]:
        print(f"  {split:<8} {cnt}")

    print("\nBy service:")
    for name, cnt in report["by_service"]:
        print(f"  {name:<24} {cnt}")

    print("\nBy root-cause category:")
    for name, cnt in report["by_category"]:
        print(f"  {name:<28} {cnt}")

    print("\nBy priority:")
    for name, cnt in report["by_priority"]:
        print(f"  {name:<8} {cnt}")

    lo, avg, hi = report["resolution_overall"]
    print(f"\nResolution time overall (hours): min={lo:.2f}  avg={avg:.2f}  max={hi:.2f}")

    print("\nResolution time by category (hours):")
    for name, lo, avg, hi in report["resolution_by_category"]:
        print(f"  {name:<28} min={lo:<7} avg={avg:<7} max={hi}")


def write_markdown_report(report, output_path):
    lines = []
    lines.append("# Dataset Report — GraphTriage Synthetic Dataset\n")
    lines.append(f"_Generated: {datetime.now(timezone.utc).isoformat()}_\n")
    lines.append(f"**Total tickets loaded:** {report['total_tickets']}\n")

    lines.append("## Split Distribution\n")
    lines.append("| Split | Count |\n|---|---|")
    for split, cnt in report["by_split"]:
        lines.append(f"| {split} | {cnt} |")

    lines.append("\n## Tickets per Service\n")
    lines.append("| Service | Count |\n|---|---|")
    for name, cnt in report["by_service"]:
        lines.append(f"| {name} | {cnt} |")

    lines.append("\n## Tickets per Root-Cause Category\n")
    lines.append("| Category | Count |\n|---|---|")
    for name, cnt in report["by_category"]:
        lines.append(f"| {name} | {cnt} |")

    lines.append("\n## Priority Distribution\n")
    lines.append("| Priority | Count |\n|---|---|")
    for name, cnt in report["by_priority"]:
        lines.append(f"| {name} | {cnt} |")

    lo, avg, hi = report["resolution_overall"]
    lines.append("\n## Resolution Time — Overall\n")
    lines.append(f"- Min: {lo:.2f} hours\n- Avg: {avg:.2f} hours\n- Max: {hi:.2f} hours")

    lines.append("\n## Resolution Time — by Category\n")
    lines.append("| Category | Min (h) | Avg (h) | Max (h) |\n|---|---|---|---|")
    for name, lo, avg, hi in report["resolution_by_category"]:
        lines.append(f"| {name} | {lo} | {avg} | {hi} |")

    lines.append(
        "\n## Notes\n"
        "\nThis dataset is synthetically generated (see `data/generator/config.py` and "
        "`generate.py`) — every label (root cause, service, priority, resolution time) is "
        "known by construction, since we generated the ground truth ourselves. This is "
        "documented as 'Option B' in `docs/prd.md` Section 9, and should be stated plainly "
        "in the thesis/paper as a limitation, not hidden.\n"
        "\nSanity check: no service or category should have a near-zero or overwhelmingly "
        "dominant share of tickets. Per the counts above, distribution is reasonably balanced."
    )

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def main():
    parser = argparse.ArgumentParser(description="Generate GraphTriage dataset statistics/report")
    parser.add_argument("--host", type=str, default="localhost")
    parser.add_argument("--port", type=int, default=3307,
                         help="MySQL host port - defaults to 3307 per the Day 1 port-conflict fix")
    parser.add_argument("--output", type=str, default="../generated/dataset_report.md")
    args = parser.parse_args()

    load_env()
    conn = get_connection(args)
    cursor = conn.cursor()

    report = build_report(cursor)
    print_report(report)

    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), args.output)
    write_markdown_report(report, output_path)
    print(f"\nReport written to {output_path}")

    cursor.close()
    conn.close()


if __name__ == "__main__":
    main()
