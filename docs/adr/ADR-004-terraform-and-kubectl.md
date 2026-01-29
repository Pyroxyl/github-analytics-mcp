# ADR-004: Terraform and kubectl Coexistence

## Status

Accepted

## Context

The project includes Kubernetes manifests in `k8s/` and Terraform configuration in `terraform/`. These are two different tools that can deploy the same workloads. The question is why both exist and when to use each.

## Decision

Maintain both deployment methods, each serving a different use case:

**`k8s/` — Raw Kubernetes manifests:**
- Deployed via `kubectl apply -f k8s/` or the provided `deploy.sh`
- Best for: learning Kubernetes, quick experiments, CI/CD pipelines that use `kubectl` directly
- No external state to manage, no init step required
- What you see is what you deploy

**`terraform/` — Terraform IaC:**
- Deployed via `terraform init && terraform apply`
- Best for: production environments, multi-environment setups, drift detection
- Manages state, supports `plan` before `apply`, can manage non-K8s resources (DNS, cloud IAM, etc.)
- Variables and `.tfvars` files enable environment-specific configuration

The two are not meant to be used simultaneously on the same cluster. They represent alternative deployment paths.

## Consequences

### Positive

- Users can choose the tool that matches their experience and requirements.
- The `k8s/` manifests serve as readable documentation of what Terraform creates.
- Learning path is gradual: start with `kubectl`, graduate to Terraform when state management matters.
- Terraform can be extended to provision cluster-level resources (namespaces, RBAC, cloud load balancers) that raw manifests cannot.

### Negative

- Two deployment paths must be kept in sync when the K8s resource definitions change.
- Users might accidentally apply both, creating duplicate resources.
- Terraform state introduces operational overhead (state storage, locking) for simple setups.

### Neutral

- The CI/CD pipeline uses `kubectl` for deployment (simplicity). Teams with Terraform Cloud or similar can swap this out.
