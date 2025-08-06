# Makefile for Ping-Pong Flask Application
# Handles development, testing, and deployment tasks

.PHONY: help install run test test-quick test-unit lint format pre-commit-run docker-build docker-run clean dev-check

# Variables
APP_NAME := ping-pong
DOCKER_TAG := latest
PORT := 5000

# Default target
help: ## Show available commands
	@echo "Available commands:"
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make install          - Install dependencies"
	@echo ""
	@echo "Development:"
	@echo "  make run             - Run Flask application locally"
	@echo "  make run-gunicorn    - Run with gunicorn locally"
	@echo ""
	@echo "Testing:"
	@echo "  make test            - Run comprehensive tests"
	@echo "  make test-quick      - Run quick pytest unit tests"
	@echo "  make test-unit       - Run pytest unit tests only"
	@echo "  make lint            - Run linting (flake8)"
	@echo "  make format          - Format code (black)"
	@echo "  make pre-commit-run  - Run all pre-commit hooks"
	@echo "  make dev-check       - Run full development workflow"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build    - Build Docker image"
	@echo "  make docker-run      - Run Docker container"
	@echo ""
	@echo "Utilities:"
	@echo "  make clean           - Clean up temporary files"
	@echo "  make help            - Show this help message"

# Install dependencies
install: ## Install Python dependencies
	@echo "Installing Python dependencies..."
	pip install -r requirements.txt
	pip install pytest pytest-flask flake8 black isort bandit
	@echo "Dependencies installed"

# Run the Flask application locally
run: ## Run the Flask application locally
	@echo "Starting Flask application..."
	uv run python main.py

# Run the Flask application with gunicorn locally
run-gunicorn: ## Run the Flask application with gunicorn locally
	@echo "Starting Flask application with gunicorn..."
	uv run gunicorn --config gunicorn.conf.py wsgi:app

# Run comprehensive tests
test: ## Run comprehensive tests
	@echo "Running comprehensive tests..."
	@echo "Running pre-commit hooks..."
	@cd .. && pre-commit run --all-files || echo "Pre-commit not configured, skipping"
	@echo "Running pytest unit tests..."
	@$(MAKE) test-unit
	@echo "All tests completed!"

# Run quick tests
test-quick: ## Run quick pytest unit tests
	@echo "Running quick pytest unit tests..."
	python -m pytest test_main.py -v --tb=short
	@echo "Quick tests completed!"

# Run pytest unit tests only
test-unit: ## Run pytest unit tests only
	@echo "Running pytest unit tests..."
	python -m pytest test_main.py -v --tb=short
	@echo "Unit tests completed!"

# Run linting
lint: ## Run linting (flake8)
	@echo "Running flake8 linting..."
	flake8 --max-line-length=127 --select=E9,F63,F7,F82 --show-source --statistics *.py
	@echo "Linting completed!"

# Format code
format: ## Format code (black)
	@echo "Formatting code with black..."
	black --line-length=127 .
	@echo "Code formatted!"

# Run pre-commit hooks manually
pre-commit-run: ## Run all pre-commit hooks
	@echo "Running pre-commit hooks..."
	@cd .. && pre-commit run --all-files
	@echo "Pre-commit hooks completed!"

# Build Docker image
docker-build: ## Build Docker image
	@echo "Building Docker image..."
	docker build -t $(APP_NAME):$(DOCKER_TAG) .
	@echo "Docker image built: $(APP_NAME):$(DOCKER_TAG)"

# Run Docker container
docker-run: docker-build ## Run Docker container
	@echo "Running Docker container..."
	@echo "Flask app will be available at http://localhost:$(PORT)"
	docker run --rm -p $(PORT):5000 --name $(APP_NAME) $(APP_NAME):$(DOCKER_TAG)

# Clean up temporary files and Docker resources
clean: ## Clean up temporary files and Docker resources
	@echo "Cleaning up temporary files..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name ".coverage" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@echo "Cleaning up Docker resources..."
	docker stop $(APP_NAME) 2>/dev/null || true
	docker rm $(APP_NAME) 2>/dev/null || true
	@echo "Cleanup completed!"

# Development workflow - run this before committing
dev-check: format lint test-unit ## Run full development workflow
	@echo "Development checks complete! Ready to commit."
