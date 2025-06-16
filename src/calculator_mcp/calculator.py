"""Calculator MCP Server using FastMCP library"""

import os
from typing import Union, Optional, List, Dict, Any
from fastmcp import FastMCP
import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create FastMCP server instance
server = FastMCP("Calculator")


@server.tool(description="Add two numbers together")
def add(a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
    """Add two numbers together"""
    return a + b


@server.tool(description="Get GitHub repository information")
def get_github_repo(owner: str, repo: str) -> Dict[str, Any]:
    """Get information about a GitHub repository"""
    github_token = os.getenv("GITHUB_TOKEN")
    headers = {}
    if github_token:
        headers["Authorization"] = f"token {github_token}"
    
    try:
        with httpx.Client() as client:
            response = client.get(
                f"https://api.github.com/repos/{owner}/{repo}",
                headers=headers
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        return {"error": f"HTTP error occurred: {e}"}
    except Exception as e:
        return {"error": f"An error occurred: {e}"}


@server.tool(description="List GitHub repository issues")
def list_github_issues(owner: str, repo: str, state: str = "open") -> List[Dict[str, Any]]:
    """List issues from a GitHub repository"""
    github_token = os.getenv("GITHUB_TOKEN")
    headers = {}
    if github_token:
        headers["Authorization"] = f"token {github_token}"
    
    try:
        with httpx.Client() as client:
            response = client.get(
                f"https://api.github.com/repos/{owner}/{repo}/issues",
                headers=headers,
                params={"state": state}
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        return [{"error": f"HTTP error occurred: {e}"}]
    except Exception as e:
        return [{"error": f"An error occurred: {e}"}]


@server.tool(description="Create a new GitHub issue")
def create_github_issue(owner: str, repo: str, title: str, body: Optional[str] = None) -> Dict[str, Any]:
    """Create a new issue in a GitHub repository"""
    github_token = os.getenv("GITHUB_TOKEN")
    if not github_token:
        return {"error": "GitHub token is required to create issues"}
    
    headers = {"Authorization": f"token {github_token}"}
    data = {"title": title}
    if body:
        data["body"] = body
    
    try:
        with httpx.Client() as client:
            response = client.post(
                f"https://api.github.com/repos/{owner}/{repo}/issues",
                headers=headers,
                json=data
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        return {"error": f"HTTP error occurred: {e}"}
    except Exception as e:
        return {"error": f"An error occurred: {e}"}


@server.tool(description="List GitHub repository pull requests")
def list_github_prs(owner: str, repo: str, state: str = "open") -> List[Dict[str, Any]]:
    """List pull requests from a GitHub repository"""
    github_token = os.getenv("GITHUB_TOKEN")
    headers = {}
    if github_token:
        headers["Authorization"] = f"token {github_token}"
    
    try:
        with httpx.Client() as client:
            response = client.get(
                f"https://api.github.com/repos/{owner}/{repo}/pulls",
                headers=headers,
                params={"state": state}
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        return [{"error": f"HTTP error occurred: {e}"}]
    except Exception as e:
        return [{"error": f"An error occurred: {e}"}]


def create_calculator_server() -> FastMCP:
    """Create and configure calculator MCP server"""
    return server


def main():
    """Main entry point for the MCP server"""
    server.run()


if __name__ == "__main__":
    main()