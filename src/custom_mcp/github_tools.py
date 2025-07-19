"""GitHub integration tools for repository operations"""

import os
from typing import Any

import httpx


def get_github_repo(owner: str, repo: str) -> dict[str, Any]:
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


def list_github_issues(owner: str, repo: str, state: str = "open") -> list[dict[str, Any]]:
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


def create_github_issue(owner: str, repo: str, title: str, body: str | None = None) -> dict[str, Any]:
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


def list_github_prs(owner: str, repo: str, state: str = "open") -> list[dict[str, Any]]:
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


def update_github_issue(owner: str, repo: str, issue_number: int, state: str | None = None,
                       title: str | None = None, body: str | None = None) -> dict[str, Any]:
    """Update a GitHub issue (state, title, or body)"""
    github_token = os.getenv("GITHUB_TOKEN")
    if not github_token:
        return {"error": "GitHub token is required to update issues"}

    headers = {"Authorization": f"token {github_token}"}
    data = {}

    if state:
        if state not in ["open", "closed"]:
            return {"error": "state must be either 'open' or 'closed'"}
        data["state"] = state

    if title:
        data["title"] = title

    if body:
        data["body"] = body

    if not data:
        return {"error": "At least one field (state, title, or body) must be provided"}

    try:
        with httpx.Client() as client:
            response = client.patch(
                f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}",
                headers=headers,
                json=data
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        return {"error": f"HTTP error occurred: {e}"}
    except Exception as e:
        return {"error": f"An error occurred: {e}"}
