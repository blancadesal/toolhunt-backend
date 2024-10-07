#!/bin/bash
set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd $PROJECT_DIR

docker compose exec -T web python scripts/update_db.py
docker compose exec -T web cat db_update.log > db_update.log
docker compose exec -T web rm db_update.log

