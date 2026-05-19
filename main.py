import requests

def fetch_repos(org, token):
    repos = []
    url = f'https://api.github.com/orgs/{org}/repos'
    headers = {'Authorization': f'token {token}'}
    while url:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        repos.extend(response.json())
        url = response.links.get('next', {}).get('url')
    return repos


def fetch_all_prs(repos, token):
    all_prs = []
    headers = {'Authorization': f'token {token}'}
    for repo in repos:
        url = repo['pulls_url'].replace('{/number}', '')
        while url:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            all_prs.extend(response.json())
            url = response.links.get('next', {}).get('url')
    return all_prs
