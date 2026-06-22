from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from api.deps import get_db

router = APIRouter()

@router.get("/summary")
def issue_summary(db: Session = Depends(get_db)):
    rows = db.execute(text("""
        SELECT r.name AS repo,
               COUNT(*) FILTER (WHERE i.state='open')   AS open,
               COUNT(*) FILTER (WHERE i.state='closed') AS closed,
               ROUND((AVG(i.resolution_hrs) / 24)::numeric, 1) AS avg_resolve_days
        FROM issue i
        JOIN repository r ON r.repo_id = i.repo_id
        GROUP BY r.name ORDER BY open DESC
    """)).fetchall()
    return [dict(r._mapping) for r in rows]

@router.get("/trend")
def issue_trend(days: int = 90, db: Session = Depends(get_db)):
    rows = db.execute(text("""
        SELECT r.name AS repo,
               date_trunc('week', i.created_at)::date AS week,
               COUNT(*) AS opened
        FROM issue i
        JOIN repository r ON r.repo_id = i.repo_id
        WHERE i.created_at >= NOW() - make_interval(days => :days)
        GROUP BY 1,2 ORDER BY 2,1
    """), {"days": days}).fetchall()
    return [{"repo": r.repo, "week": str(r.week), "opened": r.opened} for r in rows]

@router.get("/resolution")
def issue_resolution(db: Session = Depends(get_db)):
    rows = db.execute(text("""
        SELECT
            CASE WHEN 'bug'         = ANY(labels) THEN 'bug'
                 WHEN 'performance' = ANY(labels) THEN 'performance'
                 WHEN 'enhancement' = ANY(labels) THEN 'enhancement'
                 ELSE 'other' END AS label_type,
            ROUND((AVG(resolution_hrs) / 24)::numeric, 1) AS avg_days,
            COUNT(*) AS total
        FROM issue
        WHERE closed_at IS NOT NULL
        GROUP BY 1 ORDER BY avg_days DESC
    """)).fetchall()
    return [dict(r._mapping) for r in rows]
