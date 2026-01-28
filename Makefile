# GitHub Analytics MCP Server - Makefile
# Common commands for Docker operations

.PHONY: build run stop logs shell clean rebuild test help api api-logs api-shell api-test

# Default target
.DEFAULT_GOAL := help

# Variables
IMAGE_NAME := github-analytics-mcp
CONTAINER_NAME := github-analytics-mcp
API_CONTAINER := github-analytics-api

## build: Build all Docker images
build:
	docker-compose build

## run: Start MCP server
run:
	docker-compose up -d mcp-server

## run-api: Start API gateway
run-api:
	docker-compose up -d api-gateway

## run-all: Start all services
run-all:
	docker-compose up -d mcp-server api-gateway

## run-with-redis: Start all with Redis cache
run-with-redis:
	docker-compose --profile with-cache up -d

## stop: Stop all containers
stop:
	docker-compose down

## logs: View MCP server logs
logs:
	docker-compose logs -f mcp-server

## api-logs: View API gateway logs
api-logs:
	docker-compose logs -f api-gateway

## shell: Open shell in MCP server container
shell:
	docker exec -it $(CONTAINER_NAME) /bin/bash

## api-shell: Open shell in API gateway container
api-shell:
	docker exec -it $(API_CONTAINER) /bin/bash

## clean: Remove containers, images, and volumes
clean:
	docker-compose down -v --rmi local
	docker image prune -f

## rebuild: Clean rebuild all images
rebuild: stop
	docker-compose build --no-cache
	docker-compose up -d mcp-server api-gateway

## test: Run unit tests
test:
	docker run --rm --env-file .env $(IMAGE_NAME) python -m pytest

## api-test: Test API endpoints
api-test:
	@echo "Testing API endpoints..."
	@curl -s http://localhost:8080/health | python3 -m json.tool
	@echo "\nAPI is running!"

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
