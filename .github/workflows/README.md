# CI/CD Pipelines

## Workflow Overview

```
Push/PR → [CI] → Tests + Lint
                    │
Push to main → [Docker Build] → Build & push to ghcr.io
                                      │
                              [CD] → Terraform apply → Health check
```

## Workflows

### CI (`ci.yml`)
- **Trigger**: Every push and PR to `main`/`develop`
- **Actions**: Install deps, lint with ruff, run pytest
- **Matrix**: Python 3.11, 3.12

### Docker Build (`docker-build.yml`)
- **Trigger**: Push to `main` (when source/Docker files change)
- **Actions**: Build MCP server + API gateway images, push to `ghcr.io`
- **Tags**: Git SHA + `latest`

### CD (`cd.yml`)
- **Trigger**: After successful Docker Build workflow
- **Actions**: Terraform init/apply, rollout status check, pod verification

## Required Secrets

| Secret | Description |
|--------|-------------|
| `GITHUB_TOKEN` | Auto-provided by GitHub Actions (for GHCR + CI tests) |
| `GH_ANALYTICS_TOKEN` | GitHub PAT for the MCP server's API calls |
| `KUBECONFIG` | Base64-encoded kubeconfig for the target cluster |

Set secrets at: **Settings → Secrets and variables → Actions**
