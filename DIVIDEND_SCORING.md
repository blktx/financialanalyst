# Phase 3: Dividend Scoring — Practice Prototype

## Purpose
This learning project connects an existing SQLite stock database to Python functions and exports an explainable dividend score to CSV. The yield component rewards higher reported dividend yield; the payout component uses a simple earnings payout rule. The thresholds are illustrative and have not been validated as an investment model.

## Run
Use Python 3; the scoring script uses only standard-library modules. From the folder containing the script and your existing financial.db, run:

```bash
python3 dividend_score.py
```

The stocks table must contain ticker, dividend_yield, and payout_ratio. The script opens financial.db in read-only mode, selects all stocks alphabetically, and exports dividend_scores.csv in the current working directory. Each run replaces that CSV. Rows with either metric set to SQL NULL are skipped with a message. The database itself is not modified.

The database is a local prerequisite and is not included in this update. The existing loader and refresh scripts require yfinance (and pandas for the loader), the existing extended database schema, and configured local paths. To update an already populated database, use daily_refresh.py with its DB_PATH and LOG_PATH set correctly. load_database.py uses INSERT OR REPLACE with basic columns only; rerunning it can reset extended columns such as payout_ratio.

## Data units
Both scoring inputs use percentage numbers: 1.96 means 1.96%, and 25.71 means 25.71%.

For the source values checked during this exercise, yfinance dividendYield was already a percentage number. load_database.py and daily_refresh.py therefore no longer multiply that field by 100. The observed payoutRatio was a fraction (0.2571), so daily_refresh.py still multiplies that field by 100 to store 25.71. Check source field units when changing providers or versions rather than applying a blanket conversion.

In Excel, keep these CSV fields formatted as Number. Applying Percentage formatting directly to 1.96 would display 196%.

## Practice rules
| Dividend yield (%) | Points |
|---|---:|
| 0 or below | 0 |
| Above 0 and below 2 | 1 |
| 2 to below 4 | 3 |
| 4 or above | 5 |

| Payout ratio (%) | Points |
|---|---:|
| 0 or below | 0 |
| Above 0 and below 60 | 5 |
| 60 to below 90 | 3 |
| 90 or above | 1 |

Total = yield score + payout score, out of 10.

## Example snapshot
The uploaded CSV was reviewed on September 29, 2026. It contains 40 unique tickers; the source data timestamp is not stored in this CSV.

| Ticker | Yield (%) | Payout (%) | Yield score | Payout score | Total |
|---|---:|---:|---:|---:|---:|
| JPM | 1.96 | 25.71 | 1 | 5 | 6 |
| MAIN | 5.77 | 86.35 | 5 | 3 | 8 |
| T | 4.46 | 36.63 | 5 | 5 | 10 |

## Limitations
- This is an educational prototype, not a buy/sell recommendation. A 10/10 means a stock matches these two rules; 0/10 is not an overall company-quality judgment.
- Higher yield can reflect a falling share price. This rule does not test the cause of a high yield.
- No company-type adjustments are made. REITs and business development companies need separate analysis; the scores for O and MAIN should not be interpreted as comparable dividend safety ratings.
- Cash flow, debt, dividend growth, payment history, valuation, and total returns are not included.
- Zero and negative payout ratios are both assigned zero points, but they can have different meanings and need review.
- SQL NULL values are skipped, but the existing upstream scripts can replace missing provider metrics with zero. The scoring script cannot distinguish those missing values from genuine zeros.
- Thresholds, equal weights, and source data have not been backtested or independently validated.

## Validation
All three Python files passed syntax checks. Running the scoring script against a temporary SQLite database populated with the uploaded CSV inputs reproduced all 40 CSV rows exactly. A missing-metric row was skipped, the database remained unchanged, and an absent database failed without creating an empty file. No live market refresh was run during this review.

## Next steps
Preserve missing data upstream, include timestamps, distinguish company types, and evaluate additional indicators before treating the prototype as a formal screening model.
