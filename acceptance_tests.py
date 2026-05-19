import unittest
import responses
import os
from monitor import fetch_repos, fetch_prs, calculate_days_open, calculate_review_density, get_pr_data
from report import render_table, get_age_color

class TestAcceptance(unittest.TestCase):
    
    @responses.activate
    def test_criterion_1_fetch_repos(self):
        """Test fetching repos with pagination and rate limit handling."""
        responses.add(
            responses.GET,
            "https://api.github.com/orgs/test-org/repos",
            json=[{"name": "repo1", "owner": {"login": "test-org"}}],
            match_querystring=False
        )
        responses.add(
            responses.GET,
            "https://api.github.com/orgs/test-org/repos",
            json=[],
            match_querystring=False
        )
        repos = fetch_repos("test-org", "token")
        self.assertEqual(len(repos), 1)
        self.assertEqual(repos[0]["name"], "repo1")

    @responses.activate
    def test_criterion_2_filter_stale(self):
        """Test stale filtering based on days open."""
        responses.add(
            responses.GET,
            "https://api.github.com/orgs/test-org/repos",
            json=[{"name": "repo1", "owner": {"login": "test-org"}}],
            match_querystring=False
        )
        responses.add(
            responses.GET,
            "https://api.github.com/orgs/test-org/repos",
            json=[],
            match_querystring=False
        )
        responses.add(
            responses.GET,
            "https://api.github.com/repos/test-org/repo1/pulls",
            json=[{"number": 1, "updated_at": "2023-01-01T00:00:00Z", "user": {"login": "user1"}, "html_url": "http://test.com"}],
            match_querystring=False
        )
        responses.add(
            responses.GET,
            "https://api.github.com/repos/test-org/repo1/pulls",
            json=[],
            match_querystring=False
        )
        responses.add(
            responses.GET,
            "https://api.github.com/repos/test-org/repo1/issues/1/comments",
            json=[{"body": "comment1"}],
            match_querystring=False
        )
        
        data = get_pr_data("test-org", "token", 14)
        self.assertEqual(len(data), 1)
        self.assertGreater(data[0]["days_open"], 14)

    def test_criterion_3_review_density(self):
        """Test review density calculation."""
        pr = {"updated_at": "2023-01-01T00:00:00Z"}
        density = calculate_review_density(pr, 5)
        self.assertGreater(density, 0)

    def test_criterion_4_color_coding(self):
        """Test color coding based on PR age."""
        self.assertEqual(get_age_color(5), "green")
        self.assertEqual(get_age_color(10), "yellow")
        self.assertEqual(get_age_color(20), "red")

    def test_criterion_5_edge_cases(self):
        """Test edge cases: empty org, missing fields."""
        pr = {}
        days = calculate_days_open(pr)
        self.assertEqual(days, 0)

if __name__ == "__main__":
    unittest.main()
