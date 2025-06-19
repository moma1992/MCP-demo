"""Test cases for GitHub tools using FastMCP library"""

import sys
import os
import pytest
import httpx
from unittest.mock import patch
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from custom_mcp.github_tools import (
    get_github_repo,
    list_github_issues,
    create_github_issue,
    list_github_prs,
    update_github_issue
)


class TestGitHubTools:
    """Test suite for GitHub tools functionality"""

    @pytest.fixture
    def mock_repo_response(self):
        """Mock GitHub repository response"""
        return {
            "id": 123456,
            "name": "test-repo",
            "full_name": "testuser/test-repo",
            "description": "A test repository",
            "private": False,
            "html_url": "https://github.com/testuser/test-repo",
            "stargazers_count": 42,
            "forks_count": 7
        }

    @pytest.fixture
    def mock_issue_response(self):
        """Mock GitHub issue response"""
        return {
            "id": 789,
            "number": 1,
            "title": "Test Issue",
            "body": "This is a test issue",
            "state": "open",
            "html_url": "https://github.com/testuser/test-repo/issues/1",
            "user": {"login": "testuser"}
        }

    @pytest.fixture
    def mock_pr_response(self):
        """Mock GitHub pull request response"""
        return {
            "id": 101112,
            "number": 2,
            "title": "Test PR",
            "body": "This is a test PR",
            "state": "open",
            "html_url": "https://github.com/testuser/test-repo/pull/2",
            "user": {"login": "testuser"}
        }

    def test_get_github_repo_success(self, httpx_mock, mock_repo_response):
        """Test successful repository retrieval"""
        httpx_mock.add_response(
            method="GET",
            url="https://api.github.com/repos/testuser/test-repo",
            json=mock_repo_response
        )
        
        result = get_github_repo("testuser", "test-repo")
        
        assert result["name"] == "test-repo"
        assert result["full_name"] == "testuser/test-repo"
        assert result["stargazers_count"] == 42

    def test_get_github_repo_with_token(self, httpx_mock, mock_repo_response):
        """Test repository retrieval with GitHub token"""
        with patch.dict(os.environ, {"GITHUB_TOKEN": "test_token"}):
            httpx_mock.add_response(
                method="GET",
                url="https://api.github.com/repos/testuser/test-repo",
                json=mock_repo_response,
                match_headers={"Authorization": "token test_token"}
            )
            
            result = get_github_repo("testuser", "test-repo")
            
            assert result["name"] == "test-repo"

    def test_get_github_repo_error(self, httpx_mock):
        """Test repository retrieval error handling"""
        httpx_mock.add_response(
            method="GET",
            url="https://api.github.com/repos/testuser/nonexistent",
            status_code=404
        )
        
        result = get_github_repo("testuser", "nonexistent")
        
        assert "error" in result
        assert "HTTP error occurred" in result["error"]

    def test_list_github_issues_success(self, httpx_mock, mock_issue_response):
        """Test successful issues listing"""
        httpx_mock.add_response(
            method="GET",
            url="https://api.github.com/repos/testuser/test-repo/issues?state=open",
            json=[mock_issue_response]
        )
        
        result = list_github_issues("testuser", "test-repo")
        
        assert len(result) == 1
        assert result[0]["title"] == "Test Issue"
        assert result[0]["state"] == "open"

    def test_list_github_issues_with_state(self, httpx_mock, mock_issue_response):
        """Test issues listing with specific state"""
        closed_issue = mock_issue_response.copy()
        closed_issue["state"] = "closed"
        
        httpx_mock.add_response(
            method="GET",
            url="https://api.github.com/repos/testuser/test-repo/issues?state=closed",
            json=[closed_issue]
        )
        
        result = list_github_issues("testuser", "test-repo", "closed")
        
        assert len(result) == 1
        assert result[0]["state"] == "closed"

    def test_create_github_issue_success(self, httpx_mock, mock_issue_response):
        """Test successful issue creation"""
        with patch.dict(os.environ, {"GITHUB_TOKEN": "test_token"}):
            httpx_mock.add_response(
                method="POST",
                url="https://api.github.com/repos/testuser/test-repo/issues",
                json=mock_issue_response,
                match_headers={"Authorization": "token test_token"}
            )
            
            result = create_github_issue("testuser", "test-repo", "Test Issue", "Test body")
            
            assert result["title"] == "Test Issue"
            assert result["number"] == 1

    def test_create_github_issue_no_token(self):
        """Test issue creation without token"""
        with patch.dict(os.environ, {}, clear=True):
            result = create_github_issue("testuser", "test-repo", "Test Issue")
            
            assert "error" in result
            assert "GitHub token is required" in result["error"]

    def test_list_github_prs_success(self, httpx_mock, mock_pr_response):
        """Test successful pull requests listing"""
        httpx_mock.add_response(
            method="GET",
            url="https://api.github.com/repos/testuser/test-repo/pulls?state=open",
            json=[mock_pr_response]
        )
        
        result = list_github_prs("testuser", "test-repo")
        
        assert len(result) == 1
        assert result[0]["title"] == "Test PR"
        assert result[0]["number"] == 2

    def test_update_github_issue_success(self, httpx_mock, mock_issue_response):
        """Test successful issue update"""
        updated_issue = mock_issue_response.copy()
        updated_issue["state"] = "closed"
        
        with patch.dict(os.environ, {"GITHUB_TOKEN": "test_token"}):
            httpx_mock.add_response(
                method="PATCH",
                url="https://api.github.com/repos/testuser/test-repo/issues/1",
                json=updated_issue,
                match_headers={"Authorization": "token test_token"}
            )
            
            result = update_github_issue("testuser", "test-repo", 1, state="closed")
            
            assert result["state"] == "closed"
            assert result["number"] == 1

    def test_update_github_issue_no_token(self):
        """Test issue update without token"""
        with patch.dict(os.environ, {}, clear=True):
            result = update_github_issue("testuser", "test-repo", 1, state="closed")
            
            assert "error" in result
            assert "GitHub token is required" in result["error"]

    def test_update_github_issue_invalid_state(self):
        """Test issue update with invalid state"""
        with patch.dict(os.environ, {"GITHUB_TOKEN": "test_token"}):
            result = update_github_issue("testuser", "test-repo", 1, state="invalid")
            
            assert "error" in result
            assert "state must be either 'open' or 'closed'" in result["error"]

    def test_update_github_issue_no_fields(self):
        """Test issue update with no fields provided"""
        with patch.dict(os.environ, {"GITHUB_TOKEN": "test_token"}):
            result = update_github_issue("testuser", "test-repo", 1)
            
            assert "error" in result
            assert "At least one field" in result["error"]

    def test_update_github_issue_multiple_fields(self, httpx_mock, mock_issue_response):
        """Test issue update with multiple fields"""
        updated_issue = mock_issue_response.copy()
        updated_issue.update({
            "title": "Updated Title",
            "body": "Updated body",
            "state": "closed"
        })
        
        with patch.dict(os.environ, {"GITHUB_TOKEN": "test_token"}):
            httpx_mock.add_response(
                method="PATCH",
                url="https://api.github.com/repos/testuser/test-repo/issues/1",
                json=updated_issue,
                match_headers={"Authorization": "token test_token"}
            )
            
            result = update_github_issue(
                "testuser", "test-repo", 1,
                state="closed",
                title="Updated Title",
                body="Updated body"
            )
            
            assert result["state"] == "closed"
            assert result["title"] == "Updated Title"
            assert result["body"] == "Updated body"