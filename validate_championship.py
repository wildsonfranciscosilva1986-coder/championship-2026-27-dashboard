#!/usr/bin/env python3
"""Validate Championship 2026/27 final-score dataset against EFL and ESPN tables."""
import csv, json, collections
from pathlib import Path
ROOT=Path(__file__).parent
D=ROOT/'data'
cutoff='2026-10-18 12:05 America/Sao_Paulo'
def read(name):
    with open(D/name,encoding='utf-8',newline='') as f: return list(csv.DictReader(f))
fixtures=read('fixtures_results_2026_27.csv')
efl=read('efl_official_table.csv')
espn=read('independent_espn_table.csv')
assert len(efl)==24 and len(espn)==24, 'Expected 24 clubs in both source tables'
assert len({r['fixture_id'] for r in fixtures})==len(fixtures), 'Duplicate fixture ids'
clubs={r['team'] for r in efl}
assert {r['team'] for r in espn}==clubs, 'Independent source club set differs'
assert len(fixtures)==131, f'Expected the 131 fixtures played in the current snapshot, got {len(fixtures)}'
assert all(r['status']=='finished' for r in fixtures), 'Only confirmed final scores belong in this file'
assert all(r['home'] in clubs and r['away'] in clubs for r in fixtures), 'Foreign club / division contamination'
assert all(r['home_goals'].isdigit() and r['away_goals'].isdigit() for r in fixtures), 'Invalid final score'
calc={t:dict(P=0,W=0,D=0,L=0,GF=0,GA=0,PTS=0) for t in clubs}
for r in fixtures:
    hg,ag=int(r['home_goals']),int(r['away_goals'])
    for t,gf,ga in ((r['home'],hg,ag),(r['away'],ag,hg)):
        x=calc[t]; x['P']+=1; x['GF']+=gf; x['GA']+=ga
        if gf>ga: x['W']+=1; x['PTS']+=3
        elif gf==ga: x['D']+=1; x['PTS']+=1
        else: x['L']+=1
# EFL officially applied a four-point deduction to Southampton for 2026/27.
deductions={'Southampton':-4}
fields={'P':'played','W':'won','D':'drawn','L':'lost','GF':'goals_for','GA':'goals_against','PTS':'points'}
errors=[]
for official in efl:
    team=official['team']; s=calc[team]
    for k,col in fields.items():
        got=s[k]+(deductions.get(team,0) if k=='PTS' else 0)
        if got!=int(official[col]): errors.append(f'EFL {team} {col}: computed {got}, source {official[col]}')
for row in espn:
    team=row['team']; s=calc[team]
    for k,col in fields.items():
        got=s[k]+(deductions.get(team,0) if k=='PTS' else 0)
        if got!=int(row[col]): errors.append(f'ESPN {team} {col}: computed {got}, source {row[col]}')
# EFL and ESPN summary tables also must agree field-for-field.
for a,b in zip(efl,espn):
    for f in ['played','won','drawn','lost','goals_for','goals_against','goal_difference','points']:
        if a[f]!=b[f]: errors.append(f'EFL/ESPN mismatch {a["team"]} {f}: {a[f]} vs {b[f]}')
assert not errors, '\n'.join(errors)
report={
 'competition':'EFL Championship','season':'2026/27','cutoff_local':cutoff,
 'completed_fixtures':len(fixtures),'clubs':len(clubs),'score_status':'all final only',
 'southampton_points_adjustment':-4,'derived_table_matches_efl_and_espn':True,
 'checked_fields':['played','points (deduction-adjusted)','W','D','L','GF','GA','GD'],
 'upcoming_rows':len(read('upcoming_fixtures_through_2026-11-01.csv')),
 'limitations':['Upcoming schedule coverage is through 2026-11-01 only.','EFL live competition page returned stale historical table data; current official EFL post-match table article was used for the official standings.','ESPN schedule/match feed provided independent score and near-term fixture records.']}
(ROOT/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
(ROOT/'validation.txt').write_text('PASS — '+json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
