# GitHub Analytics MCP Server
# WHY multi-stage: The builder stage installs gcc for C-extension compilation.
# The production stage copies only the compiled packages, keeping the final
# image free of build tools (~100MB smaller, smaller attack surface).
# See docs/adr/ADR-003-multi-stage-docker.md.

FROM python:3.11-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM python:3.11-slim

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /root/.local /root/.local

# Make sure scripts in .local are usable
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Copy application code
COPY src/ ./src/

# Expose port for future API gateway
EXPOSE 8080

# WHY import-based health check: The MCP server uses stdio, not HTTP, so there
# is no TCP port to probe. Verifying that the module imports successfully
# confirms the Python environment and dependencies are intact — without
# requiring curl/wget in the production image.
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import src.server" || exit 1

# Run the MCP server
CMD ["python", "-m", "src.server"]
