# Validation report — EFL Championship 2026/27

**Snapshot cutoff:** 20 October 2026, 13:38:26 America/Sao_Paulo (BRT, UTC−03:00)

## Result

PASS. `python3 validate_championship.py` exits successfully and reconciles the match-derived table against both the official EFL standings and the independent ESPN table for all 24 clubs. Checked values: played, points after the official Southampton −4 adjustment, W–D–L, goals for, goals against, and goal difference.

## Coverage

- 131 completed fixtures, all marked `finished` with integer final scores; latest result date in the file is 17 October 2026.
- 24 Championship clubs.
- 25 scheduled upcoming fixtures, bounded through 1 November 2026 (the actual rows range 20–31 October UTC).
- No fixture coverage beyond 1 November is represented.

## Dashboard feature/build check

`python3 build_dashboard.py` succeeds and produces the standalone `index.html` (24 clubs; 131 completed + 25 scheduled = 156 available match records). The overview now includes 131/552 completed/season fixtures; 378 goals and 2.89 goals per match; BTTS 83/131 (63.4%); Over 2.5 81/131 (61.8%); and home/draw/away results 52/36/43. The new Fixtures tab browses all available records with status and club filters. Existing club profiles, venue splits, form, rankings, H2H and matchup estimates remain. The generated `index.html` is 62,575 bytes; SHA-256 `62b5717c1041ce777b99e202ceb9ba18ee82132ddd0922165a15399217c2209c`.

## Evidence and limitations

Source URLs, their roles, cutoff, row-level ESPN event links, and known source limitations are in `source_log.json`; raw upstream response snapshots were not present in the existing project files. The EFL live competition page returned stale historical standings; the latest official 18 October post-match table article, fetched again on 20 October, is the official standings baseline. Its 24 rows match the saved EFL table snapshot. ESPN standings and the near-term schedule page were also fetched 20 October at 13:38 BRT; the 20 October Wolves–Portsmouth match remained scheduled at cutoff. The ESPN table and results-derived table agree with the official 18 October table for all 24 clubs after the Southampton deduction. The bounded upcoming fixtures come from ESPN and are not a whole-season schedule. See `validation.json` for machine-readable results and `validation.txt` for the validator's text report.
