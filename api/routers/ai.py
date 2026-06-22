from fastapi import APIRouter
from ai.weekly_summary import generate_weekly_summary, fetch_kpis
import os
from datetime import datetime

router = APIRouter()

@router.get("/kpis")
def get_kpis():
    return fetch_kpis()

@router.get("/weekly-summary")
def weekly_summary():
    report = generate_weekly_summary()
    # 同时保存文件
    os.makedirs("report/output", exist_ok=True)
    out = f"report/output/weekly_{datetime.now().strftime('%Y_W%V')}.md"
    with open(out, "w") as f:
        f.write(report)
    return {"report": report, "saved_to": out}
