"""
GraphTriage — Validate Knowledge Graph (Day 3, Step 4)

Cross-checks that Neo4j node/relationship counts match the MySQL row counts
they were synced from (sync_to_graph.py), and prints one full sample chain
(Ticket -> Service, Ticket -> Bug -> Fix) so you can eyeball that the
relationships actually make sense, not just that the counts line up.

Usage:
    cd graph-etl
    python3 validate_graph.py
"""

import argparse
import os

import mysql.connector
from dotenv import load_dotenv
from neo4j import GraphDatabase


def load_env():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    load_dotenv(os.path.join(repo_root, ".env"))


def get_mysql_connection(args):
    return mysql.connector.connect(
        host=args.mysql_host,
        port=args.mysql_port,
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE"),
    )


def get_neo4j_driver(args):
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD")
    return GraphDatabase.driver(args.neo4j_uri, auth=(user, password))


def mysql_counts(cursor):
    cursor.execute("SELECT COUNT(*) FROM service")
    services = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM ticket")
    tickets = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM bug")
    bugs = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM fix")
    fixes = cursor.fetchone()[0]
    return {"Service": services, "Ticket": tickets, "Bug": bugs, "Fix": fixes}


def neo4j_node_counts(session):
    counts = {}
    for label in ["Service", "Ticket", "Bug", "Fix"]:
        result = session.run(f"MATCH (n:{label}) RETURN count(n) AS c")
        counts[label] = result.single()["c"]
    return counts


def neo4j_relationship_counts(session):
    counts = {}
    for rel in ["RAISED_ON", "CAUSED_BY", "FIXED_BY"]:
        result = session.run(f"MATCH ()-[r:{rel}]->() RETURN count(r) AS c")
        counts[rel] = result.single()["c"]
    return counts


def sample_chain(session):
    result = session.run(
        """
        MATCH (t:Ticket)-[:RAISED_ON]->(s:Service)
        MATCH (t)-[:CAUSED_BY]->(b:Bug)-[:FIXED_BY]->(f:Fix)
        RETURN t.id AS ticket_id, t.title AS title, s.name AS service,
               b.category AS root_cause, f.resolution_time_hours AS resolution_hours
        LIMIT 1
        """
    )
    return result.single()


def main():
    parser = argparse.ArgumentParser(description="Validate the GraphTriage knowledge graph")
    parser.add_argument("--mysql-host", type=str, default="localhost")
    parser.add_argument("--mysql-port", type=int, default=3307)
    parser.add_argument("--neo4j-uri", type=str, default="bolt://localhost:7687")
    args = parser.parse_args()

    load_env()

    mysql_conn = get_mysql_connection(args)
    mysql_cursor = mysql_conn.cursor()
    m_counts = mysql_counts(mysql_cursor)
    mysql_cursor.close()
    mysql_conn.close()

    driver = get_neo4j_driver(args)
    driver.verify_connectivity()

    with driver.session() as session:
        n_counts = neo4j_node_counts(session)
        r_counts = neo4j_relationship_counts(session)
        chain = sample_chain(session)

    driver.close()

    print("=== Node Count Cross-Check (MySQL rows vs Neo4j nodes) ===")
    all_match = True
    for label in ["Service", "Ticket", "Bug", "Fix"]:
        mysql_n, neo4j_n = m_counts[label], n_counts[label]
        status = "OK" if mysql_n == neo4j_n else "MISMATCH"
        if mysql_n != neo4j_n:
            all_match = False
        print(f"  {label:<10} MySQL={mysql_n:<6} Neo4j={neo4j_n:<6} [{status}]")

    print("\n=== Relationship Counts ===")
    for rel, count in r_counts.items():
        print(f"  {rel:<12} {count}")
    # Every ticket should have exactly one RAISED_ON, one CAUSED_BY;
    # every bug should have exactly one FIXED_BY (1 bug : 1 fix in this dataset).
    expected = m_counts["Ticket"]
    for rel in ["RAISED_ON", "CAUSED_BY"]:
        if r_counts[rel] != expected:
            all_match = False
            print(f"  WARNING: expected {expected} {rel} relationships, found {r_counts[rel]}")
    if r_counts["FIXED_BY"] != m_counts["Bug"]:
        all_match = False
        print(f"  WARNING: expected {m_counts['Bug']} FIXED_BY relationships, found {r_counts['FIXED_BY']}")

    print("\n=== Sample Full Chain (Ticket -> Service, Ticket -> Bug -> Fix) ===")
    if chain:
        print(f"  Ticket #{chain['ticket_id']}: {chain['title']}")
        print(f"    -> Service: {chain['service']}")
        print(f"    -> Root cause: {chain['root_cause']}")
        print(f"    -> Resolution time: {chain['resolution_hours']}h")
    else:
        print("  No complete chain found - something is wrong with the sync.")
        all_match = False

    print("\n" + ("ALL CHECKS PASSED" if all_match else "SOME CHECKS FAILED - see above"))


if __name__ == "__main__":
    main()
