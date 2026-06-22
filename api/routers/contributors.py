from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from api.deps import get_db

router = APIRouter()

# Known CI bots and service accounts to exclude
BOT_FILTER = """
    AND c.author NOT IN (
        'rocm-ci', 'Jenkins', 'foreman', 'rocm-devops',
        'dependabot[bot]', 'github-actions[bot]', 'amd-ci'
    )
    AND c.author NOT LIKE '%%[bot]'
    AND c.author NOT LIKE 'AMD\%%'
"""

@router.get("/ranking")
def contributor_ranking(limit: int = 20, db: Session = Depends(get_db)):
    rows = db.execute(text(f"""
        SELECT author,
               COUNT(DISTINCT repo_id) AS repos,
               SUM(commits)            AS commits
        FROM (
            SELECT c.author,
                   c.repo_id,
                   COUNT(*) AS commits
            FROM commit c
            WHERE c.author IS NOT NULL
            {BOT_FILTER}
            GROUP BY c.author, c.repo_id
        ) sub
        GROUP BY author
        ORDER BY commits DESC
        LIMIT :limit
    """), {"limit": limit}).fetchall()
    return [dict(r._mapping) for r in rows]


@router.get("/by-repo")
def contributors_by_repo(repo: str | None = None,
                         limit: int = 30,
                         db: Session = Depends(get_db)):
    rows = db.execute(text(f"""
        SELECT r.name AS repo,
               c.author,
               COUNT(*) AS commits
        FROM commit c
        JOIN repository r ON r.repo_id = c.repo_id
        WHERE c.author IS NOT NULL
          AND (:repo IS NULL OR r.name = :repo)
        {BOT_FILTER}
        GROUP BY r.name, c.author
        ORDER BY r.name, commits DESC
        LIMIT :limit
    """), {"repo": repo, "limit": limit}).fetchall()
    return [dict(r._mapping) for r in rows]


@router.get("/bus-factor")
def bus_factor(db: Session = Depends(get_db)):
    """每个 repo 里 top-3 贡献者占总 commit 的比例，越高风险越大。"""
    rows = db.execute(text(f"""
        WITH repo_total AS (
            SELECT c.repo_id, COUNT(*) AS total
            FROM commit c
            WHERE c.author IS NOT NULL
            {BOT_FILTER}
            GROUP BY c.repo_id
        ),
        ranked AS (
            SELECT c.repo_id,
                   c.author,
                   COUNT(*) AS commits,
                   ROW_NUMBER() OVER (
                       PARTITION BY c.repo_id ORDER BY COUNT(*) DESC
                   ) AS rnk
            FROM commit c
            WHERE c.author IS NOT NULL
            {BOT_FILTER}
            GROUP BY c.repo_id, c.author
        )
        SELECT r.name AS repo,
               rt.total AS total_commits,
               SUM(rk.commits) AS top3_commits,
               ROUND(100.0 * SUM(rk.commits) / rt.total, 1) AS top3_pct
        FROM ranked rk
        JOIN repository r  ON r.repo_id  = rk.repo_id
        JOIN repo_total rt ON rt.repo_id = rk.repo_id
        WHERE rk.rnk <= 3
        GROUP BY r.name, rt.total
        ORDER BY top3_pct DESC
    """)).fetchall()
    return [dict(r._mapping) for r in rows]
