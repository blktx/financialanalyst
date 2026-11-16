# Phase 3 — Dividend Scoring Model

Version 1 completed November 13, 2026. Documentation restored November 16, 2026.

## Purpose

This learning project uses Python and SQLite to score dividend stocks,
compare P/E ratios within sectors, generate a weekly Gmail digest, and
explore a dividend-cut scenario. The scoring thresholds are heuristic
learning assumptions, not empirically validated investment rules.

## Dividend Scoring Formula

Inputs use percentage units: 4.0 means 4%, and 60.0 means 60%.

| Dividend yield | Points |
|---|---:|
| 4% or higher | 5 |
| 2% to below 4% | 3 |
| Above 0% to below 2% | 1 |
| 0% or below | 0 |

| Payout ratio | Points |
|---|---:|
| Above 0% to below 60% | 5 |
| 60% to below 90% | 3 |
| 90% or higher | 1 |
| 0% or below | 0 |

Total score = yield points + payout points. The maximum is 10.
Higher yields receive more points; positive payout ratios below 60%
receive the most payout points. Zero and negative payout ratios receive
zero points under this model, without diagnosing their underlying causes.

In the SQL query and scenario functions, missing yield or payout data
produces a missing total rather than zero. The original Python CSV
workflow skips records with missing inputs.

`dividend_scoring.sql` uses `DENSE_RANK()` to rank totals from highest
to lowest. Equal totals share a rank, and results are ordered by total
descending and ticker alphabetically.

## Sector Valuation Comparison

`sector_median_pe.sql` and `valuation_flags.sql` calculate the median
positive P/E within each sector in the tracked dataset.

1. Exclude missing, zero, and negative P/E ratios from the calculation.
2. Use `ROW_NUMBER()` to assign positions within each sector and
   `COUNT(*) OVER (...)` to count eligible observations.
3. For an odd count, use the middle P/E. For an even count, average
   the two middle P/Es.
4. Use a `LEFT JOIN` to attach sector statistics to all stocks,
   including those with missing P/E ratios.

| Condition, evaluated in this order | Valuation flag |
|---|---|
| Stock P/E is missing or nonpositive | P/E unavailable |
| No valid sector median exists | Sector median unavailable |
| Fewer than two eligible observations | Insufficient peers |
| Stock P/E is below the median | Below sector median |
| Stock P/E equals the median | At sector median |
| Stock P/E is above the median | Above sector median |

The sector count and median include the stock itself when eligible.
They represent this project's tracked stocks, not the entire sector.
Small samples limit the comparison. A below-median P/E does not establish
undervaluation. Valuation flags do not change dividend-score points.

## Dividend-Cut Scenario

`scenario_model.py` asks what happens to scores if dividends fall 20%
while share prices and earnings remain unchanged.

```text
Remaining dividend = 1 - 0.20 = 0.80
Scenario yield = original yield × 0.80
Scenario payout ratio = original payout ratio × 0.80
Score change = scenario total - original total
```

The script reads `financial.db` in read-only mode and applies the same
functions before and after the cut. It prints results without updating
the database. Missing inputs are reported as unscored. Among remaining
records, nonpositive dividend yields are excluded from the scenario.
The SQL scoring query itself retains all stocks.

| Example measure | Original | After a 20% cut |
|---|---:|---:|
| Dividend yield | 4.00% | 3.20% |
| Payout ratio | 50.00% | 40.00% |
| Yield points | 5 | 3 |
| Payout points | 5 | 5 |
| Total score | 10 | 8 |

The snapshot tested on November 13, 2026 contained 40 stocks:

| Outcome | Count |
|---|---:|
| Score decreased | 3 |
| Score unchanged | 19 |
| Score increased | 5 |
| Excluded: nonpositive yield | 11 |
| Unscored: missing data | 2 |
| Total | 40 |

These results describe that snapshot and may change after data refreshes.

### Why a dividend cut can increase the score

A lower payout ratio can earn more points while the yield remains in
the same scoring band. For example, a 3% yield and 70% payout score
3 + 3 = 6. After a 20% cut, a 2.4% yield and 56% payout score
3 + 5 = 8, even though dividend income fell.

Version 1 has no explicit dividend-cut penalty. An increased score
does not prove that a company or investment has improved. Similarly,
an unchanged score can hide a meaningful reduction in income.

## Weekly Email Workflow

1. `weekly_digest.py` reads `dividend_scoring.sql` and the database.
2. It writes `weekly_digest.txt` with the generation time, oldest and
   newest stock-update timestamps, model label, and first five stocks.
