import asyncio, sys, os
sys.path.insert(0, os.path.abspath("."))

from collectors.rest_collector import (
    REPOS, fetch_repo_meta, fetch_issues,
    fetch_prs, fetch_commits, fetch_workflow_runs
)
from etl.transformer import (
    transform_repo, transform_issues, transform_prs,
    transform_commits, transform_workflow_runs
)
from etl.loader import (
    upsert_repo, upsert_issues, upsert_prs,
    upsert_commits, upsert_workflow_runs
)

async def collect_one(repo):
    print(f"\n{'='*50}\n  {repo}\n{'='*50}")

    print("  [1/5] repo meta ...")
    meta    = await fetch_repo_meta(repo)
    repo_id = upsert_repo(transform_repo(meta))
    print(f"        repo_id = {repo_id}")

    print("  [2/5] issues ...")
    issues = await fetch_issues(repo)
    upsert_issues(transform_issues(issues, repo_id))
    print(f"        {len(issues)} issues saved")

    print("  [3/5] pull requests ...")
    prs = await fetch_prs(repo)
    upsert_prs(transform_prs(prs, repo_id))
    print(f"        {len(prs)} PRs saved")

    print("  [4/5] commits ...")
    commits = await fetch_commits(repo)
    upsert_commits(transform_commits(commits, repo_id))
    print(f"        {len(commits)} commits saved")

    print("  [5/5] workflow runs ...")
    runs = await fetch_workflow_runs(repo)
    upsert_workflow_runs(transform_workflow_runs(runs, repo_id))
    print(f"        {len(runs)} runs saved")

async def main():
    repos = sys.argv[1:] if len(sys.argv) > 1 else REPOS
    for repo in repos:
        try:
            await collect_one(repo)
        except Exception as e:
            print(f"  ERROR on {repo}: {e}")
            import traceback; traceback.print_exc()
    print("\nAll done.")

if __name__ == "__main__":
    asyncio.run(main())
