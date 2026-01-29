# Terraform - Kubernetes Infrastructure

Manages Kubernetes resources for GitHub Analytics MCP using Terraform.

## Prerequisites

- [Terraform](https://developer.hashicorp.com/terraform/install) >= 1.0
- Kubernetes cluster (OrbStack / minikube / kind)
- `kubectl` configured with context `orbstack`
- Docker image built: `make build`

## Quick Start

```bash
# Initialize Terraform
make terraform-init

# Preview changes
make terraform-plan

# Apply (deploy resources)
make terraform-apply

# Destroy all resources
make terraform-destroy
```

## Manual Usage

```bash
cd terraform/

terraform init
terraform plan -var="github_token=$GITHUB_TOKEN"
terraform apply -var="github_token=$GITHUB_TOKEN"
terraform destroy -var="github_token=$GITHUB_TOKEN"
```

## Resources Created

| Resource | Name | Description |
|----------|------|-------------|
| Namespace | `github-analytics` | Isolated namespace |
| Secret | `github-analytics-secret` | GitHub token |
| Deployment | `api-gateway` | API Gateway (2 replicas) |
| Service | `api-gateway-service` | LoadBalancer on port 80 |
| HPA | `api-gateway-hpa` | Auto-scale 2-5 pods at 70% CPU |

## Variables

See `variables.tf` for all configurable values. Copy `terraform.tfvars.example` to `terraform.tfvars` for local overrides.
