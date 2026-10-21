#!/bin/sh
set -e

echo "Waiting for Neo4j and applying constraints..."
i=0
until python setup_constraints.py --uri "$NEO4J_URI"; do
  i=$((i+1))
  if [ "$i" -ge 30 ]; then
    echo "Neo4j not reachable, giving up."
    exit 1
  fi
  echo "Neo4j not ready yet (try $i/30), retrying in 5s..."
  sleep 5
done

python sync_to_graph.py --mysql-host "$MYSQL_HOST" --mysql-port "$MYSQL_PORT" --neo4j-uri "$NEO4J_URI"
python validate_graph.py --mysql-host "$MYSQL_HOST" --mysql-port "$MYSQL_PORT" --neo4j-uri "$NEO4J_URI" || true

echo "Graph seed finished."