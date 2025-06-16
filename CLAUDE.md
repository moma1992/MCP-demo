# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

FastMCP is a modern Python MCP (Model Context Protocol) server built with contemporary Python tooling and best practices. The project uses FastMCP framework for rapid MCP server development with optional FastAPI integration.

## Development Commands

### Package Management
- `uv sync` - Install dependencies and sync virtual environment
- `uv add <package>` - Add new dependency
- `uv add --dev <package>` - Add development dependency
- `uv remove <package>` - Remove dependency
- `uv lock` - Update lock file

### Code Quality
- `uv run ruff check` - Run linter
- `uv run ruff format` - Format code
- `uv run ruff check --fix` - Auto-fix linting issues
- `uv run mypy .` - Type checking

### Testing
- `uv run pytest` - Run all tests
- `uv run pytest tests/` - Run specific test directory
- `uv run pytest -v` - Verbose test output
- `uv run pytest --cov` - Run tests with coverage
- `uv run pytest -x` - Stop on first failure

### Development Server
- `uv run python -m fastmcp` - Run MCP server via STDIO
- `uv run python -m fastmcp --http` - Run MCP server via HTTP
- `uv run uvicorn main:app --reload` - Run FastAPI server with auto-reload (if using FastAPI integration)

### Pre-commit Hooks
- `uv run pre-commit install` - Install git hooks
- `uv run pre-commit run --all-files` - Run all hooks manually

## Architecture

### Core Components
- **MCP Server**: Built with FastMCP framework for rapid development
- **Tools**: Decorated functions that expose functionality to MCP clients
- **Resources**: Static or dynamic content accessible to clients
- **Prompts**: Reusable prompt templates

### Project Structure
```
fastmcp/
├── pyproject.toml          # Project configuration and dependencies
├── src/fastmcp/           # Main package
│   ├── __init__.py
│   ├── server.py          # MCP server implementation
│   ├── tools/             # MCP tools modules
│   └── resources/         # MCP resources modules
├── tests/                 # Test suite
├── docs/                  # Documentation
└── scripts/               # Utility scripts
```

### Technology Stack
- **Package Manager**: uv (fast, modern Python package manager)
- **MCP Framework**: FastMCP (Pythonic MCP server framework)
- **Code Quality**: ruff (formatting + linting), mypy (type checking)
- **Testing**: pytest, pytest-cov (coverage)
- **Pre-commit**: Automated code quality checks

### MCP Implementation Patterns

#### Tool Definition
```python
from fastmcp import FastMCP

mcp = FastMCP("MyServer")

@mcp.tool
def my_tool(param: str) -> str:
    """Tool description for MCP client"""
    return f"Result: {param}"
```

#### Resource Definition
```python
@mcp.resource("my-resource")
def my_resource() -> str:
    """Resource description"""
    return "Resource content"
```

#### Server Startup
- STDIO transport: `mcp.run()`
- HTTP transport: `mcp.run(transport="http")`
- FastAPI integration: Mount to existing FastAPI app

## Development Guidelines

### Code Style
- Use ruff for consistent formatting and linting
- Follow PEP 8 naming conventions
- Add type hints to all function signatures
- Write descriptive docstrings for MCP tools and resources

### Testing Strategy
- Write unit tests for all tools and resources
- Use pytest fixtures for common test data
- Mock external dependencies in tests
- Maintain >90% test coverage

### MCP Best Practices
- Keep tool functions focused and single-purpose
- Provide clear descriptions for all MCP components
- Use appropriate error handling and validation
- Follow MCP protocol specifications