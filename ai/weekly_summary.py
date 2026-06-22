import os, json
from datetime import datetime
from openai import OpenAI
from sqlalchemy import text
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.environ["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com",
)

# 复用 api/deps.py 的 engine
from api.deps import engine


def fetch_kpis() -> dict:
    with engine.connect() as conn:
        issues = conn.execute(text("""
            SELECT r.name AS repo,
                   COUNT(*) FILTER (WHERE i.state='open')   AS open,
                   COUNT(*) FILTER (WHERE i.state='closed') AS closed,
                   ROUND((AVG(i.resolution_hrs)/24)::numeric,1) AS avg_resolve_days
            FROM issue i JOIN repository r ON r.repo_id=i.repo_id
            GROUP BY r.name ORDER BY open DESC
        """)).fetchall()

        prs = conn.execute(text("""
            SELECT r.name AS repo,
                   COUNT(*) FILTER (WHERE p.state='open') AS open,
                   COUNT(*) FILTER (WHERE p.merged_at IS NOT NULL) AS merged,
                   ROUND((AVG(p.cycle_hours)/24)::numeric,1) AS avg_cycle_days
            FROM pull_request p JOIN repository r ON r.repo_id=p.repo_id
            GROUP BY r.name ORDER BY open DESC
        """)).fetchall()

        ci = conn.execute(text("""
            SELECT r.name AS repo,
                   COUNT(*) AS total_runs,
                   COUNT(*) FILTER (WHERE w.status='success') AS passed,
                   ROUND(100.0 * COUNT(*) FILTER (WHERE w.status='success')
                         / NULLIF(COUNT(*) FILTER (WHERE w.status IN ('success','failure')),0),1) AS pass_rate
            FROM workflow_run w JOIN repository r ON r.repo_id=w.repo_id
            WHERE w.status IN ('success','failure')
              AND w.name NOT LIKE 'pip in %%'
              AND w.duration_s BETWEEN 60 AND 7200
            GROUP BY r.name
        """)).fetchall()

        bus = conn.execute(text("""
            WITH repo_total AS (
                SELECT repo_id, COUNT(*) AS total FROM commit GROUP BY repo_id
            ),
            ranked AS (
                SELECT repo_id, author, COUNT(*) AS commits,
                       ROW_NUMBER() OVER (PARTITION BY repo_id ORDER BY COUNT(*) DESC) AS rnk
                FROM commit
                WHERE author NOT IN ('rocm-ci','Jenkins','foreman','rocm-devops')
                  AND author NOT LIKE '%%[bot]'
                GROUP BY repo_id, author
            )
            SELECT r.name AS repo,
                   ROUND(100.0*SUM(rk.commits)/rt.total,1) AS top3_pct
            FROM ranked rk
            JOIN repository r  ON r.repo_id=rk.repo_id
            JOIN repo_total rt ON rt.repo_id=rk.repo_id
            WHERE rk.rnk <= 3
            GROUP BY r.name, rt.total ORDER BY top3_pct DESC
        """)).fetchall()

    return {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "issues":     [dict(r._mapping) for r in issues],
        "prs":        [dict(r._mapping) for r in prs],
        "ci":         [dict(r._mapping) for r in ci],
        "bus_factor": [dict(r._mapping) for r in bus],
    }


SYSTEM = """You are a senior engineering program manager at AMD analyzing ROCm open-source libraries.
Write clear, concise weekly engineering health reports for technical leads.
Always cite exact numbers. Never invent data. Output Markdown."""

PROMPT = """Here is this week's KPI data for ROCm GitHub repositories:

{kpi_json}

Write a weekly engineering health report with exactly these sections:

## Executive Summary
2-3 sentences on overall health.

## Key Findings
Bullet points per repo. Cite specific numbers.

## Risk Flags 🚨
Top 2-3 risks with data.

## Recommendations
Concrete actions. Name specific repos/teams.

## Positive Signals ✅
1-2 things going well.

Under 500 words. Be direct and analytical."""


def generate_weekly_summary() -> str:
    kpis = fetch_kpis()
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user",   "content": PROMPT.format(kpi_json=json.dumps(kpis, indent=2, default=str))},
        ],
        max_tokens=800,
        temperature=0.3,
    )
    return response.choices[0].message.content


if __name__ == "__main__":
    print("Generating weekly summary...\n")
    report = generate_weekly_summary()
    print(report)
    os.makedirs("report/output", exist_ok=True)
    out = f"report/output/weekly_{datetime.now().strftime('%Y_W%V')}.md"
    with open(out, "w") as f:
        f.write(report)
    print(f"\n✅ Saved to {out}")
