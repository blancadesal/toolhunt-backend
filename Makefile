.PHONY: help init-db migrations migrate seed start start-prod stop restart clean lint test logs db-shell db-exec status web-shell update-db

help:  ## Show this help message
	@echo "Make targets:"
	@echo "============="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

start:  ## Start docker compose services (dev)
	@docker compose up -d --build

start-prod:  ## Start docker compose services (prod)
	@docker compose -f compose.yml -f compose.prod.yml up -d --build

stop:  ## Stop docker compose services
	@docker compose down

restart: stop start  ## Restart docker compose services

status:  ## Show the status of docker compose services
	@docker compose ps

web-logs:  ## View logs from the web service
	@docker compose logs -f web

init-db:  ## Initialize the database
	@docker compose exec web aerich init-db

migrations:  ## Generate migration files
	@docker compose exec web aerich migrate

migrate:  ## Perform database migrations
	@docker compose exec web aerich upgrade

seed:  ## Seed the database with test data
	@docker compose exec web python scripts/seed.py

update-db:  ## Update the database with tool and task information from the Toolhub API
	@docker compose exec web python scripts/update_db.py

db-shell:  ## Access the mariadb shell
	@docker compose exec db sh -c 'mysql -u $$MARIADB_USER -p$$MARIADB_PASSWORD'

db-exec:  ## Access the db shell
	@docker compose exec db sh

web-shell:  ## Access the web shell
	@docker compose exec web sh

lint:  ## Lint using pre-commit
	@echo "Running pre-commit..."
	@poetry run pre-commit run --all-files

test:  ## Run tests using pytest
	@docker compose exec web python -m pytest

clean:  ## Clean up Docker images and containers
	@docker image prune -f
	@docker container prune -f
