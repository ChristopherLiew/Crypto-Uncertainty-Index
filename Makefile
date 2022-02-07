# Set up
install:
	brew install poetry
	poetry install
	poetry shell
	poetry config experimental.new-installer = false

update:
	poetry update


# Docker
run:
	docker-compose -f docker-compose.yml up

build:
	docker-compose -f docker-compose.yml build

up:
	docker-compose -f docker-compose.yml up

down:
	echo "WARNING: composing down removes containers and"
	docker-compose -f docker-compose.yml down

stop:
	docker-compose -f docker-compose.yml stop

ps:
	docker-compose -f docker-compose.yml ps

# Postgres
pg-build:
	poetry shell
	python postgres/setup.py

# Elastic Cluster
es-cluster-health:
	curl -X GET "localhost:9200/_cluster/health?wait_for_status=yellow&timeout=30s&pretty"

es-cluster-stats:
	curl -X GET "localhost:9200/_cluster/stats?human&pretty&pretty"

# Clean Up
clean:
	rm -rf **/.ipynb_checkpoints **/.pytest_cache **/__pycache__ **/**/__pycache__ .ipynb_checkpoints .pytest_cache **/cache

# HEADACHE BUT IT FINALLY WORKS!!! 
# Install llvmlite + Bertopic
install-bertopic:
	brew install cmake
	arch -arm64 brew install llvm@11
	LLVM_CONFIG="/opt/homebrew/Cellar/llvm@11/11.1.0_4/bin/llvm-config" arch -arm64 poetry add llvmlite
	poetry add bertopic
