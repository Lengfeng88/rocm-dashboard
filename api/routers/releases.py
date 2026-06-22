from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from api.deps import get_db

router = APIRouter()

@router.get("/pr-velocity")
def pr_velocity(db: Session = Depends(get_db)):
    rows = db.execute(text("""
        SELECT r.name AS repo,
               date_trunc('month', p.merged_at)::date AS month,
               COUNT(*) AS merged_prs,
               ROUND((AVG(p.cycle_hours) / 24)::numeric, 1) AS avg_days
        FROM pull_request p
        JOIN repository r ON r.repo_id = p.repo_id
        WHERE p.merged_at IS NOT NULL
          AND p.merged_at >= NOW() - INTERVAL '6 months'
        GROUP BY 1,2 ORDER BY 2 DESC,1
    """)).fetchall()
    return [{"repo": r.repo, "month": str(r.month),
             "merged_prs": r.merged_prs, "avg_days": r.avg_days} for r in rows]
