"""Calculator MCP Server using FastMCP library"""

from dotenv import load_dotenv
from fastmcp import FastMCP

# Import tools from separate modules
from .calculator_tools import add
from .github_tools import (
    create_github_issue,
    get_github_repo,
    list_github_issues,
    list_github_prs,
    update_github_issue,
)
from .slack_tools import (
    get_slack_users,
    send_slack_bulk_dm,
    send_slack_channel_message,
)
from .youtube_tools import (
    analyze_youtube_video,
    get_youtube_trending_analysis,
    search_youtube_videos,
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

# Register YouTube tools
server.tool(description="Search YouTube videos by keyword and analyze popularity factors")(search_youtube_videos)
server.tool(description="Analyze specific YouTube video in detail")(analyze_youtube_video)
server.tool(description="Get trending YouTube videos and analyze trends")(get_youtube_trending_analysis)

# Register Slack tools
server.tool(description="Send direct messages to multiple Slack users at once")(send_slack_bulk_dm)
server.tool(description="Get list of Slack workspace users")(get_slack_users)
server.tool(description="Send a message to a Slack channel")(send_slack_channel_message)

# Make functions available for import (for backward compatibility with tests)
__all__ = [
    "add",
    "get_github_repo",
    "list_github_issues",
    "create_github_issue",
    "list_github_prs",
    "update_github_issue",
    "search_youtube_videos",
    "analyze_youtube_video",
    "get_youtube_trending_analysis",
    "send_slack_bulk_dm",
    "get_slack_users",
    "send_slack_channel_message",
    "server",
    "create_custom_mcp_server",
    "main"
]


def create_custom_mcp_server() -> FastMCP:
    """Create and configure custom MCP server"""
    return server


def main():
    """Main entry point for the MCP server"""
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--stdio":
        server.run(transport="stdio")
    else:
        server.run(transport="stdio")  # デフォルトでSTDIOを使用


if __name__ == "__main__":
    main()
