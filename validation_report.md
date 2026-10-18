# Validation report — EFL Championship 2026/27

**Snapshot cutoff:** 18 October 2026, 12:05 America/Sao_Paulo (BRT, UTC−03:00)

## Result

PASS. `python3 validate_championship.py` exits successfully and reconciles the match-derived table against both the official EFL standings and the independent ESPN table for all 24 clubs. Checked values: played, points after the official Southampton −4 adjustment, W–D–L, goals for, goals against, and goal difference.

## Coverage

- 131 completed fixtures, all marked `finished` with integer final scores; latest result date in the file is 17 October 2026.
- 24 Championship clubs.
- 25 scheduled upcoming fixtures, bounded to the published window 19 October–1 November 2026 (the actual rows range 20–31 October UTC).
- No fixture coverage beyond 1 November is represented.

## Dashboard feature/build check

`python3 build_dashboard.py` succeeds and produces the standalone `index.html` (24 clubs; 131 completed + 25 scheduled = 156 available match records). The overview now includes 131/552 completed/season fixtures; 378 goals and 2.89 goals per match; BTTS 83/131 (63.4%); Over 2.5 81/131 (61.8%); and home/draw/away results 52/36/43. The new Fixtures tab browses all available records with status and club filters. Existing club profiles, venue splits, form, rankings, H2H and matchup estimates remain. The generated HTML SHA-256 is `d3ce5848159926ce47368004ee74615f6c76bf15244ce0880a6431e4278613dc`.

## Evidence and limitations

Source URLs, their roles, cutoff, row-level ESPN event links, and known source limitations are in `source_log.json`; raw upstream response snapshots were not present in the existing project files. The EFL live competition page returned stale historical standings, so the dated official EFL post-match table article is the official standings baseline. The bounded upcoming fixtures come from ESPN and are not a whole-season schedule. See `validation.json` for machine-readable results and `validation.txt` for the validator's text report.
