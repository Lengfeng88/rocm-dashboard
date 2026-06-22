from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from api.deps import get_db

router = APIRouter()

@router.get("/summary")
def pr_summary(db: Session = Depends(get_db)):
    rows = db.execute(text("""
        SELECT r.name AS repo,
               COUNT(*) FILTER (WHERE p.state='open') AS open,
               COUNT(*) FILTER (WHERE p.merged_at IS NOT NULL) AS merged,
               ROUND((AVG(p.cycle_hours) / 24)::numeric, 1) AS avg_cycle_days
        FROM pull_request p
        JOIN repository r ON r.repo_id = p.repo_id
        GROUP BY r.name ORDER BY open DESC
    """)).fetchall()
    return [dict(r._mapping) for r in rows]

@router.get("/merge-time")
def merge_time(days: int = 30, db: Session = Depends(get_db)):
    rows = db.execute(text("""
        SELECT r.name AS repo,
               ROUND((AVG(p.cycle_hours) / 24)::numeric, 1) AS avg_days,
               COUNT(*) AS total_merged
        FROM pull_request p
        JOIN repository r ON r.repo_id = p.repo_id
        WHERE p.merged_at IS NOT NULL
          AND p.merged_at >= NOW() - make_interval(days => :days)
        GROUP BY r.name ORDER BY avg_days DESC
    """), {"days": days}).fetchall()
    return [dict(r._mapping) for r in rows]

@router.get("/trend")
def pr_trend(days: int = 90, db: Session = Depends(get_db)):
    rows = db.execute(text("""
        SELECT r.name AS repo,
               date_trunc('week', p.created_at)::date AS week,
               COUNT(*) AS opened,
               COUNT(*) FILTER (WHERE p.merged_at IS NOT NULL) AS merged
        FROM pull_request p
        JOIN repository r ON r.repo_id = p.repo_id
        WHERE p.created_at >= NOW() - make_interval(days => :days)
        GROUP BY 1,2 ORDER BY 2,1
    """), {"days": days}).fetchall()
    return [{"repo": r.repo, "week": str(r.week),
             "opened": r.opened, "merged": r.merged} for r in rows]
