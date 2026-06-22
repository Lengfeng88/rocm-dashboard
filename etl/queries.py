import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
load_dotenv()

engine = create_engine(os.environ["DATABASE_URL_SYNC"], echo=False)

def get_weekly_kpis() -> dict:
    with engine.connect() as conn:

        issue_summary = conn.execute(text("""
            SELECT r.name AS repo,
                   COUNT(*) FILTER (WHERE i.state='open')   AS open,
                   COUNT(*) FILTER (WHERE i.state='closed') AS closed,
                   ROUND(CAST(AVG(i.resolution_hrs)/24 AS numeric), 1) AS avg_resolve_days
            FROM issue i
            JOIN repository r ON r.repo_id = i.repo_id
            GROUP BY r.name ORDER BY open DESC
        """)).fetchall()

        pr_summary = conn.execute(text("""
            SELECT r.name AS repo,
                   COUNT(*) FILTER (WHERE p.state='open') AS open,
                   COUNT(*) FILTER (WHERE p.merged_at IS NOT NULL) AS merged,
                   ROUND(CAST(AVG(p.cycle_hours)/24 AS numeric), 1) AS avg_cycle_days
            FROM pull_request p
            JOIN repository r ON r.repo_id = p.repo_id
            GROUP BY r.name ORDER BY avg_cycle_days DESC NULLS LAST
        """)).fetchall()

        merge_time = conn.execute(text("""
            SELECT r.name AS repo,
                   ROUND(CAST(AVG(p.cycle_hours)/24 AS numeric), 1) AS avg_days,
                   COUNT(*) AS merged_count
            FROM pull_request p
            JOIN repository r ON r.repo_id = p.repo_id
            WHERE p.merged_at >= NOW() - INTERVAL '30 days'
            GROUP BY r.name ORDER BY avg_days DESC NULLS LAST
        """)).fetchall()

        ci_summary = conn.execute(text("""
            SELECT r.name AS repo,
                   COUNT(*) AS total_runs,
                   COUNT(*) FILTER (WHERE w.status='success') AS passed,
                   ROUND(CAST(100.0 * COUNT(*) FILTER (WHERE w.status='success')
                         / NULLIF(COUNT(*),0) AS numeric), 1) AS pass_rate
            FROM workflow_run w
            JOIN repository r ON r.repo_id = w.repo_id
            WHERE w.started_at >= NOW() - INTERVAL '30 days'
            GROUP BY r.name ORDER BY pass_rate ASC NULLS LAST
        """)).fetchall()

        top_contributors = conn.execute(text("""
            SELECT author, COUNT(*) AS commits
            FROM commit
            WHERE author IS NOT NULL
            GROUP BY author ORDER BY commits DESC LIMIT 5
        """)).fetchall()

        bus_factor = conn.execute(text("""
            SELECT r.name AS repo,
                   ROUND(CAST(100.0 * SUM(top3) / NULLIF(SUM(total),0) AS numeric), 1) AS top3_pct
            FROM (
                SELECT repo_id,
                       commits AS total,
                       CASE WHEN rnk <= 3 THEN commits ELSE 0 END AS top3
                FROM (
                    SELECT repo_id, commits,
                           ROW_NUMBER() OVER (PARTITION BY repo_id ORDER BY commits DESC) AS rnk
                    FROM (
                        SELECT repo_id, author, COUNT(*) AS commits
                        FROM commit WHERE author IS NOT NULL
                        GROUP BY repo_id, author
                    ) sub
                ) ranked
            ) bf
            JOIN repository r ON r.repo_id = bf.repo_id
            GROUP BY r.name ORDER BY top3_pct DESC
        """)).fetchall()

    def rows_to_dicts(rows):
        return [dict(r._mapping) for r in rows]

    return {
        "issue_summary":    rows_to_dicts(issue_summary),
        "pr_summary":       rows_to_dicts(pr_summary),
        "merge_time_30d":   rows_to_dicts(merge_time),
        "ci_summary":       rows_to_dicts(ci_summary),
        "top_contributors": rows_to_dicts(top_contributors),
        "bus_factor":       rows_to_dicts(bus_factor),
    }
