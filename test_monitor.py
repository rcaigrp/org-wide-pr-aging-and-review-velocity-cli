import unittest
import responses
import requests
import os
import time
from datetime import datetime, timezone
from monitor import fetch_org_repos, fetch_repo_prs, calculate_days_open, calculate_review_density, fetch_org_data
from unittest.mock import patch

os.environ["GITHUB_TOKEN"] = "mock_token"

class TestMonitor(unittest.TestCase):
    @responses.activate
    def test_fetch_org_repos(self):
        responses.add(
            responses.GET,
            "https://api.github.com/orgs/test-org/repos",
            json=[{"id": 1, "name": "repo1", "owner": {"login": "test-org"}}],
            status=200,
            headers={"X-RateLimit-Remaining": "100"}
        )
        responses.add(
            responses.GET,
            "https://api.github.com/orgs/test-org/repos",
            json=[],
            status=200,
            headers={"X-RateLimit-Remaining": "100"}
        )
        repos = fetch_org_repos("test-org", "mock_token")
        self.assertEqual(len(repos), 1)
        self.assertEqual(repos[0]["name"], "repo1")

    @responses.activate
    def test_fetch_repo_prs(self):
        repo = {"id": 1, "name": "repo1", "owner": {"login": "test-org"}}
        responses.add(
            responses.GET,
            "https://api.github.com/repos/test-org/repo1/pulls",
            json=[{"number": 100, "updated_at": "2023-01-01T00:00:00Z", "user": {"login": "user1"}, "html_url": "http://example.com/100"}],
            status=200,
            headers={"X-RateLimit-Remaining": "100"}
        )
        responses.add(
            responses.GET,
            "https://api.github.com/repos/test-org/repo1/pulls",
            json=[],
            status=200,
            headers={"X-RateLimit-Remaining": "100"}
        )
        prs = fetch_repo_prs(repo, "mock_token")
        self.assertEqual(len(prs), 1)

    @responses.activate
    @patch('monitor.datetime')
    def test_calculate_review_density(self, MockDatetime):
        MockDatetime.now.return_value = datetime.fromisoformat("2023-02-01T00:00:00+00:00")
        pr = {"number": 100, "updated_at": "2023-01-01T00:00:00Z"}
        responses.add(
            responses.GET,
            "https://api.github.com/repos/test-org/repo1/issues/100/comments",
            json=[{"body": "comment1"}],
            status=200,
            headers={"X-RateLimit-Remaining": "100"}
        )
        density = calculate_review_density(pr, "test-org", "repo1", "mock_token")
        # days_open is 31. density = 1 / 31 = 0.032
        self.assertAlmostEqual(density, 1/31, places=2)

    @responses.activate
    def test_rate_limit_backoff(self):
        responses.add(
            responses.GET,
            "https://api.github.com/orgs/test-org/repos",
            json=[],
            status=200,
            headers={"X-RateLimit-Remaining": "5", "X-RateLimit-Reset": str(int(time.time()) + 10)}
        )
        repos = fetch_org_repos("test-org", "mock_token")
        self.assertEqual(repos, [])

    @responses.activate
    def test_empty_org(self):
        responses.add(
            responses.GET,
            "https://api.github.com/orgs/empty-org/repos",
            json=[],
            status=200,
            headers={"X-RateLimit-Remaining": "100"}
        )
        data = fetch_org_data("empty-org", "mock_token", 14)
        self.assertEqual(data, [])

    @responses.activate
    @patch('monitor.datetime')
    def test_stale_filtering(self, MockDatetime):
        MockDatetime.now.return_value = datetime.fromisoformat("2023-02-01T00:00:00+00:00")
        responses.add(
            responses.GET,
            "https://api.github.com/orgs/test-org/repos",
            json=[{"id": 1, "name": "repo1", "owner": {"login": "test-org"}}],
            status=200,
            headers={"X-RateLimit-Remaining": "100"}
        )
        responses.add(
            responses.GET,
            "https://api.github.com/orgs/test-org/repos",
            json=[],
            status=200,
            headers={"X-RateLimit-Remaining": "100"}
        )
        responses.add(
            responses.GET,
            "https://api.github.com/repos/test-org/repo1/pulls",
            json=[
                {"number": 1, "updated_at": "2023-01-01T00:00:00Z", "user": {"login": "user1"}, "html_url": "http://example.com/1"},
                {"number": 2, "updated_at": "2023-01-15T00:00:00Z", "user": {"login": "user2"}, "html_url": "http://example.com/2"}
            ],
            status=200,
            headers={"X-RateLimit-Remaining": "100"}
        )
        responses.add(
            responses.GET,
            "https://api.github.com/repos/test-org/repo1/pulls",
            json=[],
            status=200,
            headers={"X-RateLimit-Remaining": "100"}
        )
        
        responses.add(
            responses.GET,
            "https://api.github.com/repos/test-org/repo1/issues/1/comments",
            json=[],
            status=200,
            headers={"X-RateLimit-Remaining": "100"}
        )
        responses.add(
            responses.GET,
            "https://api.github.com/repos/test-org/repo1/issues/2/comments",
            json=[],
            status=200,
            headers={"X-RateLimit-Remaining": "100"}
        )

        data = fetch_org_data("test-org", "mock_token", 14)
        # PR 1: 31 days open (stale)
        # PR 2: 17 days open (stale)
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["days_open"], 31)
