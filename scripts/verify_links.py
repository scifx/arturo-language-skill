#!/usr/bin/env python3
"""Recheck the stable or latest URLs in references/library-index.csv."""
import argparse, concurrent.futures, csv, pathlib, urllib.request, urllib.error
ROOT = pathlib.Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser(); p.add_argument('--latest', action='store_true'); p.add_argument('--workers', type=int, default=16); a=p.parse_args()
with (ROOT/'references/library-index.csv').open(encoding='utf-8', newline='') as f: rows=list(csv.DictReader(f))
key='latest_url' if a.latest else 'stable_url'
def one(r):
    u=r[key]
    try:
        q=urllib.request.Request(u, headers={'User-Agent':'ArturoSkillLinkCheck/1.0'})
        with urllib.request.urlopen(q, timeout=20) as x: return r['name'], x.status, u
    except urllib.error.HTTPError as e: return r['name'], e.code, u
    except Exception as e: return r['name'], type(e).__name__, u
with concurrent.futures.ThreadPoolExecutor(max_workers=a.workers) as ex: out=list(ex.map(one,rows))
bad=[x for x in out if x[1] != 200]
print(f'checked={len(out)} ok={len(out)-len(bad)} bad={len(bad)}')
for x in bad: print(*x, sep='\t')
raise SystemExit(bool(bad))
