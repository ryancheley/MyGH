"""Extended tests for GitHub API client to improve coverage."""

from unittest.mock import patch

import httpx
import pytest
import respx

from mygh.api.client import GitHubClient
from mygh.exceptions import APIError


class TestGitHubClientValidationErrors:
    """Test GitHub API client validation error handling."""

    @pytest.fixture
    def client(self):
        """Create a test client."""
        return GitHubClient(token="test_token")

    @pytest.mark.api_mock
    @respx.mock
    async def test_get_starred_repos_validation_error(self, client):
        """Test get_starred_repos with validation error (line 178-179)."""
        # Mock API response with invalid data that will cause ValidationError
        respx.get("https://api.github.com/user/starred").mock(
            return_value=httpx.Response(
                200,
                json=[
                    {
                        "id": "invalid_id",  # Should be int, not string
                        "name": "test-repo",
                        # Missing required fields to trigger ValidationError
                    }
                ],
            )
        )

        with pytest.raises(APIError, match="Invalid repository data"):
            await client.get_starred_repos()

    @pytest.mark.api_mock
    @respx.mock
    async def test_get_user_repos_validation_error(self, client):
        """Test get_user_repos with validation error (line 213-214)."""
        # Mock API response with invalid data
        respx.get("https://api.github.com/user/repos").mock(
            return_value=httpx.Response(
                200,
                json=[
                    {
                        "id": "invalid_id",  # Should be int, not string
                        "name": "test-repo",
                        # Missing required fields to trigger ValidationError
                    }
                ],
            )
        )

        with pytest.raises(APIError, match="Invalid repository data"):
            await client.get_user_repos()

    @pytest.mark.api_mock
    @respx.mock
    async def test_get_user_gists_validation_error(self, client):
        """Test get_user_gists with validation error (line 239-240)."""
        # Mock API response with invalid data
        respx.get("https://api.github.com/gists").mock(
            return_value=httpx.Response(
                200,
                json=[
                    {
                        "id": "invalid_id",
                        # Should be string but let's trigger another validation error
                        "description": 123,  # Should be string, not int
                        # Missing required fields
                    }
                ],
            )
        )

        with pytest.raises(APIError, match="Invalid gist data"):
            await client.get_user_gists()

    @pytest.mark.api_mock
    @respx.mock
    async def test_get_repo_issues_validation_error(self, client):
        """Test get_repo_issues with validation error (line 282-283)."""
        # Mock API response with invalid data
        respx.get("https://api.github.com/repos/owner/repo/issues").mock(
            return_value=httpx.Response(
                200,
                json=[
                    {
                        "id": "invalid_id",  # Should be int, not string
                        "number": "invalid_number",  # Should be int, not string
                        # Missing required fields
                    }
                ],
            )
        )

        with pytest.raises(APIError, match="Invalid issue data"):
            await client.get_repo_issues("owner", "repo")

    @pytest.mark.api_mock
    async def test_search_repositories_validation_error(self, client):
        """Test search_repositories with validation error."""
        with patch.object(client, "_request") as mock_request:
            # Mock invalid response data that will cause ValidationError
            mock_request.return_value = {
                "total_count": 1,
                "incomplete_results": False,
                "items": [
                    {
                        "id": "invalid_id",  # Should be int, not string
                        "name": "test-repo",
                        # Missing required fields
                    }
                ],
            }

            with pytest.raises(APIError, match="Invalid search result data"):
                await client.search_repositories("test")


class TestGitHubClientHttpxErrors:
    """Test httpx specific error handling."""

    @pytest.fixture
    def client(self):
        """Create a test client."""
        return GitHubClient(token="test_token")

    @pytest.mark.api_mock
    async def test_request_httpx_timeout_error(self, client):
        """Test request with httpx timeout error."""
        with patch.object(client.client, "request") as mock_request:
            mock_request.side_effect = httpx.TimeoutException("Request timed out")

            with pytest.raises(APIError, match="Request failed"):
                await client._request("GET", "/test")

    @pytest.mark.api_mock
    async def test_request_httpx_connect_error(self, client):
        """Test request with httpx connection error."""
        with patch.object(client.client, "request") as mock_request:
            mock_request.side_effect = httpx.ConnectError("Connection failed")

            with pytest.raises(APIError, match="Request failed"):
                await client._request("GET", "/test")

    @pytest.mark.api_mock
    async def test_request_httpx_read_error(self, client):
        """Test request with httpx read error."""
        with patch.object(client.client, "request") as mock_request:
            mock_request.side_effect = httpx.ReadError("Read failed")

            with pytest.raises(APIError, match="Request failed"):
                await client._request("GET", "/test")
