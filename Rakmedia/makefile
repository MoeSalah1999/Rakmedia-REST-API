# ----------------------------------------
# Makefile for Django Production Project
# ----------------------------------------
# Author: Moe Salah
# Description:
#   This Makefile provides convenient shortcuts
#   for managing the Django application, Docker, testing,
#   environment setup, and deployment tasks.
# ----------------------------------------

# Variables
PROJECT_NAME=task_management_system
DOCKER_IMAGE=$(PROJECT_NAME):latest
DOCKER_COMPOSE_FILE=docker-compose.yml
ENV_FILE=.env
PYTHON=python
MANAGE=$(PYTHON) manage.py

# ========================================
# ENVIRONMENT SETUP
# ========================================

.PHONY: install
install:
	@echo "Installing dependencies..."
	pip install --upgrade pip
	pip install -r requirements.txt
	@echo "✅ Dependencies installed successfully."

.PHONY: makemigrations
makemigrations:
	@echo "🔧 Creating new migrations..."
	$(MANAGE) makemigrations
	@echo "✅ Migrations created."

.PHONY: migrate
migrate:
	@echo "📦 Applying migrations..."
	$(MANAGE) migrate
	@echo "✅ Database migrated successfully."

.PHONY: createsuperuser
createsuperuser:
	@echo "👑 Creating superuser..."
	$(MANAGE) createsuperuser

.PHONY: collectstatic
collectstatic:
	@echo "📁 Collecting static files..."
	$(MANAGE) collectstatic --noinput
	@echo "✅ Static files collected."

.PHONY: shell
shell:
	@echo "🐚 Opening Django shell..."
	$(MANAGE) shell

# ========================================
# SERVER COMMANDS
# ========================================

.PHONY: run
run:
	@echo "🚀 Running development server..."
	$(MANAGE) runserver 0.0.0.0:8000

.PHONY: run-prod
run-prod:
	@echo "🚀 Running Django in production mode..."
	DJANGO_SETTINGS_MODULE=project.settings.prod $(MANAGE) runserver 0.0.0.0:8000

.PHONY: worker
worker:
	@echo "⚙️  Running Django Q worker..."
	$(MANAGE) qcluster

# ========================================
# TESTING & QUALITY
# ========================================

.PHONY: test
test:
	@echo "🧪 Running unit tests..."
	$(MANAGE) test
	@echo "✅ All tests passed."

.PHONY: lint
lint:
	@echo "🧹 Linting code with flake8..."
	flake8 --max-line-length=100 .
	@echo "✅ Linting completed."

.PHONY: format
format:
	@echo "✨ Formatting code with black..."
	black .
	@echo "✅ Code formatted."

.PHONY: coverage
coverage:
	@echo "📊 Running test coverage report..."
	coverage run manage.py test
	coverage report -m
	coverage html
	@echo "✅ Coverage report generated (see htmlcov/index.html)."

# ========================================
# DOCKER COMMANDS
# ========================================

.PHONY: docker-build
docker-build:
	@echo "🐳 Building Docker image..."
	docker build -t $(DOCKER_IMAGE) .
	@echo "✅ Docker image built successfully."

.PHONY: docker-up
docker-up:
	@echo "🐳 Starting Docker containers..."
	docker-compose -f $(DOCKER_COMPOSE_FILE) up -d
	@echo "✅ Containers started."

.PHONY: docker-down
docker-down:
	@echo "🧹 Stopping Docker containers..."
	docker-compose -f $(DOCKER_COMPOSE_FILE) down
	@echo "✅ Containers stopped."

.PHONY: docker-logs
docker-logs:
	@echo "📜 Showing Docker logs..."
	docker-compose logs -f

.PHONY: docker-prune
docker-prune:
	@echo "🧽 Cleaning up Docker resources..."
	docker system prune -af
	@echo "✅ Docker cleaned."

# ========================================
# DATABASE UTILITIES
# ========================================

.PHONY: dbshell
dbshell:
	@echo "🐘 Opening PostgreSQL shell..."
	$(MANAGE) dbshell

.PHONY: dumpdata
dumpdata:
	@echo "💾 Dumping data to fixtures.json..."
	$(MANAGE) dumpdata --indent 2 > fixtures.json
	@echo "✅ Data dumped successfully."

.PHONY: loaddata
loaddata:
	@echo "📥 Loading data from fixtures.json..."
	$(MANAGE) loaddata fixtures.json
	@echo "✅ Data loaded successfully."

# ========================================
# DEPLOYMENT & CLEANUP
# ========================================

.PHONY: clean
clean:
	@echo "🧹 Cleaning up pycache and temp files..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	@echo "✅ Project cleaned."

.PHONY: resetdb
resetdb:
	@echo "⚠️ Resetting database..."
	$(MANAGE) flush --no-input
	$(MAKE) migrate
	@echo "✅ Database reset."

.PHONY: help
help:
	@echo "📘 Available Make commands:"
	@grep '^[a-zA-Z_-]\+:' Makefile | sed 's/:.*//'
