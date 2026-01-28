# GitHub Analytics MCP Server

A Model Context Protocol (MCP) server for GitHub repository analytics. Provides tools to query repository statistics, commits, contributors, and language breakdowns.

## Features

- **get_repo_stats** - Get repository statistics (stars, forks, issues, watchers)
- **list_recent_commits** - List recent commits with author and message details
- **analyze_contributors** - Analyze top contributors and their contributions
- **get_language_breakdown** - Get programming language distribution

## Prerequisites

- **Python 3.11+**
- **GitHub Personal Access Token** - Required for API authentication
  - Create one at: https://github.com/settings/tokens
  - Required scopes: `repo` (for private repos) or `public_repo` (for public repos only)

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd github-analytics-mcp
   ```

2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and add your GitHub Personal Access Token:
   ```
   GITHUB_TOKEN=your_github_personal_access_token_here
   ```

## Usage

### Running the MCP Server

```bash
# Activate virtual environment (if not already active)
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Run the server
python src/server.py
```

### Testing the Setup

```bash
python test_mcp_server.py
```

### MCP Client Configuration

Add to your MCP client configuration (e.g., Claude Desktop):

```json
{
  "mcpServers": {
    "github-analytics": {
      "command": "python",
      "args": ["src/server.py"],
      "cwd": "/path/to/github-analytics-mcp",
      "env": {
        "GITHUB_TOKEN": "your_token_here"
      }
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

## License

MIT
