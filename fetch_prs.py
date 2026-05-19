import requests

def fetch_org_repos_and_prs(org_name, token):
    headers = {'Authorization': f'token {token}'}
    repos_url = f'https://api.github.com/orgs/{org_name}/repos'
    repos_response = requests.get(repos_url, headers=headers)

    if repos_response.status_code != 200:
        raise Exception('Error fetching repositories.')

    repos = repos_response.json()
    prs_list = []

    for repo in repos:
        repo_name = repo['name']
        prs_url = f'https://api.github.com/repos/{org_name}/{repo_name}/pulls?state=all'
        while prs_url:
            prs_response = requests.get(prs_url, headers=headers)

            if prs_response.status_code != 200:
                raise Exception(f'Error fetching PRs for repo {repo_name}.')

            prs_list.extend(prs_response.json())

            # Handle pagination
            prs_url = prs_response.links.get('next', {}).get('url')

    return prs_list
