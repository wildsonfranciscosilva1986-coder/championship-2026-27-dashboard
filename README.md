# English Championship 2026/27 — DIN Mercado Dashboard

Standalone mobile-first Championship dashboard with a daily validated refresh. It stays separate from the Premier League and every other division.

## Automatic update

GitHub Actions runs daily at 06:13 BRT and can also be started manually. The workflow fetches the ESPN match scoreboard by each date in the published season calendar, accepts only `STATUS_FULL_TIME` events with `completed=true` and integer scores, loads the current rendered EFL Championship table, and reconciles all 24 clubs (P/W/D/L/GF/GA/GD/points, with Southampton's official −4 deduction). It stops before modifying files or publishing if the EFL page fails, club/season checks fail, an existing final conflicts, or any score-derived field differs from the current official EFL table. Scheduled/postponed matches remain unscored. On successful validation the standalone page and snapshot files are committed to the existing Pages repository.

A separate daily Zapia job runs at 06:43 BRT (after the GitHub refresh), copies the already-published, validated `index.html` to the private Google Drive folder `DIN Mercado — Championship 2026-27`, replaces the same Drive file, then downloads it and verifies SHA-256. It does not upload unless the same-day GitHub run succeeded and the public cutoff matches the validated metadata.

## Manual build and validation

```bash
python -m pip install -r requirements.txt
python -m playwright install chromium
python refresh_championship.py
python build_dashboard.py
python validate_championship.py
```

The refresh command fails closed before replacing source files unless it can read 24 current EFL table rows and reconcile the score-derived table. The Southampton four-point deduction is applied only to points, never to match W-D-L. Final scores are accepted only with explicit ESPN full-time status; postponed/live/unplayed games stay out of statistics.

## Scope and limitations

The full-season 552-match pairing list is not represented as complete. Upcoming fixtures shown are only the current ESPN-published horizon, which can change and is not represented as the whole season. The EFL official table is accessed through the live rendered page with Playwright; the refresh fails closed if that page cannot yield all 24 rows or the score-derived table differs. Results come from the ESPN match-level scoreboard and are reconciled against the rendered official EFL table; ESPN's live standings may lag and are not used as the authoritative table. Matchup rates are descriptive early-season estimates, not betting advice.
