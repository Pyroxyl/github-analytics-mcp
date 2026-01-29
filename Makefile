# GitHub Analytics MCP Server - Makefile
# Common commands for Docker operations

.PHONY: build run stop logs shell clean rebuild test help api api-logs api-shell api-test \
       k8s-deploy k8s-status k8s-logs k8s-delete \
       terraform-init terraform-plan terraform-apply terraform-destroy

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

## k8s-deploy: Deploy to Kubernetes
k8s-deploy:
	bash k8s/deploy.sh

## k8s-status: Show K8s deployment status
k8s-status:
	@kubectl -n github-analytics get pods,svc,hpa

## k8s-logs: View API gateway pod logs
k8s-logs:
	kubectl -n github-analytics logs -f -l app=api-gateway

## k8s-delete: Delete all K8s resources
k8s-delete:
	kubectl delete namespace github-analytics --ignore-not-found

## terraform-init: Initialize Terraform
terraform-init:
	cd terraform && terraform init

## terraform-plan: Preview Terraform changes (dry-run)
terraform-plan:
	cd terraform && terraform plan -var="github_token=$${GITHUB_TOKEN}"

## terraform-apply: Apply Terraform configuration
terraform-apply:
	cd terraform && terraform apply -var="github_token=$${GITHUB_TOKEN}"

## terraform-destroy: Destroy all Terraform-managed resources
terraform-destroy:
	cd terraform && terraform destroy -var="github_token=$${GITHUB_TOKEN}"

## help: Show this help message
help:
	@echo "GitHub Analytics MCP Server - Available commands:"
	@echo ""
	@grep -E '^##' $(MAKEFILE_LIST) | sed -e 's/## /  /'
	@echo ""
	@echo "Usage: make <command>"
