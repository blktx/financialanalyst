from datetime import datetime
from pathlib import Path
import sqlite3

project_folder = Path(__file__).resolve().parent
db_path = project_folder / "financial.db"
sql_path = project_folder / "dividend_scoring.sql"

query = sql_path.read_text(encoding="utf-8")

with sqlite3.connect(db_path.as_uri() + "?mode=ro", uri=True) as conn:
    conn.row_factory = sqlite3.Row
    results = conn.execute(query).fetchall()

    refresh_dates = conn.execute(
        """
        SELECT
            MIN(last_updated) AS oldest,
            MAX(last_updated) AS newest
        FROM stocks
        """
    ).fetchone()

generated_at = datetime.now().strftime("%Y-%m-%d %H:%M")

lines = [
    "Weekly Dividend Digest",
    f"Generated: {generated_at}",
        f"Stock data timestamps: {refresh_dates['oldest']} to {refresh_dates['newest']}",
    "Model: Version 1 — yield + payout scoring",
    "First 5 stocks; ties ordered alphabetically.",
    "",
]
for row in results[:5]:
    lines.append(
        f"{row['ticker']}: "
        f"score {row['total_score']}, "
        f"rank {row['score_rank']}"
    )

digest_text = "\n".join(lines)

output_path = project_folder / "weekly_digest.txt"
output_path.write_text(digest_text, encoding="utf-8")

print(digest_text)
print(f"\nSaved to: {output_path}")