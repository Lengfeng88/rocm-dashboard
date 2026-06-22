from datetime import datetime

def parse_dt(s):
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except Exception:
        return None

def hours_between(a, b):
    if a and b:
        return round((b - a).total_seconds() / 3600, 2)
    return None

def transform_repo(raw):
    return {
        "name":       raw["full_name"],
        "full_name":  raw["full_name"],
        "language":   raw.get("language"),
        "created_at": parse_dt(raw.get("created_at")),
    }

def transform_issues(raw, repo_id):
    out = []
    for d in raw:
        created = parse_dt(d.get("created_at"))
        closed  = parse_dt(d.get("closed_at"))
        out.append({
            "issue_id":       d["number"],
            "repo_id":        repo_id,
            "state":          d.get("state"),
            "title":          d.get("title", "")[:500],
            "author":         (d.get("user") or {}).get("login"),
            "created_at":     created,
            "closed_at":      closed,
            "resolution_hrs": hours_between(created, closed),
            "labels":         [l["name"] for l in d.get("labels", [])],
            "milestone":      (d.get("milestone") or {}).get("title"),
            "comments":       d.get("comments", 0),
        })
    return out

def transform_prs(raw, repo_id):
    out = []
    for d in raw:
        created = parse_dt(d.get("created_at"))
        merged  = parse_dt(d.get("merged_at"))
        out.append({
            "pr_id":          d["number"],
            "repo_id":        repo_id,
            "state":          d.get("state"),
            "title":          d.get("title", "")[:500],
            "author":         (d.get("user") or {}).get("login"),
            "created_at":     created,
            "merged_at":      merged,
            "cycle_hours":    hours_between(created, merged),
            "review_hours":   None,
            "changed_files":  d.get("changed_files", 0),
            "additions":      d.get("additions", 0),
            "deletions":      d.get("deletions", 0),
        })
    return out

def transform_commits(raw, repo_id):
    out = []
    for d in raw:
        commit = d.get("commit", {})
        author = commit.get("author", {})
        out.append({
            "sha":          d["sha"],
            "repo_id":      repo_id,
            "author":       (d.get("author") or {}).get("login") or author.get("name"),
            "committed_at": parse_dt(author.get("date")),
            "files":        0,
            "insertions":   0,
            "deletions":    0,
        })
    return out

def transform_workflow_runs(raw, repo_id):
    out = []
    for d in raw:
        started = parse_dt(d.get("run_started_at") or d.get("created_at"))
        updated = parse_dt(d.get("updated_at"))
        duration = None
        if started and updated:
            duration = max(0, int((updated - started).total_seconds()))
        out.append({
            "run_id":     d["id"],
            "repo_id":    repo_id,
            "name":       d.get("name", "")[:200],
            "status":     d.get("conclusion") or d.get("status"),
            "started_at": started,
            "duration_s": duration,
        })
    return out
