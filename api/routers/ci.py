from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from api.deps import get_db

router = APIRouter()

_FILTER = """
    w.name NOT LIKE 'pip in %%'
    AND w.name NOT LIKE 'Dependabot%%'
    AND w.status IN ('success', 'failure')
    AND w.duration_s < 86400
"""

@router.get("/stability")
def ci_stability(days: int = 90, db: Session = Depends(get_db)):
    rows = db.execute(text(f"""
        SELECT r.name AS repo,
               COUNT(*) AS total_runs,
               COUNT(*) FILTER (WHERE w.status='success') AS passed,
               COUNT(*) FILTER (WHERE w.status='failure') AS failed,
               ROUND(
                   100.0 * COUNT(*) FILTER (WHERE w.status='success')
                   / NULLIF(COUNT(*) FILTER (WHERE w.status IN ('success','failure')),0), 1
               ) AS pass_rate,
               ROUND((PERCENTILE_CONT(0.5) WITHIN GROUP (
                   ORDER BY w.duration_s) / 60.0)::numeric, 1) AS median_min
        FROM workflow_run w
        JOIN repository r ON r.repo_id = w.repo_id
        WHERE w.started_at >= NOW() - make_interval(days => :days)
          AND {_FILTER}
        GROUP BY r.name
        ORDER BY pass_rate ASC NULLS LAST
    """), {"days": days}).fetchall()
    return [dict(r._mapping) for r in rows]

@router.get("/workflows")
def ci_workflows(repo: str | None = None, days: int = 90,
                 db: Session = Depends(get_db)):
    rows = db.execute(text(f"""
        SELECT r.name AS repo,
               w.name AS workflow,
               COUNT(*) AS total_runs,
               COUNT(*) FILTER (WHERE w.status='success') AS passed,
               COUNT(*) FILTER (WHERE w.status='failure') AS failed,
               ROUND(
                   100.0 * COUNT(*) FILTER (WHERE w.status='success')
                   / NULLIF(COUNT(*) FILTER (WHERE w.status IN ('success','failure')),0), 1
               ) AS pass_rate,
               ROUND((PERCENTILE_CONT(0.5) WITHIN GROUP (
                   ORDER BY w.duration_s) / 60.0)::numeric, 1) AS median_min
        FROM workflow_run w
        JOIN repository r ON r.repo_id = w.repo_id
        WHERE w.started_at >= NOW() - make_interval(days => :days)
          AND {_FILTER}
          AND (:repo IS NULL OR r.name = :repo)
        GROUP BY r.name, w.name
        HAVING COUNT(*) >= 2
        ORDER BY r.name, pass_rate ASC
    """), {"days": days, "repo": repo}).fetchall()
    return [dict(r._mapping) for r in rows]

@router.get("/coverage")
def ci_coverage(db: Session = Depends(get_db)):
    """哪些 repo 有真实 CI，哪些只有 bot runs。"""
    rows = db.execute(text(f"""
        SELECT r.name AS repo,
               COUNT(*) FILTER (WHERE {_FILTER.replace('%%','%')}) AS real_ci_runs,
               COUNT(*) FILTER (WHERE w.name LIKE 'pip in %%') AS bot_runs,
               COUNT(*) AS total_runs
        FROM workflow_run w
        JOIN repository r ON r.repo_id = w.repo_id
        GROUP BY r.name
        ORDER BY real_ci_runs DESC
    """)).fetchall()
    return [dict(r._mapping) for r in rows]
