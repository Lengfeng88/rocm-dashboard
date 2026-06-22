"""
API smoke tests — verify all endpoints return 200 and correct shape.
Requires DATABASE_URL_SYNC to be set.
"""
import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


def test_health():
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_issues_summary():
    r = client.get("/api/issues/summary")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_prs_summary():
    r = client.get("/api/prs/summary")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    if data:
        assert "repo" in data[0]
        assert "avg_cycle_days" in data[0]


def test_ci_stability():
    r = client.get("/api/ci/stability")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_ci_coverage():
    r = client.get("/api/ci/coverage")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    if data:
        assert "real_ci_runs" in data[0]
        assert "bot_runs" in data[0]


def test_contributors_ranking():
    r = client.get("/api/contributors/ranking")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    if data:
        assert "author" in data[0]
        assert "commits" in data[0]


def test_bus_factor():
    r = client.get("/api/contributors/bus-factor")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    if data:
        assert "top3_pct" in data[0]
        assert data[0]["top3_pct"] <= 100.0


def test_releases_pr_velocity():
    r = client.get("/api/releases/pr-velocity")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_ci_workflows_filter():
    r = client.get("/api/ci/workflows?repo=ROCm/rccl")
    assert r.status_code == 200
    data = r.json()
    # All results should be for rccl
    for row in data:
        assert row["repo"] == "ROCm/rccl"
