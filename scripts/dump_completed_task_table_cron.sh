#!/bin/bash
set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd $PROJECT_DIR

docker compose exec -T db sh -c 'mysqldump -u $MARIADB_USER -p$MARIADB_PASSWORD web_prod completed_task' > ./completed_task_backup.sql

