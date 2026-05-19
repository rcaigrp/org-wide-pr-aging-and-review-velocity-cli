
import requests

def fetch_repositories(org, token):
    url = f'https://api.github.com/orgs/{org}/repos'
    headers = {'Authorization': f'token {token}'}
    repos = []
    while url:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        repos.extend(response.json())
        url = response.links.get('next', {}).get('url')
    return repos

def fetch_pull_requests(repo, token):
    url = f'https://api.github.com/repos/{repo}/pulls'
    headers = {'Authorization': f'token {token}'}
    prs = []
    while url:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        prs.extend(response.json())
        url = response.links.get('next', {}).get('url')
    return prs

def fetch_all_org_prs(org, token):
    repositories = fetch_repositories(org, token)
    all_prs = {}
    for repo in repositories:
        repo_full_name = repo['full_name']
        all_prs[repo_full_name] = fetch_pull_requests(repo_full_name, token)
    return all_prs
