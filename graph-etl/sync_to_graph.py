"""
GraphTriage — Sync Services + Tickets from MySQL to Neo4j (Day 3, Step 2)

Reads services and tickets from MySQL (loaded on Day 2) and creates the
corresponding (:Service) and (:Ticket) nodes in Neo4j, connected by
(:Ticket)-[:RAISED_ON]->(:Service), per docs/design.md Section 2.

This is Part 1 of the graph ETL — Bug and Fix nodes are added in Step 3
(sync_bugs_and_fixes function, added to this same file).

Safe to re-run: all writes use MERGE, so re-running won't create duplicates.

Prerequisites:
    pip install -r requirements.txt
    Neo4j constraints already applied (Day 3, Step 1 - setup_constraints.py)

Usage:
    cd graph-etl
    python3 sync_to_graph.py
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
    if not password:
        raise SystemExit("NEO4J_PASSWORD not found in .env — see Day 1 .env setup.")
    return GraphDatabase.driver(args.neo4j_uri, auth=(user, password))


def sync_services(mysql_cursor, neo4j_session):
    mysql_cursor.execute("SELECT id, name, owning_team FROM service")
    rows = mysql_cursor.fetchall()

    for mysql_id, name, owning_team in rows:
        neo4j_session.run(
            """
            MERGE (s:Service {name: $name})
            SET s.mysql_id = $mysql_id, s.owning_team = $owning_team
            """,
            name=name,
            mysql_id=mysql_id,
            owning_team=owning_team,
        )

    return len(rows)


def sync_tickets(mysql_cursor, neo4j_session):
    mysql_cursor.execute(
        """
        SELECT t.id, t.title, t.description, t.status, t.priority,
               t.created_at, t.resolved_at, t.dataset_split, s.name
        FROM ticket t
        JOIN service s ON t.service_id = s.id
        """
    )
    rows = mysql_cursor.fetchall()

    for (ticket_id, title, description, status, priority,
         created_at, resolved_at, dataset_split, service_name) in rows:
        neo4j_session.run(
            """
            MERGE (t:Ticket {id: $id})
            SET t.title = $title,
                t.description = $description,
                t.status = $status,
                t.priority = $priority,
                t.created_at = toString($created_at),
                t.resolved_at = toString($resolved_at),
                t.dataset_split = $dataset_split
            WITH t
            MATCH (s:Service {name: $service_name})
            MERGE (t)-[:RAISED_ON]->(s)
            """,
            id=ticket_id,
            title=title,
            description=description,
            status=status,
            priority=priority,
            created_at=created_at,
            resolved_at=resolved_at,
            dataset_split=dataset_split,
            service_name=service_name,
        )

    return len(rows)


def sync_bugs_and_fixes(mysql_cursor, neo4j_session):
    mysql_cursor.execute(
        """
        SELECT b.id, b.category, b.severity, b.ticket_id,
               f.id, f.description, f.resolution_time_hours
        FROM bug b
        JOIN fix f ON f.bug_id = b.id
        """
    )
    rows = mysql_cursor.fetchall()

    for (bug_id, category, severity, ticket_id,
         fix_id, fix_description, resolution_time_hours) in rows:
        neo4j_session.run(
            """
            MERGE (b:Bug {id: $bug_id})
            SET b.category = $category, b.severity = $severity
            WITH b
            MATCH (t:Ticket {id: $ticket_id})
            MERGE (t)-[:CAUSED_BY]->(b)
            WITH b
            MERGE (f:Fix {id: $fix_id})
            SET f.description = $fix_description,
                f.resolution_time_hours = $resolution_time_hours
            MERGE (b)-[:FIXED_BY]->(f)
            """,
            bug_id=bug_id,
            category=category,
            severity=severity,
            ticket_id=ticket_id,
            fix_id=fix_id,
            fix_description=fix_description,
            resolution_time_hours=resolution_time_hours,
        )

    return len(rows)


def main():
    parser = argparse.ArgumentParser(description="Sync MySQL services + tickets into Neo4j")
    parser.add_argument("--mysql-host", type=str, default="localhost")
    parser.add_argument("--mysql-port", type=int, default=3307,
                         help="MySQL host port - defaults to 3307 per the Day 1 port-conflict fix")
    parser.add_argument("--neo4j-uri", type=str, default="bolt://localhost:7687")
    args = parser.parse_args()

    load_env()

    mysql_conn = get_mysql_connection(args)
    mysql_cursor = mysql_conn.cursor()

    driver = get_neo4j_driver(args)
    driver.verify_connectivity()
    print("Connected to MySQL and Neo4j.")

    with driver.session() as session:
        service_count = sync_services(mysql_cursor, session)
        print(f"Synced {service_count} services.")

        ticket_count = sync_tickets(mysql_cursor, session)
        print(f"Synced {ticket_count} tickets (with RAISED_ON relationships).")

        bug_fix_count = sync_bugs_and_fixes(mysql_cursor, session)
        print(f"Synced {bug_fix_count} bug->fix pairs (with CAUSED_BY / FIXED_BY relationships).")

    mysql_cursor.close()
    mysql_conn.close()
    driver.close()

    print("Done.")


if __name__ == "__main__":
    main()
