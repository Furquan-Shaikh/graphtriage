"""
GraphTriage — Load Synthetic Dataset into MySQL (Day 2, Step 4)

Reads tickets_train.csv, tickets_val.csv, tickets_test.csv (produced by
generate.py + split_dataset.py) and loads them into the MySQL schema defined
in schema.sql, creating service / ticket / bug / fix rows.

This script runs from your HOST machine (not inside Docker), connecting to
the MySQL container via its exposed host port. Per the Day 1 port-conflict
fix (see docs/memory.md Section 3), that port is 3307, not the MySQL default
3306 — override with --port if your setup differs.

Prerequisites:
    pip install mysql-connector-python python-dotenv

Usage:
    cd data/generator
    python3 load_to_mysql.py
"""

import argparse
import csv
import os

import mysql.connector
from dotenv import load_dotenv

SPLIT_FILES = {
    "train": "tickets_train.csv",
    "val": "tickets_val.csv",
    "test": "tickets_test.csv",
}


def load_env():
    # .env lives at the repo root, two levels up from data/generator/
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


def create_schema(cursor):
    schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "schema.sql")
    with open(schema_path, "r") as f:
        schema_sql = f.read()
    for statement in schema_sql.split(";"):
        statement = statement.strip()
        if statement:
            cursor.execute(statement)


def get_or_create_service(cursor, service_cache, service_name):
    if service_name in service_cache:
        return service_cache[service_name]

    cursor.execute("SELECT id FROM service WHERE name = %s", (service_name,))
    row = cursor.fetchone()
    if row:
        service_id = row[0]
    else:
        cursor.execute("INSERT INTO service (name) VALUES (%s)", (service_name,))
        service_id = cursor.lastrowid

    service_cache[service_name] = service_id
    return service_id


def load_split(cursor, service_cache, csv_path, split_name):
    with open(csv_path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    for row in rows:
        service_id = get_or_create_service(cursor, service_cache, row["service_name"])

        cursor.execute(
            """
            INSERT INTO ticket
                (title, description, service_id, status, priority,
                 created_at, resolved_at, dataset_split)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                row["title"],
                row["description"],
                service_id,
                row["status"],
                row["priority"],
                row["created_at"].replace("T", " ")[:19],
                row["resolved_at"].replace("T", " ")[:19],
                split_name,
            ),
        )
        ticket_id = cursor.lastrowid

        cursor.execute(
            "INSERT INTO bug (ticket_id, category, severity) VALUES (%s, %s, %s)",
            (ticket_id, row["root_cause_category"], row["priority"]),
        )
        bug_id = cursor.lastrowid

        cursor.execute(
            "INSERT INTO fix (bug_id, description, resolution_time_hours) VALUES (%s, %s, %s)",
            (bug_id, row["fix_description"], float(row["resolution_time_hours"])),
        )

    return len(rows)


def main():
    parser = argparse.ArgumentParser(description="Load synthetic GraphTriage dataset into MySQL")
    parser.add_argument("--host", type=str, default="localhost")
    parser.add_argument("--port", type=int, default=3307,
                         help="MySQL host port - defaults to 3307 per the Day 1 port-conflict fix")
    parser.add_argument("--data-dir", type=str, default="../generated")
    args = parser.parse_args()

    load_env()

    conn = get_connection(args)
    cursor = conn.cursor()

    print("Creating schema (if not already present)...")
    create_schema(cursor)
    conn.commit()

    service_cache = {}
    base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), args.data_dir)

    total_loaded = 0
    for split_name, filename in SPLIT_FILES.items():
        csv_path = os.path.join(base_dir, filename)
        count = load_split(cursor, service_cache, csv_path, split_name)
        conn.commit()
        print(f"  Loaded {count} tickets from {filename} (split={split_name})")
        total_loaded += count

    cursor.close()
    conn.close()

    print(f"Done. Total tickets loaded: {total_loaded}")
    print(f"Services created: {len(service_cache)} -> {list(service_cache.keys())}")


if __name__ == "__main__":
    main()