3. `send_digest.py --send` sends the report through Gmail.
4. `run_weekly_digest.py` generates the report first and sends only
   if report generation succeeds.

Exactly five stock rows are shown, so a tie may extend beyond the report.
The Gmail App Password is retrieved from macOS Keychain, not stored
in source code. Without `--send`, the email script prepares a message
without sending, but still reads Keychain and the saved report.

The supplied LaunchAgent schedules the runner for Mondays at 08:00
in the Mac's local time zone (America/New_York when configured).
Timely delivery depends on an awake Mac, a logged-in user, network
access, accessible local files, and successful authentication.
The configuration contains machine-specific paths.

### Report generation is separate from data refresh

The weekly runner currently does **not** run `daily_refresh.py`.
A newly generated email can therefore contain older stock data.
On November 16, 2026, the 08:00 email was delivered successfully,
but its stock-update timestamps were still November 2, 2026.
Automatic refresh before report generation is the next improvement.

The configured logs are `/tmp/beckylin-weekly-digest.log` and
`/tmp/beckylin-weekly-digest-error.log`. These temporary files are not
a permanent audit history. The email script currently prints a
Keychain lookup failure without explicitly returning a nonzero exit
status, so logs and actual receipt matter when checking delivery.

## Validation

The following checks passed on November 13, 2026:

| Check | Result |
|---|---|
| 0% dividend cut | All 27 scored stocks unchanged; 11 excluded and 2 unscored |
| Yield boundaries | 1.99 → 1, 2.00 → 3, 3.99 → 3, 4.00 → 5 |
| Payout boundaries | 59.99 → 5, 60.00 → 3, 89.99 → 3, 90.00 → 1 |
| Python versus SQL | Component scores and totals matched for all 40 stocks, including missing values |

The zero-cut check was manual; `dividend_cut` was restored to `0.20`.
The eight boundary assertions and Python–SQL comparison remain in
`scenario_model.py`. Run Python normally, because `-O` disables assertions.
These checks verify rule consistency for the tested inputs, not
external-data accuracy or predictive investment performance.

## Running the Project

From the project folder, with Python and the local database available:

```bash
# Run the scenario and assertions; no email is sent.
python3 scenario_model.py

# Generate a report; no email is sent.
python3 weekly_digest.py

# Prepare the saved report as an email without sending it.
python3 send_digest.py
```

To deliberately send the saved report:

```bash
python3 send_digest.py --send
```

To generate and send a report in one step:

```bash
python3 run_weekly_digest.py
```

The scenario and digest scripts use Python's standard library.
The separate refresh script requires `yfinance`. SQL queries require
a SQLite version with window-function support. The database, Keychain
credentials, and local scheduling configuration must be set up separately.

## Main Files

| File | Purpose |
|---|---|
| `financial.db` | Local stock database |
| `dividend_score.py` | Original Python scoring and CSV workflow |
| `dividend_scoring.sql` | Component scores, totals and ranks |
| `dividend_score_distribution.sql` | Stock counts by score |
| `sector_median_pe.sql` | Sector median P/E calculation |
| `valuation_flags.sql` | Stock-level P/E comparisons |
| `scenario_model.py` | Dividend-cut scenario and validation |
| `weekly_digest.py` | Text report generation |
| `weekly_digest.txt` | Generated report |
| `send_digest.py` | Email preparation and optional sending |
| `run_weekly_digest.py` | Generate-then-send workflow |
| `com.beckylin.weekly-dividend-digest.plist` | Local schedule configuration |
| `daily_refresh.py` | Separate stock-data refresh |

## Limitations and Next Improvements

- Thresholds are heuristic and have not been backtested.
- Scores change in discrete bands and omit dividend history, cash flow,
  debt, earnings quality, and company-type adjustments.
- The scenario assumes fixed prices and earnings; it is not a forecast.
- Sector medians use a small tracked universe and include the stock itself.
- The email currently shows scores and ranks, not valuation or scenario results.
- Automatic data refresh and failure checks before sending remain pending.

Possible extensions include several cut sizes, price and earnings
scenarios, CSV scenario exports, and dedicated automated tests.

## Completion Status

All seven Phase 3 tasks are complete for the Version 1 learning scope:
formula design, SQL scoring, valuation flags, weekly email, scenario
model, validation, and documentation. Automatic stock-data refresh
is a separate follow-up improvement.
