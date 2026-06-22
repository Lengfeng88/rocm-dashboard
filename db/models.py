from sqlalchemy import Column, BigInteger, Integer, Text, Float, ARRAY, TIMESTAMP, ForeignKey
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Repository(Base):
    __tablename__ = "repository"
    repo_id    = Column(Integer, primary_key=True, autoincrement=True)
    name       = Column(Text, unique=True, nullable=False)
    full_name  = Column(Text)
    language   = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True))

class Issue(Base):
    __tablename__ = "issue"
    issue_id       = Column(BigInteger, primary_key=True)
    repo_id        = Column(Integer, ForeignKey("repository.repo_id"), primary_key=True)
    state          = Column(Text)
    title          = Column(Text)
    author         = Column(Text)
    created_at     = Column(TIMESTAMP(timezone=True))
    closed_at      = Column(TIMESTAMP(timezone=True))
    resolution_hrs = Column(Float)
    labels         = Column(ARRAY(Text))
    milestone      = Column(Text)
    comments       = Column(Integer)

class PullRequest(Base):
    __tablename__ = "pull_request"
    pr_id         = Column(BigInteger, primary_key=True)
    repo_id       = Column(Integer, ForeignKey("repository.repo_id"), primary_key=True)
    state         = Column(Text)
    title         = Column(Text)
    author        = Column(Text)
    created_at    = Column(TIMESTAMP(timezone=True))
    merged_at     = Column(TIMESTAMP(timezone=True))
    cycle_hours   = Column(Float)
    review_hours  = Column(Float)
    changed_files = Column(Integer)
    additions     = Column(Integer)
    deletions     = Column(Integer)

class Commit(Base):
    __tablename__ = "commit"
    sha          = Column(Text, primary_key=True)
    repo_id      = Column(Integer, ForeignKey("repository.repo_id"))
    author       = Column(Text)
    committed_at = Column(TIMESTAMP(timezone=True))
    files        = Column(Integer)
    insertions   = Column(Integer)
    deletions    = Column(Integer)

class WorkflowRun(Base):
    __tablename__ = "workflow_run"
    run_id     = Column(BigInteger, primary_key=True)
    repo_id    = Column(Integer, ForeignKey("repository.repo_id"))
    name       = Column(Text)
    status     = Column(Text)
    started_at = Column(TIMESTAMP(timezone=True))
    duration_s = Column(Integer)

class Contributor(Base):
    __tablename__ = "contributor"
    username = Column(Text, primary_key=True)
    repo_id  = Column(Integer, ForeignKey("repository.repo_id"), primary_key=True)
    commits  = Column(Integer, default=0)
    prs      = Column(Integer, default=0)
    reviews  = Column(Integer, default=0)
    issues   = Column(Integer, default=0)
