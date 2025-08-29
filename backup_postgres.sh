#!/bin/bash
# Backup PostgreSQL database to a .sql file
# Usage: source environment variables before running

export PGPASSWORD="${POSTGRES_PASSWORD}"
pg_dump -h "${POSTGRES_HOST}" -U "${POSTGRES_USER}" -d "${POSTGRES_DATABASE}" -F c -b -v -f "asa_postgres_backup_$(date +%Y%m%d_%H%M%S).sql"
unset PGPASSWORD
