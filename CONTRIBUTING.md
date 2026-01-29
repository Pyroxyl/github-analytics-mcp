# Contributing

## Development Workflow

1. Fork the repository
2. Create a feature branch from `main`:
   ```bash
   git checkout -b feature/your-feature
   ```
3. Make your changes
4. Run tests locally:
   ```bash
   make test
   ```
5. Commit and push:
   ```bash
   git add .
   git commit -m "feat: description of changes"
   git push origin feature/your-feature
   ```
6. Open a Pull Request against `main`

## Branch Strategy

| Branch | Purpose |
|--------|---------|
| `main` | Production-ready code. Deploys automatically. |
| `develop` | Integration branch for features. |
| `feature/*` | New features. PR into `main`. |
| `fix/*` | Bug fixes. PR into `main`. |

## Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` — New feature
- `fix:` — Bug fix
- `docs:` — Documentation
- `chore:` — Maintenance
- `refactor:` — Code restructure
- `test:` — Tests

## CI/CD Pipeline

When you open a PR:
1. **CI** runs automatically — lints code with `ruff` and runs `pytest`
2. PR must pass CI before merging

When merged to `main`:
1. **Docker Build** — builds and pushes images to `ghcr.io`
2. **CD** — deploys to Kubernetes via Terraform

## Local Development

```bash
# Setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run server
python -m src.server

# Run API gateway
uvicorn src.api:app --reload --port 8080

# Run tests
pytest tests/ -v

# Docker
make build
make run-all
```

## Infrastructure

- **Docker**: `make build` / `make run-all`
- **Kubernetes**: `make k8s-deploy` / `make k8s-status`
- **Terraform**: `make terraform-plan` / `make terraform-apply`
