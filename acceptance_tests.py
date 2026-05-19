import pytest
import responses
from main import fetch_repos, fetch_all_prs

@responses.activate
def test_fetch_repos_and_prs_pagination():
    org = 'test-org'
    token = 'test-token'
    responses.add(responses.GET, f'https://api.github.com/orgs/{org}/repos', json=[{'name': 'repo1', 'pulls_url': 'https://api.github.com/repos/repo1/pulls{/number}'}, {'name': 'repo2', 'pulls_url': 'https://api.github.com/repos/repo2/pulls{/number}'}], status=200)
    responses.add(responses.GET, 'https://api.github.com/repos/repo1/pulls', json=[{'id': 1, 'title': 'PR1'}], status=200)
    responses.add(responses.GET, 'https://api.github.com/repos/repo2/pulls', json=[{'id': 2, 'title': 'PR2'}], status=200)

    repos = fetch_repos(org, token)
    all_prs = fetch_all_prs(repos, token)

    assert len(repos) == 2
    assert len(all_prs) == 2
