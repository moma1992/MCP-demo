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
from .youtube_ai_tools import (
    analyze_success_patterns_tool,
    generate_optimized_titles_tool,
    optimize_posting_schedule_tool,
    suggest_next_content_tool,
)
from .youtube_analytics_tools import (
    analyze_audience_insights_tool,
    compare_video_performance_tool,
    get_channel_analytics_tool,
    get_video_analytics_tool,
)

# Import new YouTube channel management tools
from .youtube_channel_tools import (
    add_video_chapters_tool,
    batch_update_videos_tool,
    generate_buzz_title_tool,
    list_my_videos_tool,
    setup_youtube_oauth_tool,
    update_video_metadata_tool,
)
from .youtube_semantic_tools import create_youtube_semantic_tools
from .youtube_management_tools import create_youtube_management_tools
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
server.tool(description="Update GitHub issue status, title, or body")(
    update_github_issue
)

# Register YouTube tools (original)
server.tool(
    description="Search YouTube videos by keyword and analyze popularity factors"
)(search_youtube_videos)
server.tool(description="Analyze specific YouTube video in detail")(
    analyze_youtube_video
)
server.tool(description="Get trending YouTube videos and analyze trends")(
    get_youtube_trending_analysis
)

# Register YouTube Channel Management tools
server.tool(description="Get list of all videos from your YouTube channel")(
    list_my_videos_tool
)
server.tool(
    description="Update video metadata (title, description, tags) for your YouTube video"
)(update_video_metadata_tool)
server.tool(description="Batch update metadata for multiple YouTube videos at once")(
    batch_update_videos_tool
)
server.tool(
    description="Add chapters (table of contents) to YouTube video description"
)(add_video_chapters_tool)
server.tool(description="Generate buzz-worthy title suggestions for YouTube video")(
    generate_buzz_title_tool
)
server.tool(
    description="Setup YouTube OAuth authentication - shows step-by-step instructions"
)(setup_youtube_oauth_tool)

# Register YouTube Analytics tools
server.tool(description="Get comprehensive analytics for your YouTube channel")(
    get_channel_analytics_tool
)
server.tool(description="Get detailed analytics for specific YouTube video")(
    get_video_analytics_tool
)
server.tool(description="Analyze audience demographics and viewing patterns")(
    analyze_audience_insights_tool
)
server.tool(description="Compare performance metrics between multiple videos")(
    compare_video_performance_tool
)

# Register YouTube AI tools
server.tool(description="Generate AI-optimized titles for better click-through rates")(
    generate_optimized_titles_tool
)
server.tool(
    description="Get AI suggestions for next video content based on trends and performance"
)(suggest_next_content_tool)
server.tool(description="Analyze your channel's success patterns and get recommendations")(
    analyze_success_patterns_tool
)
server.tool(description="Optimize your posting schedule for maximum engagement")(
    optimize_posting_schedule_tool
)

# Register Slack tools
server.tool(description="Send direct messages to multiple Slack users at once")(
    send_slack_bulk_dm
)
server.tool(description="Get list of Slack workspace users")(get_slack_users)
server.tool(description="Send a message to a Slack channel")(send_slack_channel_message)

# Register YouTube Semantic Analysis tools
create_youtube_semantic_tools(server)

# Register YouTube Management and Content Generation tools  
create_youtube_management_tools(server)

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
    "list_my_videos_tool",
    "update_video_metadata_tool",
    "batch_update_videos_tool",
    "add_video_chapters_tool",
    "generate_buzz_title_tool",
    "setup_youtube_oauth_tool",
    "get_channel_analytics_tool",
    "get_video_analytics_tool",
    "analyze_audience_insights_tool",
    "compare_video_performance_tool",
    "generate_optimized_titles_tool",
    "suggest_next_content_tool",
    "analyze_success_patterns_tool",
    "optimize_posting_schedule_tool",
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
