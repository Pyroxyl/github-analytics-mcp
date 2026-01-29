# ADR-003: Multi-Stage Docker Build

## Status

Accepted

## Context

The application depends on Python packages that require C compilation during installation (e.g., packages with C extensions). A naive single-stage Dockerfile would include `gcc` and other build tools in the final image, increasing its size and attack surface.

Additionally, the MCP server image needs to be as small as possible since it may run on developer machines alongside other containers.

## Decision

Use a two-stage Docker build:

**Stage 1 (builder):**
- Base: `python:3.11-slim`
- Installs `gcc` and build dependencies
- Runs `pip install --user` to install packages into `/root/.local`

**Stage 2 (production):**
- Base: `python:3.11-slim` (fresh, no build tools)
- Copies only `/root/.local` from the builder stage
- Copies application source code
- Uses an import-based health check (`python -c "import src.server"`) instead of curl/wget to avoid installing additional tools

## Consequences

### Positive

- Final image contains no compiler toolchain — smaller size, reduced attack surface.
- `--user` install keeps packages in a single directory, making the `COPY --from=builder` clean.
- Import-based health check avoids adding `curl` or `wget` to the production image.
- Build cache is effective: changing application code does not re-trigger `pip install`.

### Negative

- The health check only verifies that the module can be imported, not that the server is actually accepting connections. This is acceptable for the MCP server (stdio-based, no TCP listener) but would be insufficient for an HTTP server.
- Two-stage builds increase Dockerfile complexity slightly.

### Neutral

- The API gateway (`api/Dockerfile`) follows the same pattern for consistency.
- `PYTHONUNBUFFERED=1` ensures logs appear immediately in `docker logs` — important for debugging stdio-based servers that don't flush stdout by default.
