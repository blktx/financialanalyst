def score_yield(yield_pct):
    if yield_pct >= 4:
        return 5
    elif yield_pct >= 2:
        return 3
    elif yield_pct > 0:
        return 1
    else:
        return 0


def score_payout(payout_pct):
    if payout_pct >= 90:
        return 1
    elif payout_pct >= 60:
        return 3
    elif payout_pct > 0:
        return 5
    else:
        return 0


def score_dividend(yield_pct, payout_pct):
    yield_score = score_yield(yield_pct)
    payout_score = score_payout(payout_pct)
    return yield_score + payout_score

import sqlite3

with sqlite3.connect("file:financial.db?mode=ro", uri=True) as conn:
    rows = conn.execute(
    """
    SELECT ticker, dividend_yield, payout_ratio
    FROM stocks
    ORDER BY ticker
    """
).fetchall()

results = []

for ticker, yield_pct, payout_pct in rows:
    if yield_pct is None or payout_pct is None:
        print(f"{ticker}: missing data; score skipped")
        continue

    yield_score = score_yield(yield_pct)
    payout_score = score_payout(payout_pct)
    total = score_dividend(yield_pct, payout_pct)

    results.append({
        "ticker": ticker,
        "dividend_yield": yield_pct,
        "payout_ratio": payout_pct,
        "yield_score": yield_score,
        "payout_score": payout_score,
        "total_score": total,
    })


import csv
columns = [
    "ticker",
    "dividend_yield",
    "payout_ratio",
    "yield_score",
    "payout_score",
    "total_score",
]

with open("dividend_scores.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=columns)
    writer.writeheader()
    writer.writerows(results)

print(f"Saved {len(results)} results to dividend_scores.csv")
