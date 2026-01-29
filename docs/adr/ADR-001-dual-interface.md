# ADR-001: Dual MCP + REST Interface

## Status

Accepted

## Context

This service needs to serve two distinct consumer types:

1. **AI agents** (e.g., Claude Desktop) that communicate over stdio using the Model Context Protocol (MCP). These consumers expect tool-style invocation with JSON arguments and human-readable text responses.
2. **Humans and programs** that communicate over HTTP. These consumers expect RESTful endpoints, proper HTTP status codes, and structured JSON responses.

Both consumers need the same underlying data — repository stats, commits, contributors, and language distribution. The question is how to expose this data without duplicating the business logic.

## Decision

Implement a single `GitHubClient` class that contains all business logic, and create two thin adapter layers:

- `src/server.py` — MCP server that translates MCP tool calls into `GitHubClient` method calls and formats results as text content.
- `api/routes.py` — FastAPI router that translates HTTP requests into `GitHubClient` method calls and formats results as JSON responses with appropriate HTTP status codes.

Neither adapter contains business logic. They only handle:
- Input parsing (MCP arguments vs. HTTP path/query params)
- Error translation (MCP error text vs. HTTP status codes)
- Response formatting (TextContent vs. Pydantic models)

## Consequences

### Positive

- Business logic changes propagate to both interfaces automatically.
- Each interface can evolve independently (e.g., adding pagination to REST without affecting MCP).
- Testing `GitHubClient` in isolation covers the core logic for both interfaces.
- Adding a third interface (gRPC, WebSocket, CLI) requires only a new adapter.

### Negative

- Two deployment targets to maintain (separate Dockerfiles, separate K8s deployments).
- Error handling must be translated twice — once per interface — which introduces a small surface for inconsistency.
- The MCP server currently uses synchronous `GitHubClient` calls wrapped in async handlers, adding minor complexity.

### Neutral

- The MCP protocol is still evolving. If its tool invocation model changes significantly, only `src/server.py` needs updating.
