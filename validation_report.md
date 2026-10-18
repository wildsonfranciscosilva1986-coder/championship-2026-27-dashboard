# Validation report — EFL Championship 2026/27

**Snapshot cutoff:** 18 October 2026, 12:05 America/Sao_Paulo (BRT, UTC−03:00)

## Result

PASS. `python3 validate_championship.py` exits successfully and reconciles the match-derived table against both the official EFL standings and the independent ESPN table for all 24 clubs. Checked values: played, points after the official Southampton −4 adjustment, W–D–L, goals for, goals against, and goal difference.

## Coverage

- 131 completed fixtures, all marked `finished` with integer final scores; latest result date in the file is 17 October 2026.
- 24 Championship clubs.
- 25 scheduled upcoming fixtures, bounded to the published window 19 October–1 November 2026 (the actual rows range 20–31 October UTC).
- No fixture coverage beyond 1 November is represented.

## Build check

`python3 build_dashboard.py` succeeds and produces the standalone `index.html` (24 clubs; 156 completed plus scheduled match records). Two consecutive builds produced identical SHA-256: `0fae56083aa9c39b27bbb3eae5e31fb0dcb171cb75f085baa926c16d88ff0951`.

## Evidence and limitations

Source URLs, their roles, cutoff, row-level ESPN event links, and known source limitations are in `source_log.json`; raw upstream response snapshots were not present in the existing project files. The EFL live competition page returned stale historical standings, so the dated official EFL post-match table article is the official standings baseline. The bounded upcoming fixtures come from ESPN and are not a whole-season schedule. See `validation.json` for machine-readable results and `validation.txt` for the validator's text report.
