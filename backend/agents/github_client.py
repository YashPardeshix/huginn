import os
import re
import httpx

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")


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


def _auth_headers() -> dict:
    if not GITHUB_TOKEN:
        raise ValueError("GITHUB_TOKEN is not set — cannot post to GitHub")
    return {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
    }


def post_issue_comment(owner: str, repo: str, issue_number: str, body: str) -> None:
    url = f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}/comments"
    response = httpx.post(url, headers=_auth_headers(), json={"body": body})
    if response.status_code not in (200, 201):
        raise ValueError(f"Failed to post comment: {response.status_code} {response.text}")


def close_issue(owner: str, repo: str, issue_number: str) -> None:
    url = f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}"
    response = httpx.patch(url, headers=_auth_headers(), json={"state": "closed"})
    if response.status_code != 200:
        raise ValueError(f"Failed to close issue: {response.status_code} {response.text}")