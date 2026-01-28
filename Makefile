# GitHub Analytics MCP Server - Makefile
# Common commands for Docker operations

.PHONY: build run stop logs shell clean rebuild test help

# Default target
.DEFAULT_GOAL := help

# Variables
IMAGE_NAME := github-analytics-mcp
CONTAINER_NAME := github-analytics-mcp

## build: Build Docker image
build:
	docker build -t $(IMAGE_NAME) .

## run: Start the container using docker-compose
run:
	docker-compose up -d mcp-server

## run-with-redis: Start with Redis cache enabled
run-with-redis:
	docker-compose --profile with-cache up -d

## stop: Stop all containers
stop:
	docker-compose down

## logs: View container logs (follow mode)
logs:
	docker-compose logs -f mcp-server

## shell: Open a shell in the running container
shell:
	docker exec -it $(CONTAINER_NAME) /bin/bash

## clean: Remove containers, images, and volumes
clean:
	docker-compose down -v --rmi local
	docker image prune -f

## rebuild: Clean rebuild of the image
rebuild: stop
	docker-compose build --no-cache
	docker-compose up -d mcp-server

## test: Run tests inside container
test:
	docker run --rm --env-file .env $(IMAGE_NAME) python -m pytest

## status: Show container status
status:
	docker-compose ps

## help: Show this help message
help:
	@echo "GitHub Analytics MCP Server - Available commands:"
	@echo ""
	@grep -E '^##' $(MAKEFILE_LIST) | sed -e 's/## /  /'
	@echo ""
	@echo "Usage: make <command>"
