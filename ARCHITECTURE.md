# Architecture

## Design Philosophy

**One domain, two interfaces, shared core logic.**

This project wraps the GitHub API into a single business-logic layer (`GitHubClient`) and exposes it through two thin adapters: an MCP server for AI agents and a FastAPI gateway for humans and programs. Neither adapter contains business logic — they only translate between their protocol and the shared core.

This is intentional. The goal is to demonstrate how a well-factored service layer can serve multiple access patterns without duplicating logic.

## Layered Architecture

```
┌─────────────────────────────────────────────────────┐
│  Interface Layer                                     │
│  ┌──────────────────┐  ┌──────────────────────────┐ │
│  │  MCP Server       │  │  FastAPI Gateway          │ │
│  │  (stdio, AI)      │  │  (HTTP, humans/programs)  │ │
│  └────────┬─────────┘  └────────────┬─────────────┘ │
├───────────┼─────────────────────────┼───────────────┤
│  Client Layer                                        │
│  ┌──────────────────────────────────────────────┐   │
│  │  GitHubClient                                 │   │
│  │  Domain exceptions, data transformation       │   │
│  └──────────────────────┬───────────────────────┘   │
├─────────────────────────┼───────────────────────────┤
│  Infrastructure Layer                                │
│  ┌────────────┐  ┌───────────┐  ┌────────────────┐ │
│  │  Docker     │  │  K8s      │  │  Terraform     │ │
│  │  Compose    │  │  manifests│  │  IaC           │ │
│  └────────────┘  └───────────┘  └────────────────┘ │
├──────────────────────────────────────────────────────┤
│  Automation Layer                                    │
│  ┌──────────────────────────────────────────────┐   │
│  │  GitHub Actions CI/CD                         │   │
│  └──────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────┘
```

### Why four layers?

| Layer | Purpose | Why it exists |
|-------|---------|---------------|
| **Interface** | Protocol translation | Each access pattern (stdio vs HTTP) has different serialization, error reporting, and lifecycle needs. Keeping them as thin adapters means adding a third interface (e.g., gRPC) requires zero changes to business logic. |
| **Client** | Business logic + domain errors | Isolates callers from GitHub API specifics. A `RepositoryNotFoundError` is meaningful; a raw `GithubException(status=404)` is not. |
| **Infrastructure** | Packaging + orchestration | Three deployment options (Compose, kubectl, Terraform) serve different stages: local dev, learning, and production. See [ADR-004](docs/adr/ADR-004-terraform-and-kubectl.md). |
| **Automation** | Build + deploy pipeline | CI validates every change; CD deploys on merge. Keeps the feedback loop fast. |

## Key Decisions

| Decision | ADR | Summary |
|----------|-----|---------|
| Dual MCP + REST interface | [ADR-001](docs/adr/ADR-001-dual-interface.md) | Two protocols serve different consumers without duplicating logic |
| Custom exception hierarchy | [ADR-002](docs/adr/ADR-002-exception-hierarchy.md) | Translate HTTP status codes into semantic domain errors |
| Multi-stage Docker build | [ADR-003](docs/adr/ADR-003-multi-stage-docker.md) | Separate build dependencies from runtime for smaller images |
| Terraform + kubectl coexistence | [ADR-004](docs/adr/ADR-004-terraform-and-kubectl.md) | Different tools for different deployment stages |
| HPA configuration values | [ADR-005](docs/adr/ADR-005-hpa-configuration.md) | Why 2-5 replicas and 70% CPU threshold |

## What This Project Does NOT Do

These omissions are deliberate, not oversights:

| Omission | Reason |
|----------|--------|
| **No database** | This is a stateless proxy. Every request fetches fresh data from GitHub. Adding a DB would obscure the core architecture pattern. |
| **No authentication middleware** | Auth is orthogonal to the architecture being demonstrated. Adding it would distract from the layered design. |
| **No caching (by default)** | Redis is available as an optional Docker Compose profile (`--profile with-cache`) to demonstrate the profiles mechanism, but it is not wired into the application. Caching is a feature concern, not an architecture concern. |
| **No custom metrics** | Prometheus/Grafana would add operational value but zero architectural insight. Listed in the roadmap for future work. |

## Further Reading

- [ADR Index](docs/adr/) — All Architecture Decision Records
- [README.md](README.md) — Quick start and usage
- [CONTRIBUTING.md](CONTRIBUTING.md) — Development workflow
