# Financial Analysis Portfolio

A learning portfolio combining Python, SQLite, and Power BI to collect stock data, explore financial indicators, and build explainable analysis workflows.

## Project phases

- [Phase 1](Phase1_README.md): stock data collection and database workflow.
- [Phase 2](Phase2_README.md): analysis and reporting.
- [Power BI dashboard](PowerBI_README.md): dashboard and Excel snapshot in [powerbi/](powerbi/).
- [Phase 3 practice prototype](DIVIDEND_SCORING.md): dividend scoring with Python and CSV export. This phase is in progress.

## Dividend scoring

From the folder containing dividend_score.py and an existing financial.db with the stocks table, run:

```bash
python3 dividend_score.py
```

The script reads ticker, dividend_yield, and payout_ratio, calculates two component scores, and exports dividend_scores.csv. The scoring script uses Python's standard library and opens the database in read-only mode. The local database is not included in this update; the existing data collection scripts need their dependencies, schema, and local paths configured separately.

[DIVIDEND_SCORING.md](DIVIDEND_SCORING.md) explains input units, thresholds, examples, and limitations. The included CSV is a 40-stock example snapshot reviewed on September 29, 2026.

## Scope

This repository documents learning progress. The dividend thresholds are practice rules, not a validated investment model or a buy/sell recommendation. Further work includes missing-data handling, company-type adjustments, and additional financial indicators.
