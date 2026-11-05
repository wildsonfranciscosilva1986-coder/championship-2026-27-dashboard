#!/usr/bin/env python3
"""Validate live Championship snapshot against rendered official EFL standings."""
import csv,json
from pathlib import Path
ROOT=Path(__file__).parent;D=ROOT/'data'
def read(n):
 with (D/n).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f))
fixtures=read('fixtures_results_2026_27.csv');upcoming=read('scheduled_fixtures_current.csv');efl=read('efl_official_table.csv');meta=json.loads((D/'refresh_metadata.json').read_text(encoding='utf8'))
assert len(efl)==24 and len({r['team'] for r in efl})==24,'EFL table must have 24 unique clubs'
clubs={r['team'] for r in efl}
assert len(fixtures)==meta['finished'] and len(upcoming)==meta['upcoming']
ids=[r['fixture_id'] for r in fixtures+upcoming];assert len(ids)==len(set(ids)),'Duplicate fixture IDs'
assert all(r['status']=='finished' and r['home_goals'].isdigit() and r['away_goals'].isdigit() for r in fixtures),'Non-final or malformed score in results'
assert all(r['status'] in ('scheduled','postponed') and not r['home_goals'] and not r['away_goals'] for r in upcoming),'Unfinished schedule has inferred score or wrong state'
assert all(r['home'] in clubs and r['away'] in clubs for r in fixtures+upcoming),'Club outside current EFL Championship'
assert 145<=len(fixtures)<=552
calc={t:{k:0 for k in ['played','won','drawn','lost','goals_for','goals_against','points']} for t in clubs}
for r in fixtures:
 hg,ag=int(r['home_goals']),int(r['away_goals'])
 for team,gf,ga in [(r['home'],hg,ag),(r['away'],ag,hg)]:
  x=calc[team];x['played']+=1;x['goals_for']+=gf;x['goals_against']+=ga
  if gf>ga:x['won']+=1;x['points']+=3
  elif gf==ga:x['drawn']+=1;x['points']+=1
  else:x['lost']+=1
calc['Southampton']['points']-=4
fields=['played','won','drawn','lost','goals_for','goals_against','goal_difference','points']
for r in efl:
 x=calc[r['team']];x['goal_difference']=x['goals_for']-x['goals_against']
 for k in fields:assert x[k]==int(r[k]),f"EFL mismatch {r['team']} {k}: computed {x[k]}, official {r[k]}"
assert meta['official_table_source'].startswith('https://www.efl.com/competitions/efl-championship')
html=(ROOT/'index.html').read_text(encoding='utf8')
assert meta['cutoff_brt'][:10] in meta['cutoff_brt']
assert meta['finished']==len(fixtures)
assert '131 matches' not in html and '1 November 2026' not in html and '18 October 2026' not in html
assert '2026-' in html and 'scheduled fixtures / season total' in html
assert 'const CUTOFF=Date.parse(' in html and '2026-10-18T15:05:00Z' not in html
for marker in ['homeSelect','awaySelect','matchupResult','clubSelect','fixtureStatus','tableBody']:
 assert f'id="{marker}"' in html,f'missing UI element {marker}'
assert html.count('EFL Championship')>=1
import re
m=re.search(r'const MATCHES=(\[.*?\]);\s*const CUTOFF=',html,re.S)
assert m,'dashboard data payload missing'
payload=json.loads(m.group(1))
assert len(payload)==len(fixtures)+len(upcoming)
assert sum(x['status']=='finished' for x in payload)==len(fixtures)
assert sum(x['status']=='scheduled' for x in payload)==sum(x['status']=='scheduled' for x in upcoming)
assert all(x['status'] in ('scheduled','postponed') and x['hg'] is None and x['ag'] is None for x in payload if x['status']!='finished')
report={'competition':'EFL Championship','season':'2026/27','cutoff_brt':meta['cutoff_brt'],'finished':len(fixtures),'scheduled':len(upcoming),'clubs':24,'official_EFL_reconciliation':'PASS 24/24','unique_fixture_ids':'PASS','FT_status_and_scores':'PASS','unplayed_scores_blank':'PASS','Southampton_deduction':-4,'score_source':'ESPN individual scoreboard dates; STATUS_FULL_TIME and completed=true','standings_source':'EFL rendered official Championship table'}
(ROOT/'validation.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
(ROOT/'validation.txt').write_text('PASS — '+json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
print(json.dumps(report,indent=2,ensure_ascii=False))
