"""
GraphTriage — Apply Neo4j Constraints & Indexes (Day 3, Step 1)

Reads schema_constraints.cypher and executes each statement against Neo4j.
Safe to re-run — every statement uses "IF NOT EXISTS".

This connects via the Bolt protocol (port 7687 by default in docker-compose.yml —
NOT the same as the 7474 Browser/HTTP port).

Prerequisites:
    pip install -r requirements.txt

Usage:
    cd graph-etl
    python3 setup_constraints.py
"""

import argparse
import os

from dotenv import load_dotenv
from neo4j import GraphDatabase


def load_env():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    load_dotenv(os.path.join(repo_root, ".env"))


def read_statements(cypher_path):
    with open(cypher_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Strip line comments (//...) and split on ';' to get individual statements.
    statements = []
    for raw_line in content.splitlines():
        line = raw_line.split("//", 1)[0]
        statements.append(line)
    joined = "\n".join(statements)

    return [stmt.strip() for stmt in joined.split(";") if stmt.strip()]


def main():
    parser = argparse.ArgumentParser(description="Apply Neo4j constraints/indexes for GraphTriage")
    parser.add_argument("--uri", type=str, default="bolt://localhost:7687",
                         help="Neo4j Bolt URI (note: port 7687, not the 7474 Browser port)")
    args = parser.parse_args()

    load_env()
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD")

    if not password:
        raise SystemExit(
            "NEO4J_PASSWORD not found in .env. Make sure .env exists at the repo root "
            "and matches the password you set in NEO4J_AUTH (see Day 1, .env setup)."
        )

    cypher_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "schema_constraints.cypher")
    statements = read_statements(cypher_path)

    driver = GraphDatabase.driver(args.uri, auth=(user, password))

    try:
        driver.verify_connectivity()
        print(f"Connected to Neo4j at {args.uri}")

        with driver.session() as session:
            for statement in statements:
                print(f"Running: {statement.splitlines()[0][:80]}...")
                session.run(statement)

        print(f"\nApplied {len(statements)} constraint/index statements successfully.")

    finally:
        driver.close()


if __name__ == "__main__":
    main()
