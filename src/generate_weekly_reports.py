from pathlib import Path
import pandas as pd


def build_weekly_prompt(week, weekly_summary_df, persona_weekly_df):
    """
    Builds a consistent prompt for a given week using:
    - overall weekly metrics (1 row)
    - persona-level metrics (multiple rows)
    """
    overall = weekly_summary_df.loc[weekly_summary_df["week"] == week]
    personas = (
        persona_weekly_df.loc[persona_weekly_df["week"] == week]
        .sort_values("avg_steps", ascending=False)
    )

    overall_payload = overall.to_dict(orient="records")
    persona_payload = personas.to_dict(orient="records")

    return f"""You are a health-tech product analyst writing a weekly behavioral insights report.

Context:
- Data is derived from wearable activity tracking.
- Personas represent behavioral patterns, not clinical categories.
- Be ethical, non-clinical, and actionable.

Week starting: {pd.to_datetime(week).date()}

Overall weekly metrics:
{overall_payload}

Persona-level summary:
{persona_payload}

Tasks:
1. Summarize overall activity trends for the week.
2. Highlight notable differences across personas (who drove changes).
3. Identify engagement risks or opportunities.
4. Suggest 1–2 product or growth actions.
5. Clearly state data limitations (e.g., uneven tracking, missing sleep).

Tone:
- Concise (6–12 sentences)
- Product-manager friendly
- Avoid clinical claims
"""


def write_weekly_prompts(weekly_summary_path, persona_weekly_path, out_dir):
    weekly_summary = pd.read_csv(weekly_summary_path, parse_dates=["week"])
    persona_weekly = pd.read_csv(persona_weekly_path, parse_dates=["week"])

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    weeks = sorted(weekly_summary["week"].dropna().unique())

    index_lines = ["# Weekly Insight Prompts\n"]

    for w in weeks:
        week_str = pd.to_datetime(w).date().isoformat()
        prompt = build_weekly_prompt(w, weekly_summary, persona_weekly)

        # Write individual prompt file
        week_file = out_dir / f"{week_str}_prompt.md"
        week_file.write_text(
            f"## Week Starting {week_str}\n\n```text\n{prompt.strip()}\n```\n",
            encoding="utf-8"
        )

        index_lines.append(f"- {week_str}: {week_file.name}")

    # Write an index file so it's easy to navigate
    index_path = out_dir / "README.md"
    index_path.write_text("\n".join(index_lines) + "\n", encoding="utf-8")

    print(f"✅ Wrote {len(weeks)} weekly prompt files to: {out_dir}")
    print(f"✅ Index: {index_path}")


if __name__ == "__main__":
    # Update these paths if your filenames differ
    weekly_summary_path = "data/processed/weekly_summary.csv"
    persona_weekly_path = "data/processed/persona_weekly.csv"
    out_dir = "reports/weekly_prompts"

    write_weekly_prompts(weekly_summary_path, persona_weekly_path, out_dir)
