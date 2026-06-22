from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routers import issues, prs, ci, contributors, releases, ai

app = FastAPI(title="ROCm Health Dashboard API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(issues.router,       prefix="/api/issues",       tags=["Issues"])
app.include_router(prs.router,          prefix="/api/prs",          tags=["PRs"])
app.include_router(ci.router,           prefix="/api/ci",           tags=["CI"])
app.include_router(contributors.router, prefix="/api/contributors", tags=["Contributors"])
app.include_router(ai.router,          prefix="/api/ai",          tags=["AI"])
app.include_router(releases.router,     prefix="/api/releases",     tags=["Releases"])

@app.get("/api/health")
def health():
    return {"status": "ok"}
