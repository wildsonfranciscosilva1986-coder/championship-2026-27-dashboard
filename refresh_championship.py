#!/usr/bin/env python3
"""Refresh Championship scores from ESPN FT events and reconcile all clubs to EFL.
Fails closed before changing input CSVs if official standings or score reconciliation fail.
"""
from __future__ import annotations
import csv, datetime as dt, json, re, concurrent.futures
from pathlib import Path
from zoneinfo import ZoneInfo
import requests
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parent
DATA=ROOT/'data'
EFL_URL='https://www.efl.com/competitions/efl-championship/'
ESPN='https://site.api.espn.com/apis/site/v2/sports/soccer/eng.2/scoreboard'
LOCAL_TZ=ZoneInfo('America/Sao_Paulo')
UTC=dt.timezone.utc

def read_csv(path):
    with path.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def write_csv(path,rows,fields):
    with path.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
def fetch_json(url):
    r=requests.get(url,headers={'User-Agent':'DIN-Mercado-Championship-Dashboard/1.0'},timeout=40);r.raise_for_status();return r.json()
def current_efl_table(club_names):
    """Read the live rendered EFL table, not stale cached standings or search text."""
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True)
        page=browser.new_page()
        page.goto(EFL_URL,wait_until='domcontentloaded',timeout=90000)
        try: page.get_by_role('button',name=re.compile('accept essential',re.I)).click(timeout=8000)
        except Exception: pass
        page.get_by_role('heading',name=re.compile('EFL Championship',re.I)).wait_for(timeout=30000)
        page.get_by_role('heading',name=re.compile('League Table',re.I)).wait_for(timeout=30000)
        page.wait_for_function("document.querySelectorAll('table tr').length >= 25",timeout=30000)
        html=page.content(); raw=page.locator('table tr').all_inner_texts(); browser.close()
    matches=[]
    for line in raw:
        line=' '.join(line.split())
        found=[club for club in club_names if re.search(r'(?<![A-Za-z])'+re.escape(club)+r'(?![A-Za-z])',line)]
        if len(found)!=1:continue
        team=found[0]; before,after=line.split(team,1)
        position=re.findall(r'\d+',before)
        nums=re.findall(r'(?<![A-Za-z])-?\d+(?![A-Za-z])',after)
        if not position or len(nums)<8:continue
        played,won,drawn,lost,gf,ga,gd,points=map(int,nums[:8])
        matches.append({'position':int(position[-1]),'team':team,'played':played,'won':won,'drawn':drawn,'lost':lost,'goals_for':gf,'goals_against':ga,'goal_difference':gd,'points':points})
    if len(matches)!=24 or len({x['team'] for x in matches})!=24:
        raise RuntimeError(f'EFL live table not parsed as 24 unique clubs (got {len(matches)}); refusing refresh')
    matches.sort(key=lambda x:x['position'])
    return matches,html

