#!/bin/bash
set -e

NAMESPACE="github-analytics"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "============================================"
echo "  GitHub Analytics K8s Deployment"
echo "============================================"

# Step 1: Build Docker images
echo ""
echo "[1/5] Building Docker images..."
docker build -t github-analytics-mcp "$PROJECT_DIR"
docker build -t github-analytics-api -f "$PROJECT_DIR/api/Dockerfile" "$PROJECT_DIR"
echo "  Images built."

# Step 2: Create namespace
echo ""
echo "[2/5] Creating namespace..."
kubectl apply -f "$SCRIPT_DIR/namespace.yaml"

# Step 3: Apply configs and secrets
echo ""
echo "[3/5] Applying configs and secrets..."
kubectl apply -f "$SCRIPT_DIR/configmap.yaml"
kubectl apply -f "$SCRIPT_DIR/secret.yaml"

# Step 4: Deploy applications
echo ""
echo "[4/5] Deploying applications..."
kubectl apply -f "$SCRIPT_DIR/deployment-mcp.yaml"
kubectl apply -f "$SCRIPT_DIR/deployment-api.yaml"
kubectl apply -f "$SCRIPT_DIR/service-api.yaml"
kubectl apply -f "$SCRIPT_DIR/hpa-api.yaml"

# Step 5: Wait for pods
echo ""
echo "[5/5] Waiting for pods to be ready..."
kubectl -n "$NAMESPACE" rollout status deployment/api-gateway --timeout=120s
kubectl -n "$NAMESPACE" rollout status deployment/mcp-server --timeout=120s

# Summary
echo ""
echo "============================================"
echo "  Deployment Complete"
echo "============================================"
echo ""
kubectl -n "$NAMESPACE" get pods
echo ""
kubectl -n "$NAMESPACE" get svc
echo ""
echo "API endpoint: http://localhost (via LoadBalancer)"
echo "Docs: http://localhost/docs"
