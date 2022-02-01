# Set up
install:
	brew install poetry
	poetry install
	poetry shell
	poetry config experimental.new-installer = false

update:
	poetry update

exit:
	exit

# Docker
run:
	docker-compose -f docker-compose.yml up

build:
	docker-compose -f docker-compose.yml build

up:
	docker-compose -f docker-compose.yml up

down:
	docker-compose -f docker-compose.yml down

stop:
	docker-compose -f docker-compose.yml stop

ps:
	docker-compose -f docker-compose.yml ps

# Elastic Cluster
es-cluster-health:
	curl -X GET "localhost:9200/_cluster/health?wait_for_status=yellow&timeout=30s&pretty"

es-cluster-stats:
	curl -X GET "localhost:9200/_cluster/stats?human&pretty&pretty"

# Clean Up
clean:
	rm -rf **/.ipynb_checkpoints **/.pytest_cache **/__pycache__ **/**/__pycache__ .ipynb_checkpoints .pytest_cache
