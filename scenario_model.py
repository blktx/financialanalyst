# Example inputs, expressed as percentages.
base_yield = 4.0
base_payout = 50.0

# A 20% dividend cut leaves 80% of the original dividend.
dividend_cut = 0.20
remaining_dividend = 1 - dividend_cut

# Assume share price and earnings stay unchanged.
scenario_yield = base_yield * remaining_dividend
scenario_payout = base_payout * remaining_dividend

print(f"Dividend yield: {base_yield:.2f}% → {scenario_yield:.2f}%")
print(f"Payout ratio: {base_payout:.2f}% → {scenario_payout:.2f}%")

def score_yield(yield_pct):
    if yield_pct is None:
        return None
    if yield_pct >= 4:
        return 5
    elif yield_pct >= 2:
        return 3
    elif yield_pct > 0:
        return 1
    else:
        return 0


base_yield_score = score_yield(base_yield)
scenario_yield_score = score_yield(scenario_yield)

print(f"Yield points: {base_yield_score} → {scenario_yield_score}")

def score_payout(payout_pct):
    if payout_pct is None:
        return None
    if payout_pct >= 90:
        return 1
    elif payout_pct >= 60:
        return 3
    elif payout_pct > 0:
        return 5
    else:
        return 0


base_payout_score = score_payout(base_payout)
scenario_payout_score = score_payout(scenario_payout)



print(f"Payout points: {base_payout_score} → {scenario_payout_score}")

base_total = base_yield_score + base_payout_score
scenario_total = scenario_yield_score + scenario_payout_score
score_change = scenario_total - base_total

print(f"Total score: {base_total} → {scenario_total}")
print(f"Score change: {score_change:+d}")

from pathlib import Path
import sqlite3

db_path = Path(__file__).resolve().parent / "financial.db"

with sqlite3.connect(db_path.as_uri() + "?mode=ro", uri=True) as conn:
    rows = conn.execute(
        """
        SELECT ticker, dividend_yield, payout_ratio
        FROM stocks
        ORDER BY ticker
        """
    ).fetchall()

print(f"\nLoaded {len(rows)} stocks.")

for ticker, actual_yield, actual_payout in rows:
    if actual_yield is None or actual_payout is None:
        print(f"{ticker}: unscored — missing yield or payout")
        continue

    if actual_yield <= 0:
        print(f"{ticker}: excluded — no positive dividend yield")
        continue

    cut_yield = actual_yield * remaining_dividend
    cut_payout = actual_payout * remaining_dividend

    original_score = (
        score_yield(actual_yield) + score_payout(actual_payout)
    )
    cut_score = score_yield(cut_yield) + score_payout(cut_payout)
    change = cut_score - original_score

    print(
        f"{ticker}: {original_score} → {cut_score} "
        f"(change {change:+d})"
    )
    

# Check values immediately below and at each scoring threshold.
assert score_yield(1.99) == 1
assert score_yield(2.00) == 3
assert score_yield(3.99) == 3
assert score_yield(4.00) == 5

assert score_payout(59.99) == 5
assert score_payout(60.00) == 3
assert score_payout(89.99) == 3
assert score_payout(90.00) == 1

print("\nAll threshold tests passed.")

sql_path = Path(__file__).resolve().parent / "dividend_scoring.sql"

with sqlite3.connect(db_path.as_uri() + "?mode=ro", uri=True) as conn:
    conn.row_factory = sqlite3.Row
    sql_rows = conn.execute(
        sql_path.read_text(encoding="utf-8")
    ).fetchall()

for stock in sql_rows:
    python_yield = score_yield(stock["dividend_yield"])
    python_payout = score_payout(stock["payout_ratio"])

    python_total = (
        None
        if python_yield is None or python_payout is None
        else python_yield + python_payout
    )

    assert python_yield == stock["yield_score"], stock["ticker"]
    assert python_payout == stock["payout_score"], stock["ticker"]
    assert python_total == stock["total_score"], stock["ticker"]

print(f"Python and SQL scores match for all {len(sql_rows)} stocks.")