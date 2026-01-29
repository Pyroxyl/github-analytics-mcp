# GitHub Analytics MCP Server

[![CI](https://github.com/Pyroxyl/github-analytics-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/Pyroxyl/github-analytics-mcp/actions/workflows/ci.yml)
[![Docker Build](https://github.com/Pyroxyl/github-analytics-mcp/actions/workflows/docker-build.yml/badge.svg)](https://github.com/Pyroxyl/github-analytics-mcp/actions/workflows/docker-build.yml)

A Model Context Protocol (MCP) server for GitHub repository analytics. Provides tools to query repository statistics, commits, contributors, and language breakdowns.

## Features

- **get_repo_stats** - Get repository statistics (stars, forks, issues, watchers)
- **list_recent_commits** - List recent commits with author and message details
- **analyze_contributors** - Analyze top contributors and their contributions
- **get_language_breakdown** - Get programming language distribution

## Prerequisites

- **Python 3.11+** (for local development)
- **Docker** (for containerized deployment)
- **GitHub Personal Access Token** - Required for API authentication
  - Create one at: https://github.com/settings/tokens
  - Required scopes: `repo` (for private repos) or `public_repo` (for public repos only)

## Quick Start with Docker

### 1. Clone and Configure

```bash
git clone https://github.com/Pyroxyl/github-analytics-mcp.git
cd github-analytics-mcp

# Configure environment
cp .env.example .env
# Edit .env and add your GITHUB_TOKEN
```

### 2. Build and Run

```bash
# Build the Docker image
make build

# Start the server
make run

# View logs
make logs
```

### 3. Available Make Commands

| Command | Description |
|---------|-------------|
| `make build` | Build Docker image |
| `make run` | Start the MCP server container |
| `make stop` | Stop all containers |
| `make logs` | View container logs (follow mode) |
| `make shell` | Open a shell in the running container |
| `make clean` | Remove containers, images, and volumes |
| `make rebuild` | Clean rebuild of the image |
| `make status` | Show container status |
| `make help` | Show all available commands |

### Docker Compose (Alternative)

```bash
# Start MCP server only
docker-compose up -d mcp-server

# Start with Redis cache (for future use)
docker-compose --profile with-cache up -d

# Stop all services
docker-compose down
```

## Local Development

### Installation

1. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment variables:
   ```bash
   cp .env.example .env
   # Edit .env and add your GITHUB_TOKEN
   ```

### Running Locally

```bash
# Activate virtual environment
source venv/bin/activate

# Run the server
python -m src.server
```

### Running Tests

```bash
# Run API tests
python test_real_api.py

# Run unit tests
pytest
```

## MCP Client Configuration

Add to your MCP client configuration (e.g., Claude Desktop):

```json
{
  "mcpServers": {
    "github-analytics": {
      "command": "python",
      "args": ["-m", "src.server"],
      "cwd": "/path/to/github-analytics-mcp",
      "env": {
        "GITHUB_TOKEN": "your_token_here"
      }
    }
  }
}
```

### Using Docker with Claude Desktop

```json
{
  "mcpServers": {
    "github-analytics": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "--env-file", ".env", "github-analytics-mcp"],
      "cwd": "/path/to/github-analytics-mcp"
    }
  }
}
```

## Available Tools

| Tool | Description |
|------|-------------|
| `get_repo_stats` | Get repository statistics including stars, forks, open issues, and watchers |
| `list_recent_commits` | List recent commits with SHA, author, message, and timestamp |
| `analyze_contributors` | Get top contributors with contribution counts |
| `get_language_breakdown` | Get programming language distribution as percentages |

## CI/CD Pipeline

```
Push/PR → [CI] → Lint + Test
Push to main → [Docker Build] → ghcr.io → [CD] → Kubernetes
```

- **CI**: Runs ruff lint + pytest on every push/PR (Python 3.11 & 3.12)
- **Docker Build**: Builds and pushes images to GitHub Container Registry
- **CD**: Deploys to Kubernetes via Terraform after successful build

See [`.github/workflows/README.md`](.github/workflows/README.md) for details.

## Project Structure

```
github-analytics-mcp/
├── src/
│   ├── __init__.py
│   ├── server.py          # MCP server entry point
│   ├── github_client.py   # GitHub API client
│   └── tools/             # MCP tool implementations
├── tests/                 # Unit tests
├── k8s/                   # Kubernetes manifests
├── terraform/             # Terraform IaC configuration
├── .github/workflows/     # CI/CD pipelines
├── Dockerfile             # Container definition
├── docker-compose.yml     # Multi-service orchestration
├── Makefile               # Build automation
├── requirements.txt       # Python dependencies
└── .env.example           # Environment template
```

## License

MIT
