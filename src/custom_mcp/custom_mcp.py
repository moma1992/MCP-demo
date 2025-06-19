"""Calculator MCP Server using FastMCP library"""

from fastmcp import FastMCP
from dotenv import load_dotenv

# Import tools from separate modules
from .calculator_tools import add
from .github_tools import (
    get_github_repo,
    list_github_issues,
    create_github_issue,
    list_github_prs,
    update_github_issue
)

# Load environment variables
load_dotenv()

# Create FastMCP server instance
server = FastMCP("Custom MCP")

# Register math tools
server.tool(description="Add two numbers together")(add)

# Register GitHub tools
server.tool(description="Get GitHub repository information")(get_github_repo)
server.tool(description="List GitHub repository issues")(list_github_issues)
server.tool(description="Create a new GitHub issue")(create_github_issue)
server.tool(description="List GitHub repository pull requests")(list_github_prs)
server.tool(description="Update GitHub issue status, title, or body")(update_github_issue)

# Make functions available for import (for backward compatibility with tests)
__all__ = [
    "add",
    "get_github_repo", 
    "list_github_issues",
    "create_github_issue",
    "list_github_prs",
    "update_github_issue",
    "server",
    "create_custom_mcp_server",
    "main"
]


def create_custom_mcp_server() -> FastMCP:
    """Create and configure custom MCP server"""
    return server


def main():
    """Main entry point for the MCP server"""
    server.run()


if __name__ == "__main__":
    main()