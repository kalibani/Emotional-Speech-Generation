.PHONY: help setup install install-dev test lint format clean run docker-build docker-run

help:
	@echo "Emotional Speech Generation - Available Commands:"
	@echo ""
	@echo "  setup          - Initial setup (create dirs, download models)"
	@echo "  install        - Install production dependencies"
	@echo "  install-dev    - Install development dependencies"
	@echo "  test           - Run tests with coverage"
	@echo "  test-unit      - Run unit tests only"
	@echo "  test-api       - Run API tests only"
	@echo "  lint           - Run linters (ruff, mypy)"
	@echo "  format         - Format code (black)"
	@echo "  clean          - Clean cache and temp files"
	@echo "  run            - Run API server locally"
	@echo "  run-dev        - Run API server in dev mode"
	@echo "  docker-build   - Build Docker image"
	@echo "  docker-run     - Run Docker container"
	@echo "  solution       - Run Part B CLI solution"

setup:
	@echo "Setting up project..."
	mkdir -p data/models data/audio_cache data/logs
	cp .env.example .env
	python scripts/setup_models.py

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements-dev.txt
	pre-commit install

test:
	pytest tests/ -v --cov=src --cov-report=html --cov-report=term

test-unit:
	pytest tests/unit/ -v

test-api:
	pytest tests/api/ -v

lint:
	ruff check src/ tests/
	mypy src/

format:
	black src/ tests/ scripts/
	ruff check --fix src/ tests/

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .mypy_cache .ruff_cache .coverage htmlcov/
	rm -rf data/audio_cache/*

run:
	uvicorn src.api.main:app --host 0.0.0.0 --port 8000

run-dev:
	uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload

docker-build:
	docker build -t emotional-tts:latest .

docker-run:
	docker run -p 8000:8000 -v $(PWD)/data:/app/data emotional-tts:latest

solution:
	@echo "Usage: python scripts/solution.py 'Your text here' output.wav --emotion excited --intensity 0.7"

