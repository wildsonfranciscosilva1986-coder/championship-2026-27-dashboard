# English Championship 2026/27 — DIN Mercado Dashboard

A standalone, mobile-first Championship dashboard using the dark Brazil-series palette. This project contains no Premier League or other-division data.

## Build and validation

From this directory:

```bash
python3 validate_championship.py
python3 build_dashboard.py
```

The validator rebuilds a match-level table from the **131 final-score rows** and compares P, points, W–D–L, GF, GA and GD against both the official EFL table and ESPN's independent table. It applies the EFL's official four-point 2026/27 deduction to Southampton. It fails closed on any mismatch or unconfirmed score. The dashboard reports 131 completed fixtures out of the 552-match season, goal/BTTS/Over 2.5 rates with denominators, and the home/draw/away split; its Fixtures tab browses all 156 available records and filters by status or club.

## Snapshot

Cutoff: **20 October 2026, 13:38:26 America/Sao_Paulo (BRT, UTC−03:00)**. The latest final in the dataset is 17 October; the next fixture, Wolverhampton Wanderers–Portsmouth at 18:45 UTC (15:45 BRT) on 20 October, was still scheduled at cutoff. The future-fixture file is intentionally bounded to **20 October–1 November 2026**.

## Files

- `index.html` — deployable standalone app, bundled data, Brazil-series palette and mobile-first UI. Includes league KPIs, standings/zones, recent and upcoming fixtures, club form/venue splits, Top 5 rankings, H2H and interactive 1-X-2/goal estimates, plus a filterable full available fixtures/results view.
- `championship-mark.svg` — distinct project identity asset.
- `data/fixtures_results_2026_27.csv` — 131 final scores from ESPN's match feed; links and feed IDs retained.
- `data/efl_official_table.csv` — official EFL standings snapshot.
- `data/independent_espn_table.csv` — independent standings cross-check.
- `data/upcoming_fixtures_through_2026-11-01.csv` — 25 scheduled fixtures through 1 November.
- `build_dashboard.py` — rebuilds the standalone page from the separate source files.
- `validate_championship.py` / `validation.json` / `validation.txt` / `validation_report.md` — reproducible reconciliation and its latest report.
- `source_log.json` — source URLs, cutoff, validation scope, and data limitations. Source URLs are retained; raw response snapshots were not present in the existing project files.

No `refresh_championship.py` updater is included in this package; the CSV sources must be refreshed and validated before rebuilding a later snapshot.

## Data policy and known limitations

- Official EFL standings are authoritative. EFL's live competition URL returned a stale 2023/24 table, so the current official EFL post-match article table was used instead. This is documented in the interface and source log.
- ESPN's public scoreboard was used as an independent match-level score feed. All scores in the frozen dataset were reported full-time and the resulting table reconciles exactly with the EFL table after the Southampton deduction.
- The official EFL site did not expose a stable, machine-readable full-season fixture table in this retrieval. The published upcoming window therefore uses ESPN's posted fixture list and is clearly bounded; it is not represented as the whole remaining season.
- The BBC standings page was consulted, but its extracted table removed the club labels, so it was not used as the row-level table cross-check.
- This is a data dashboard, not betting advice. Model estimates use small current-season samples.
