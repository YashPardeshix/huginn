import re
import httpx

def parse_github_url(url: str) -> tuple[str, str, str]:
    match = re.search(r"github\.com/([^/]+)/([^/]+)/issues/(\d+)", url)
    if not match:
        raise ValueError("Not a valid GitHub issue URL")
    owner, repo, issue_number = match.groups()
    return owner, repo, issue_number


def fetch_github_issue(owner: str, repo: str, issue_number: str) -> str:
    url = f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}"
    response = httpx.get(url)
    
    if response.status_code != 200:
        raise ValueError(f"Could not fetch issue: {response.status_code}")
    
    data = response.json()
    title = data["title"]
    body = data["body"] or ""
    
    return f"Title: {title}\n\n{body}"