import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
load_dotenv()

engine  = create_engine(os.environ["DATABASE_URL_SYNC"], echo=False)
Session = sessionmaker(bind=engine)

def upsert_repo(data):
    with Session() as s:
        row = s.execute(text(
            "INSERT INTO repository (name, full_name, language, created_at) "
            "VALUES (:name,:full_name,:language,:created_at) "
            "ON CONFLICT (name) DO UPDATE SET language=EXCLUDED.language "
            "RETURNING repo_id"
        ), data).fetchone()
        s.commit()
        return row[0]

def upsert_issues(rows):
    if not rows: return
    with Session() as s:
        for r in rows:
            s.execute(text("""
                INSERT INTO issue
                  (issue_id,repo_id,state,title,author,created_at,closed_at,
                   resolution_hrs,labels,milestone,comments)
                VALUES
                  (:issue_id,:repo_id,:state,:title,:author,:created_at,:closed_at,
                   :resolution_hrs,:labels,:milestone,:comments)
                ON CONFLICT (issue_id,repo_id) DO UPDATE SET
                  state=EXCLUDED.state, closed_at=EXCLUDED.closed_at,
                  resolution_hrs=EXCLUDED.resolution_hrs, comments=EXCLUDED.comments
            """), r)
        s.commit()

def upsert_prs(rows):
    if not rows: return
    with Session() as s:
        for r in rows:
            s.execute(text("""
                INSERT INTO pull_request
                  (pr_id,repo_id,state,title,author,created_at,merged_at,
                   cycle_hours,review_hours,changed_files,additions,deletions)
                VALUES
                  (:pr_id,:repo_id,:state,:title,:author,:created_at,:merged_at,
                   :cycle_hours,:review_hours,:changed_files,:additions,:deletions)
                ON CONFLICT (pr_id,repo_id) DO UPDATE SET
                  state=EXCLUDED.state, merged_at=EXCLUDED.merged_at,
                  cycle_hours=EXCLUDED.cycle_hours
            """), r)
        s.commit()

def upsert_commits(rows):
    if not rows: return
    with Session() as s:
        for r in rows:
            s.execute(text("""
                INSERT INTO commit
                  (sha,repo_id,author,committed_at,files,insertions,deletions)
                VALUES
                  (:sha,:repo_id,:author,:committed_at,:files,:insertions,:deletions)
                ON CONFLICT (sha) DO NOTHING
            """), r)
        s.commit()

def upsert_workflow_runs(rows):
    if not rows: return
    with Session() as s:
        for r in rows:
            s.execute(text("""
                INSERT INTO workflow_run
                  (run_id,repo_id,name,status,started_at,duration_s)
                VALUES
                  (:run_id,:repo_id,:name,:status,:started_at,:duration_s)
                ON CONFLICT (run_id) DO UPDATE SET status=EXCLUDED.status
            """), r)
        s.commit()
