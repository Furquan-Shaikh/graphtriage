// GraphTriage — Neo4j Schema Constraints & Indexes (Day 3, Step 1)
//
// Matches the node types in docs/design.md Section 2.
// These ensure MERGE-based upserts (used by the ETL scripts) don't create
// duplicate nodes, and that lookups by these properties are fast.
//
// Neo4j 5.x syntax (matches the neo4j:5.20-community image in docker-compose.yml).
// Can be run manually in Neo4j Browser (http://localhost:7474), or via
// setup_constraints.py, which reads and executes this file.

CREATE CONSTRAINT service_name_unique IF NOT EXISTS
FOR (s:Service) REQUIRE s.name IS UNIQUE;

CREATE CONSTRAINT ticket_id_unique IF NOT EXISTS
FOR (t:Ticket) REQUIRE t.id IS UNIQUE;

CREATE CONSTRAINT bug_id_unique IF NOT EXISTS
FOR (b:Bug) REQUIRE b.id IS UNIQUE;

CREATE CONSTRAINT fix_id_unique IF NOT EXISTS
FOR (f:Fix) REQUIRE f.id IS UNIQUE;

// Index on dataset_split — Day 5 (GNN training) will repeatedly filter
// tickets by 'train' / 'val' / 'test', so this keeps that fast as the
// graph grows.
CREATE INDEX ticket_split_index IF NOT EXISTS
FOR (t:Ticket) ON (t.dataset_split);
