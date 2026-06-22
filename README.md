# ROCm GitHub Engineering Analytics Dashboard
https://lengfeng88.github.io/rocm-dashboard/
A full-stack engineering analytics platform that tracks the health of 6 AMD ROCm open-source repositories in real time.

**Live data from:** ROCm/HIP · ROCm/rocBLAS · ROCm/rccl · ROCm/MIOpen · ROCm/rocFFT · ROCm/rocSPARSE

---

## Architecture
GitHub REST API ──┐

├──► ETL (Polars) ──► PostgreSQL ──► FastAPI ──► React Dashboard

GitHub GraphQL ───┘                                         └──► DeepSeek LLM ──► Weekly Report
## Stack

| Layer | Technology |
|-------|-----------|
| Data collection | Python + httpx (async REST + GraphQL) |
| ETL | Polars + SQLAlchemy |
| Database | PostgreSQL 16 |
| Backend API | FastAPI + uvicorn |
| Frontend | React + Recharts + Vite |
| AI Reports | DeepSeek API (OpenAI-compatible) |
| Containerization | Docker + Docker Compose |

## Features

- **Issue tracking** — open/closed counts, avg resolution time per repo
- **PR health** — cycle time, merge velocity, reviewer load
- **CI stability** — pass rate, median build time, bot run filtering
- **Contributor analysis** — ranking, bus factor (knowledge concentration risk)
- **AI weekly summary** — LLM-generated report with risk flags and recommendations
- **CI coverage detection** — distinguishes GitHub Actions from internal Jenkins CI

## Key Findings (real data)

| Metric | Value |
|--------|-------|
| RCCL CI pass rate | 23.4% (36/48 failures — early compile errors) |
| HIP CI pass rate | 0% (all 22 runs fail within 0.6 min) |
| rocSPARSE bus factor | 84.9% (top-3 contributors own 85% of commits) |
| rocBLAS avg PR cycle | 2.2 days (fastest in the ecosystem) |
| MIOpen avg PR cycle | 12.9 days (slowest — largest codebase) |
| HIP avg issue resolution | 556 days (long-lived tracking issues, not bugs) |

## Quick Start

```bash
# 1. Clone and set up environment
git clone https://github.com/Lengfeng88/rocm-dashboard
cd rocm-dashboard
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Edit .env: add GITHUB_TOKEN, DEEPSEEK_API_KEY, DATABASE_URL_SYNC

# 3. Start PostgreSQL
docker compose up db -d

# 4. Run data collection
python -m collectors.run_all

# 5. Start API
uvicorn api.main:app --reload --port 8000

# 6. Start frontend
cd frontend && npm install && npm run dev
```

Or run everything with Docker:

```bash
docker compose up
```

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/issues/summary` | Open/closed counts + avg resolution time |
| `GET /api/prs/summary` | PR counts + avg cycle time |
| `GET /api/ci/stability` | CI pass rate + median build time |
| `GET /api/ci/coverage` | GitHub Actions vs internal CI breakdown |
| `GET /api/ci/workflows` | Per-workflow drill-down |
| `GET /api/contributors/ranking` | Top contributors by commits |
| `GET /api/contributors/by-repo` | Per-repo contributor breakdown |
| `GET /api/contributors/bus-factor` | Knowledge concentration risk |
| `GET /api/releases/pr-velocity` | Monthly PR merge velocity |
| `GET /api/ai/weekly-summary` | AI-generated engineering health report |

## Project Structure
rocm-dashboard/

├── collectors/          # GitHub API data collection

│   ├── rest_collector.py    # Issues, PRs, commits, CI runs

│   ├── graphql_collector.py # PR reviews (rate-limit efficient)

│   └── run_all.py           # Orchestrator

├── etl/                 # Data transformation

│   ├── transformer.py       # Polars-based cleaning

│   └── loader.py            # PostgreSQL upsert

├── db/

│   └── schema.sql           # 6-table schema with indexes

├── api/                 # FastAPI backend

│   ├── main.py

│   ├── deps.py              # DB session

│   └── routers/             # issues, prs, ci, contributors, releases, ai

├── ai/

│   └── weekly_summary.py    # DeepSeek LLM report generation

├── frontend/            # React + Recharts dashboard

│   └── src/

│       ├── pages/           # Overview, Issues, PRs, CI, Contributors, AI

│       └── components/      # Card, StatCard

├── report/output/       # Generated weekly Markdown reports

├── docker-compose.yml

├── Dockerfile

└── requirements.txt
## Engineering Insights

**Why rocSPARSE bus factor matters:** 84.9% of commits come from 3 contributors.
If any leave, critical sparse linear algebra kernels used by PyTorch ROCm backend lose maintainers.

**Why HIP CI is 0%:** HIP's GitHub Actions workflow fails immediately (0.6 min median),
indicating a TheRock build system dependency issue — not test failures.
MIOpen, rocBLAS, rocFFT, rocSPARSE use AMD internal Jenkins (not visible via GitHub API).

**Why avg resolve time is 556 days for HIP:** These are long-lived feature tracking issues
and upstream LLVM/clang dependency items, not bugs. Normal for a CUDA compatibility layer.
