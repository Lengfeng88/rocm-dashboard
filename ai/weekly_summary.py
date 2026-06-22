import os, sys, argparse, json
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

sys.path.insert(0, os.path.abspath("."))
from etl.queries import get_weekly_kpis

client = OpenAI(
    api_key=os.environ["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com"
)

def build_prompt(kpis: dict) -> str:
    return f"""You are an AMD ROCm engineering program manager analyst.
Analyze the following GitHub engineering KPI data and write a concise weekly report.

KPI DATA:
{json.dumps(kpis, indent=2, default=str)}

Write exactly 4 paragraphs with these headers:

## Executive Summary
(3 sentences: overall health, biggest win, biggest concern)

## Top Bottlenecks
(Name specific repos and exact numbers. Which repo has the slowest merge time? Highest open PRs?)

## Recommendations
(2-3 concrete, actionable items. Name specific repos and suggested actions.)

## Next Week Risks
(What could get worse? Name specific signals from the data.)

Be direct and specific. Use numbers from the data. No bullet points, paragraph format only.
"""

def generate_weekly_summary(output_path: str = None) -> str:
    print("Fetching KPIs from database...")
    kpis = get_weekly_kpis()

    print("Calling DeepSeek API...")
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": build_prompt(kpis)}],
        max_tokens=800,
        temperature=0.3,
    )
    summary = response.choices[0].message.content

    if output_path:
        week = datetime.now().strftime("Week %W, %Y")
        full = f"# ROCm Engineering Weekly Report\n_{week}_\n\n{summary}"
        with open(output_path, "w") as f:
            f.write(full)
        print(f"Saved to {output_path}")

    return summary

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default=None)
    args = parser.parse_args()
    result = generate_weekly_summary(args.output)
    print("\n" + "="*60)
    print(result)
