"""
把实时数据库数据 + AI 周报内嵌进 index.html，用于 GitHub Pages。
"""
import os, sys, re, json, datetime
sys.path.insert(0, os.path.abspath("."))

from etl.queries import get_weekly_kpis
from etl.loader  import Session
from sqlalchemy  import text

# ── 1. 拉取所有 API 数据 ──────────────────────────────────────────────────────
def fetch_all():
    kpis = get_weekly_kpis()
    with Session() as s:
        issue_summary = [dict(r._mapping) for r in s.execute(text("""
            SELECT r.name AS repo,
                   COUNT(*) FILTER (WHERE i.state='open')   AS open,
                   COUNT(*) FILTER (WHERE i.state='closed') AS closed,
                   ROUND(CAST(AVG(i.resolution_hrs)/24 AS numeric),1) AS avg_resolve_days
            FROM issue i JOIN repository r ON r.repo_id=i.repo_id
            GROUP BY r.name ORDER BY open DESC
        """)).fetchall()]

        pr_summary = [dict(r._mapping) for r in s.execute(text("""
            SELECT r.name AS repo,
                   COUNT(*) FILTER (WHERE p.state='open') AS open,
                   COUNT(*) FILTER (WHERE p.merged_at IS NOT NULL) AS merged,
                   ROUND(CAST(AVG(p.cycle_hours)/24 AS numeric),1) AS avg_cycle_days
            FROM pull_request p JOIN repository r ON r.repo_id=p.repo_id
            GROUP BY r.name ORDER BY open DESC
        """)).fetchall()]

        merge_time = [dict(r._mapping) for r in s.execute(text("""
            SELECT r.name AS repo,
                   ROUND(CAST(AVG(p.cycle_hours)/24 AS numeric),1) AS avg_days,
                   COUNT(*) AS total_merged
            FROM pull_request p JOIN repository r ON r.repo_id=p.repo_id
            WHERE p.merged_at >= NOW() - INTERVAL '30 days'
            GROUP BY r.name ORDER BY avg_days DESC NULLS LAST
        """)).fetchall()]

        ci_data = [dict(r._mapping) for r in s.execute(text("""
            SELECT r.name AS repo,
                   COUNT(*) AS total_runs,
                   COUNT(*) FILTER (WHERE w.status='success') AS real_ci_runs,
                   COUNT(*) FILTER (WHERE w.status!='success') AS bot_runs
            FROM workflow_run w JOIN repository r ON r.repo_id=w.repo_id
            GROUP BY r.name
        """)).fetchall()]

        contributors = [dict(r._mapping) for r in s.execute(text("""
            SELECT author, COUNT(DISTINCT repo_id) AS repos, COUNT(*) AS commits
            FROM commit WHERE author IS NOT NULL
            GROUP BY author ORDER BY commits DESC LIMIT 10
        """)).fetchall()]

        bus_factor = [dict(r._mapping) for r in s.execute(text("""
            SELECT r.name AS repo,
                   ROUND(CAST(100.0*SUM(top3)/NULLIF(SUM(total),0) AS numeric),1) AS top3_pct,
                   SUM(total) AS total_commits
            FROM (
                SELECT repo_id, commits AS total,
                       CASE WHEN rnk<=3 THEN commits ELSE 0 END AS top3
                FROM (
                    SELECT repo_id, commits,
                           ROW_NUMBER() OVER (PARTITION BY repo_id ORDER BY commits DESC) AS rnk
                    FROM (SELECT repo_id,author,COUNT(*) AS commits
                          FROM commit WHERE author IS NOT NULL
                          GROUP BY repo_id,author) s
                ) ranked
            ) bf JOIN repository r ON r.repo_id=bf.repo_id
            GROUP BY r.name ORDER BY top3_pct DESC
        """)).fetchall()]

        resolution = [dict(r._mapping) for r in s.execute(text("""
            SELECT CASE WHEN 'bug'=ANY(labels) THEN 'bug'
                        WHEN 'performance'=ANY(labels) THEN 'performance'
                        WHEN 'enhancement'=ANY(labels) THEN 'enhancement'
                        ELSE 'other' END AS label_type,
                   ROUND(CAST(AVG(resolution_hrs)/24 AS numeric),1) AS avg_days,
                   COUNT(*) AS total
            FROM issue WHERE closed_at IS NOT NULL
            GROUP BY 1 ORDER BY avg_days DESC
        """)).fetchall()]

    return {
        "issueSummary": issue_summary,
        "prSummary":    pr_summary,
        "mergeTime":    merge_time,
        "ciData":       ci_data,
        "contributors": contributors,
        "busFactor":    bus_factor,
        "resolution":   resolution,
    }

