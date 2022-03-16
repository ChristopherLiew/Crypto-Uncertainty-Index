help:
	@echo "Available Commands:"
	@echo " - install	: Installs all poetry related requirements"
	@echo " - update	: Updates requirements with poetry"
	@echo " - run		: Run docker compose up"
	@echo " - down		: Stops and removes all running docker services"
	@echo " - stop		: Stops running docker services"
	@echo " - ps		: Shows all running docker services"
	@echo " - pg-crypto-build	: Builds postgres with related crypto uncertainty tables"
	@echo " - es-cluster-health	: Get elasticsearch cluster health"
	@echo " - clean	: Cleans up project by removing python, pytest and ipynb caches"
	@echo " - format : Runs Black to format all python and jupyter files + SQLFluff for all SQL files"

install:
	brew install poetry
	poetry config experimental.new-installer = false
	poetry install
	poetry shell

update:
	poetry update

# Docker
run:
	docker-compose -f docker-compose.yml up

build:
	docker-compose -f docker-compose.yml build

down:
	echo "WARNING: composing down removes containers and"
	docker-compose -f docker-compose.yml down

stop:
	docker-compose -f docker-compose.yml stop

ps:
	docker-compose -f docker-compose.yml ps

# Postgres
pg-crypto-build:
	poetry shell
	python3 postgres/setup.py

# Elastic Cluster
es-cluster-health:
	curl -X GET "localhost:9200/_cluster/health?wait_for_status=yellow&timeout=30s&pretty"

es-cluster-stats:
	curl -X GET "localhost:9200/_cluster/stats?human&pretty&pretty"

# Clean Up
clean:
	rm -rf **/.ipynb_checkpoints **/.pytest_cache **/__pycache__ **/**/__pycache__ .ipynb_checkpoints .pytest_cache **/cache

format:
	black .
	sqlfluff fix . --dialect postgres

# Others
install-bertopic:
	brew install cmake
	arch -arm64 brew install llvm@11
	LLVM_CONFIG="/opt/homebrew/Cellar/llvm@11/11.1.0_4/bin/llvm-config" arch -arm64 poetry add llvmlite
	poetry add bertopic
