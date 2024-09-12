.PHONY: help init-db migrations migrate seed start stop restart clean lint test logs db-shell status web-shell

help:  ## Show this help message
	@echo "Make targets:"
	@echo "============="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

start:  ## Start docker-compose services
	@docker-compose up -d --build

stop:  ## Stop docker-compose services
	@docker-compose down

restart: stop start  ## Restart docker-compose services

status:  ## Show the status of docker-compose services
	@docker-compose ps

web-logs:  ## View logs from the web service
	@docker-compose logs -f fastapi-web

init-db:  ## Initialize the database
	@docker-compose exec fastapi-web aerich init-db

migrations:  ## Generate migration files
	@docker-compose exec fastapi-web aerich migrate

migrate:  ## Perform database migrations
	@docker-compose exec fastapi-web aerich upgrade

seed:  ## Seed the database
	@docker-compose exec fastapi-web python scripts/seed.py

db-shell:  ## Access the database shell
	@docker-compose exec db sh -c 'mysql -u $$MARIADB_USER -p$$MARIADB_PASSWORD'

web-shell:  ## Access the web shell
	@docker-compose exec fastapi-web sh

lint:  ## Run linting using pre-commit
	@poetry run pre-commit run --all-files

test:  ## Run tests using pytest
	@docker-compose exec fastapi-web python -m pytest

clean:  ## Clean up Docker images and containers
	@docker image prune -f
	@docker container prune -f
