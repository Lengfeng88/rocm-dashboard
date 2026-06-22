import httpx, asyncio, os
from datetime import datetime, timezone
from dotenv import load_dotenv
load_dotenv()

REPOS = [
    "ROCm/HIP", "ROCm/rocBLAS", "ROCm/rccl",
    "ROCm/MIOpen", "ROCm/rocFFT", "ROCm/rocSPARSE"
]
HEADERS = {
    "Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}",
    "Accept": "application/vnd.github.v3+json"
}

async def check_rate_limit(client):
    r = await client.get("https://api.github.com/rate_limit", headers=HEADERS)
    data = r.json()["rate"]
    if data["remaining"] < 100:
        wait = max(0, data["reset"] - datetime.now(timezone.utc).timestamp()) + 5
        print(f"  Rate limit low ({data['remaining']}), sleeping {int(wait)}s ...")
        await asyncio.sleep(wait)

async def paginate(client, url, params=None):
    results, page = [], 1
    params = params or {}
    while True:
        await check_rate_limit(client)
        r = await client.get(url, headers=HEADERS,
                             params={**params, "per_page": 100, "page": page})
        r.raise_for_status()
        data = r.json()
        if not data:
            break
        results.extend(data)
        page += 1
        await asyncio.sleep(0.5)
    return results

async def fetch_issues(repo):
    async with httpx.AsyncClient(timeout=30) as client:
        raw = await paginate(client,
            f"https://api.github.com/repos/{repo}/issues",
            {"state": "all", "filter": "all"})
        return [d for d in raw if "pull_request" not in d]

async def fetch_prs(repo):
    async with httpx.AsyncClient(timeout=30) as client:
        return await paginate(client,
            f"https://api.github.com/repos/{repo}/pulls",
            {"state": "all"})

async def fetch_commits(repo):
    async with httpx.AsyncClient(timeout=30) as client:
        return await paginate(client,
            f"https://api.github.com/repos/{repo}/commits", {})

async def fetch_workflow_runs(repo):
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.get(
            f"https://api.github.com/repos/{repo}/actions/runs",
            headers=HEADERS, params={"per_page": 100})
        r.raise_for_status()
        return r.json().get("workflow_runs", [])

async def fetch_repo_meta(repo):
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.get(
            f"https://api.github.com/repos/{repo}", headers=HEADERS)
        r.raise_for_status()
        return r.json()
