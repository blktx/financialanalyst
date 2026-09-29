# Financial Analysis Dashboard (Power BI)

This is the Power BI version of my personal financial analysis project. It uses the four sheets in `Financial_Analysis_Report.xlsx` as a snapshot of a 40-company watchlist. The report has four pages:

| Page | Analysis |
| --- | --- |
| Overview | Company fundamentals, growth and dividend groups, KPI cards and filters |
| Dividend Dashboard | Yield, payout ratio, dividend streak and a rule-based safety label |
| Sector Analysis | Market capitalization and valuation across sectors |
| Trend & Momentum | Price relative to 50- and 200-day moving averages and trend signals |

## Files

- [`powerbi/Financial_Dashboard.pbix`](powerbi/Financial_Dashboard.pbix) — finished four-page Power BI report.
- [`powerbi/Financial_Analysis_Report.xlsx`](powerbi/Financial_Analysis_Report.xlsx) — the Excel input snapshot.
- [`Phase2_README.md`](Phase2_README.md) — the separate Streamlit dashboard built earlier in Phase 2.

## Open and refresh

1. Download both files in `powerbi/`.
2. Open the `.pbix` file in Power BI Desktop on Windows. The saved report can be viewed with its imported data.
3. To refresh from the workbook, open **Transform data → Data source settings**, change the Excel file path to the downloaded `Financial_Analysis_Report.xlsx`, and refresh. A path from the original development computer will not exist on your computer.

The workbook is a snapshot, so refreshing it does not fetch live market prices. The Python and SQLite work in this repository documents a separate data workflow; this Power BI file imports the Excel output.

## Interpretation and limitations

This is a learning and portfolio project, not a stock recommendation. The underlying market snapshot and derived figures have not been independently validated for investment decisions. Some yield values in the workbook appear to use inconsistent percentage scaling; review units before comparing or aggregating them. A safety label is a simplified screening rule, not an assessment of dividend sustainability. Ratios and point-in-time metrics should be averaged, weighted appropriately, or shown for a selected company rather than summed across companies.

## Next step

Phase 3 will add and test a documented dividend quality scoring model. It is not included in the current report.