# ── 2. 读取 AI 周报 ───────────────────────────────────────────────────────────
def md_to_html(text_in):
    text_in = re.sub(r'^## (.+)$', r'<h3>\1</h3>', text_in, flags=re.MULTILINE)
    text_in = re.sub(r'^# (.+)$',  r'<h2>\1</h2>', text_in, flags=re.MULTILINE)
    text_in = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text_in)
    paras = []
    for block in text_in.strip().split('\n\n'):
        block = block.strip()
        if block.startswith('<h'):
            paras.append(block)
        elif block:
            paras.append(f'<p>{block}</p>')
    return '\n'.join(paras)

def read_ai_summary():
    path = "/tmp/rocm_weekly.md"
    if not os.path.exists(path):
        return "<p>No AI summary available yet.</p>"
    with open(path) as f:
        return md_to_html(f.read())

# ── 3. 重建 index.html ────────────────────────────────────────────────────────
def build():
    print("Fetching data from DB...")
    data = fetch_all()
    for k, v in data.items():
        print(f"  {k}: {len(v)} rows")

    ai_html = read_ai_summary()
    today   = datetime.datetime.now().strftime("%Y-%m-%d")

    with open("index.html", "r") as f:
        html = f.read()

    # 更新静态数据块
    new_block = "<script>\nconst STATIC_DATA = " + json.dumps(data, default=str) + ";\n</script>"
    if "const STATIC_DATA" in html:
        html = re.sub(r'<script>\s*const STATIC_DATA[\s\S]*?</script>', new_block, html)
    else:
        html = html.replace("</head>", new_block + "\n</head>", 1)

    # 更新 AI 周报内容
    if 'id="page-ai"' in html:
        html = re.sub(
            r'(<div id="page-ai"[^>]*>)[\s\S]*?(</div>\s*</main>)',
            lambda m: build_ai_page(ai_html, today) + '\n</main>',
            html
        )
    else:
        if 'showTab(\'ai\')' not in html:
            html = html.replace('</nav>',
                '  <div class="tab" onclick="showTab(\'ai\')">AI Weekly</div>\n</nav>')
        html = html.replace('</main>', build_ai_page(ai_html, today) + '\n</main>')

    with open("index.html", "w") as f:
        f.write(html)
    print(f"Done! index.html = {len(html):,} bytes")

def build_ai_page(ai_html, today):
    return f'''<div id="page-ai" class="page">
  <div style="max-width:800px">
    <div style="display:flex;align-items:center;gap:12px;margin-bottom:20px">
      <div style="width:3px;height:32px;background:#ED1C24;border-radius:2px"></div>
      <div>
        <div style="font-size:15px;font-weight:600;color:#E2E8F0">AI Weekly Report</div>
        <div style="font-size:11px;color:#64748B;font-family:monospace">Generated by DeepSeek · {today}</div>
      </div>
    </div>
    <div style="background:#13161B;border:1px solid #1E2329;border-radius:8px;padding:28px 32px;line-height:1.8">
      <style>
        #page-ai h3{{font-size:13px;font-weight:600;color:#60A5FA;text-transform:uppercase;letter-spacing:.06em;margin:24px 0 10px;padding-bottom:6px;border-bottom:1px solid #1E2329}}
        #page-ai p{{font-size:13px;color:#94A3B8;margin:0 0 14px;line-height:1.8}}
        #page-ai strong{{color:#E2E8F0}}
      </style>
      {ai_html}
    </div>
  </div>
</div>'''

if __name__ == "__main__":
    build()
