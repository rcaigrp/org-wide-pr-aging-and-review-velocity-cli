import time
import requests
from datetime import datetime, timezone
from typing import List, Dict, Optional

BASE_URL = "https://api.github.com"

def fetch_with_rate_limit(url: str, token: str, params: dict = None) -> List[Dict]:
    """Fetch data from URL with pagination and rate limit handling."""
    data = []
    page = 1
    while True:
        params = params or {}
        params["page"] = page
        params["per_page"] = 100
        
        try:
            resp = requests.get(url, headers={"Authorization": f"Bearer {token}"}, params=params)
            resp.raise_for_status()
        except requests.HTTPError as e:
            if e.response.status_code == 403:
                print("Rate limit exceeded or insufficient permissions.")
                break
            elif e.response.status_code == 404:
                print("Resource not found.")
                break
            print(f"HTTP Error: {e}")
            break
            
        remaining = int(resp.headers.get("X-RateLimit-Remaining", 0))
        if remaining < 10:
            reset_time = int(resp.headers.get("X-RateLimit-Reset", 0))
            wait_time = max(0, reset_time - time.time())
            print(f"Rate limit approaching. Waiting {wait_time:.2f} seconds...")
            time.sleep(wait_time)

        chunk = resp.json()
        if not chunk:
            break
        data.extend(chunk)
        page += 1
        
        # If we got fewer than per_page, it's the last page
        if len(chunk) < 100:
            break
            
    return data

def fetch_org_repos(org: str, token: str) -> List[Dict]:
    """Fetch all repos for an organization."""
    url = f"{BASE_URL}/orgs/{org}/repos"
    return fetch_with_rate_limit(url, token, {"per_page": 100})

def fetch_repo_prs(repo: Dict, token: str) -> List[Dict]:
    """Fetch all PRs for a repo."""
    owner = repo.get("owner", {}).get("login", repo.get("owner_login", ""))
    name = repo.get("name")
    if not owner or not name:
        return []
    url = f"{BASE_URL}/repos/{owner}/{name}/pulls"
    return fetch_with_rate_limit(url, token, {"per_page": 100})

def fetch_issue_comments(owner: str, repo: str, pr_number: int, token: str) -> int:
    """Fetch number of comments on a PR's associated issue."""
    url = f"{BASE_URL}/repos/{owner}/{repo}/issues/{pr_number}/comments"
    try:
        resp = requests.get(url, headers={"Authorization": f"Bearer {token}"})
        resp.raise_for_status()
        return len(resp.json())
    except requests.HTTPError:
        return 0

def calculate_days_open(pr: Dict) -> int:
    """Calculate days since PR was last updated."""
    updated_at_str = pr.get("updated_at")
    if not updated_at_str:
        return 0
    try:
        updated_at = datetime.fromisoformat(updated_at_str.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        delta = now - updated_at
        return delta.days
    except ValueError:
        return 0

def calculate_review_density(pr: Dict, owner: str, repo: str, token: str) -> float:
    """Calculate review density = (comments on PR + comments on issue) / days_open."""
    days_open = calculate_days_open(pr)
    if days_open == 0:
        return 0.0
    
    # PRs are Issues in GitHub API, so comments are the same
    pr_comments_url = f"{BASE_URL}/repos/{owner}/{repo}/issues/{pr['number']}/comments"
    try:
        resp = requests.get(pr_comments_url, headers={"Authorization": f"Bearer {token}"})
        resp.raise_for_status()
        pr_comments = len(resp.json())
    except requests.HTTPError:
        pr_comments = 0
        
    return pr_comments / days_open

def fetch_org_data(org: str, token: str, min_days_stale: int = 14) -> List[Dict]:
    """Fetch and filter PRs for an organization."""
    repos = fetch_org_repos(org, token)
    if not repos:
        return []
    
    all_prs = []
    for repo in repos:
        prs = fetch_repo_prs(repo, token)
        owner = repo.get("owner", {}).get("login", repo.get("owner_login", ""))
        name = repo.get("name")
        if not owner or not name:
            continue
            
        for pr in prs:
            days_open = calculate_days_open(pr)
            if days_open >= min_days_stale:
                density = calculate_review_density(pr, owner, name, token)
                all_prs.append({
                    "repo": f"{owner}/{name}",
                    "pr_number": pr.get("number"),
                    "author": pr.get("user", {}).get("login", "unknown"),
                    "days_open": days_open,
                    "review_density": round(density, 2),
                    "link": pr.get("html_url", "")
                })
                
    # Sort by days open descending
    all_prs.sort(key=lambda x: x["days_open"], reverse=True)
    return all_prs
