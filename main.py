import requests

class GithubAPI:
    BASE_URL = 'https://api.github.com'

    def __init__(self, org, token):
        self.org = org
        self.token = token

    def fetch_repositories(self):
        repos = []
        page = 1
        while True:
            response = requests.get(
                f"{self.BASE_URL}/orgs/{self.org}/repos",
                headers={'Authorization': f'token {self.token}'},
                params={'per_page': 100, 'page': page}
            )
            response.raise_for_status()
            repos_page = response.json()
            if not repos_page:
                break
            repos.extend(repos_page)
            page += 1
        return repos

    def fetch_pull_requests(self, repo_name):
        prs = []
        page = 1
        while True:
            response = requests.get(
                f"{self.BASE_URL}/repos/{self.org}/{repo_name}/pulls",
                headers={'Authorization': f'token {self.token}'},
                params={'per_page': 100, 'page': page}
            )
            response.raise_for_status()
            prs_page = response.json()
            if not prs_page:
                break
            prs.extend(prs_page)
            page += 1
        return prs
