.PHONY: help install run docker-build docker-run clean

# Variables
APP_NAME := ping-pong
DOCKER_TAG := latest
PORT := 5000

help: ## Show this help message
	@echo "Available targets:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install Python dependencies
	pip install -r requirements.txt

run: ## Run the Flask application locally
	uv run python main.py

run-gunicorn: ## Run the Flask application with gunicorn locally
	uv run gunicorn --config gunicorn.conf.py wsgi:app

docker-build: ## Build Docker image
	docker build -t $(APP_NAME):$(DOCKER_TAG) .

docker-run: ## Run Docker container
	docker run --rm -p $(PORT):5000 --name $(APP_NAME) $(APP_NAME):$(DOCKER_TAG)

clean: ## Clean up Docker containers and images
	docker stop $(APP_NAME) 2>/dev/null || true
	docker rm $(APP_NAME) 2>/dev/null || true
	docker rmi $(APP_NAME):$(DOCKER_TAG) 2>/dev/null || true

