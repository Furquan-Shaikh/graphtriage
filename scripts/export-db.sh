#!/bin/sh
# Runs INSIDE the mysql container (called by export-db.ps1).
TABLES=$(mysql -N -u root -p"$MYSQL_ROOT_PASSWORD" -e "SHOW TABLES" "$MYSQL_DATABASE" 2>/dev/null | grep -v '^app_user$' | tr '\n' ' ')
echo "DATA TABLES: $TABLES"
mysqldump -u root -p"$MYSQL_ROOT_PASSWORD" --no-tablespaces --default-character-set=utf8mb4 --skip-add-locks --skip-dump-date "$MYSQL_DATABASE" $TABLES > /tmp/init.sql 2>/dev/null
mysqldump -u root -p"$MYSQL_ROOT_PASSWORD" --no-tablespaces --default-character-set=utf8mb4 --no-data --skip-dump-date "$MYSQL_DATABASE" app_user >> /tmp/init.sql 2>/dev/null