def main():
    now=dt.datetime.now(UTC).replace(microsecond=0)
    old_finals=read_csv(DATA/'fixtures_results_2026_27.csv')
    old_official=read_csv(DATA/'efl_official_table.csv')
    clubs={x['team'] for x in old_official} | {x['home'] for x in old_finals} | {x['away'] for x in old_finals}
    if len(clubs)!=24: raise RuntimeError(f'expected 24 Championship clubs, got {len(clubs)}')
    # Calendar endpoint defines the season's currently published dates and horizon.
    anchor=fetch_json(ESPN+'?dates='+now.strftime('%Y%m%d'))
    league=anchor['leagues'][0]
    if league.get('id')!='3914' or league.get('season',{}).get('year')!=2026: raise RuntimeError('wrong ESPN league/season')
    dates=sorted({dt.date.fromisoformat(x[:10]) for x in league.get('calendar',[])})
    if not dates:raise RuntimeError('ESPN returned no season calendar')
    def date_fetch(day):
        j=fetch_json(ESPN+'?dates='+day.strftime('%Y%m%d'))
        if j['leagues'][0].get('id')!='3914' or j['leagues'][0].get('season',{}).get('year')!=2026:raise RuntimeError('wrong ESPN date payload '+str(day))
        return day,j
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        payloads=list(pool.map(date_fetch,dates))
    final_map={x['fixture_id']:x for x in old_finals}
    scheduled_map={}
    source_counts=[]
    for day,j in payloads:
        source_counts.append({'date':str(day),'event_count':len(j.get('events',[]))})
        for e in j.get('events',[]):
            if str(e.get('season',{}).get('year'))!='2026':raise RuntimeError('season mismatch on '+str(e.get('id')))
            c=e['competitions'][0]; status=c['status']['type']; sides={x['homeAway']:x for x in c['competitors']}
            if set(sides)!={'home','away'}:raise RuntimeError('missing home/away for '+str(e.get('id')))
            h,a=sides['home'],sides['away']; eid=str(e['id']); name=status.get('name','')
            if h['team']['displayName'] not in clubs or a['team']['displayName'] not in clubs:raise RuntimeError('foreign club/division event '+eid)
            row={'fixture_id':eid,'date_utc':e['date'],'home':h['team']['displayName'],'away':a['team']['displayName'],'home_goals':'','away_goals':'','status':'','source_url':'https://www.espn.com/soccer/match/_/gameId/'+eid}
            if name=='STATUS_FULL_TIME' and status.get('completed') is True:
                if not str(h.get('score','')).isdigit() or not str(a.get('score','')).isdigit():raise RuntimeError('FT event has missing scores '+eid)
                row.update(home_goals=str(h['score']),away_goals=str(a['score']),status='finished')
                if eid in final_map:
                    old=final_map[eid]
                    if (old['home'],old['away'])!=(row['home'],row['away']):raise RuntimeError('event id orientation changed '+eid)
                    if old['home_goals'] and (old['home_goals'],old['away_goals'])!=(row['home_goals'],row['away_goals']):raise RuntimeError('previous FT score changed '+eid)
                final_map[eid]=row
            elif not status.get('completed') and name in ('STATUS_SCHEDULED','STATUS_POSTPONED','STATUS_DELAYED','STATUS_CANCELED'):
                row['status']={'STATUS_SCHEDULED':'scheduled','STATUS_POSTPONED':'postponed','STATUS_DELAYED':'scheduled','STATUS_CANCELED':'postponed'}[name]
                if dt.datetime.fromisoformat(e['date'].replace('Z','+00:00'))>now:scheduled_map[eid]=row
                elif row['status']=='postponed':scheduled_map[eid]=row
                # A scheduled match whose original kickoff has passed but has no FT state stays pending for reconciliation, not as a final.
    if len(final_map)>552:raise RuntimeError('more than 552 final games')
    if len(final_map)<145:raise RuntimeError('final-result coverage dropped unexpectedly')
    if len(final_map)<len(old_finals):raise RuntimeError(f'final-score event count dropped from {len(old_finals)} to {len(final_map)}; refusing to overwrite prior verified rows')
    if len(scheduled_map)<min(10,len(read_csv(DATA/'scheduled_fixtures_current.csv'))):raise RuntimeError(f'published scheduled-fixture count dropped unexpectedly ({len(scheduled_map)}); refusing update')
    if {r['home'] for r in final_map.values()}|{r['away'] for r in final_map.values()} != clubs:raise RuntimeError('final result set omits Championship clubs')
    if len({(r['home'],r['away']) for r in final_map.values()})!=len(final_map):raise RuntimeError('duplicate home/away pair in finals')
    if len(final_map)+len(scheduled_map)>552:raise RuntimeError('fixture count exceeds 552-season size')
    if len({(r['home'],r['away']) for r in final_map.values()})!=len(final_map):raise RuntimeError('duplicate team pairing among final results')
    table,efl_html=current_efl_table(clubs)
    calc={t:{'played':0,'won':0,'drawn':0,'lost':0,'goals_for':0,'goals_against':0,'points':0} for t in clubs}
    for r in final_map.values():
        hg,ag=int(r['home_goals']),int(r['away_goals'])
        for team,gf,ga in ((r['home'],hg,ag),(r['away'],ag,hg)):
            x=calc[team];x['played']+=1;x['goals_for']+=gf;x['goals_against']+=ga
            if gf>ga:x['won']+=1;x['points']+=3
            elif gf==ga:x['drawn']+=1;x['points']+=1
            else:x['lost']+=1
    calc['Southampton']['points']-=4
    fields=['played','won','drawn','lost','goals_for','goals_against','goal_difference','points']
    errors=[]
    for row in table:
        x=calc[row['team']];x['goal_difference']=x['goals_for']-x['goals_against']
        for f in fields:
            if x[f]!=row[f]:errors.append(f"{row['team']} {f}: scores {x[f]} vs EFL {row[f]}")
    if errors:raise RuntimeError('EFL current-table reconciliation failed: '+'; '.join(errors[:60]))
    official_rows=[]
    for r in table:
        official_rows.append({'position':int(r['position']),'team':r['team'],**{f:r[f] for f in fields}})
    # Persist only after every source and table check passes.
    fin_fields=['fixture_id','date_utc','home','away','home_goals','away_goals','status','source_url']
    finals=sorted(final_map.values(),key=lambda x:(x['date_utc'],x['fixture_id']))
    upcoming=sorted(scheduled_map.values(),key=lambda x:(x['date_utc'],x['fixture_id']))
    write_csv(DATA/'fixtures_results_2026_27.csv',finals,fin_fields)
    write_csv(DATA/'scheduled_fixtures_current.csv',upcoming,fin_fields)
    write_csv(DATA/'efl_official_table.csv',official_rows,['position','team']+fields)
    # Current official table is the accepted authority; keep a separately named score-recomputed view, not mislabeled as ESPN standings.
    derived=[]
    for r in official_rows:
        x=calc[r['team']];derived.append({'team':r['team'],**{f:x[f] for f in fields}})
    write_csv(DATA/'independent_espn_table.csv',derived,['team']+fields)
    brt=now.astimezone(LOCAL_TZ)
    horizon=max((dt.date.fromisoformat(r['date_utc'][:10]) for r in upcoming),default=now.date())
    meta={'competition':'EFL Championship','season':'2026/27','cutoff_brt':brt.isoformat(timespec='minutes'),'cutoff_utc':now.isoformat(),'finished':len(finals),'upcoming':len(upcoming),'coverage_horizon':str(horizon),'official_table_source':EFL_URL,'official_table_reconciliation':'PASS: all 24 clubs match score-derived P/W/D/L/GF/GA/GD/points after official Southampton -4 deduction','score_source':'ESPN public scoreboard per season calendar date; status STATUS_FULL_TIME and completed=true required','calendar_source':'ESPN published Championship calendar; near-term only, not a full official season pairing list','queried_dates':source_counts,'pending_or_postponed':'not scored or included in match-derived metrics'}
    (DATA/'refresh_metadata.json').write_text(json.dumps(meta,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    (ROOT/'source_snapshots').mkdir(exist_ok=True)
    (ROOT/'source_snapshots'/('efl_standings_'+now.strftime('%Y%m%dT%H%M%SZ')+'.html')).write_text(efl_html,encoding='utf-8')
    print(json.dumps(meta,indent=2,ensure_ascii=False))
if __name__=='__main__':main()
