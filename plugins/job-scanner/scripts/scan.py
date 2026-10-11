#!/usr/bin/env python3
"""Job Scanner: zero-LLM-cost job board scanner.

Usage:
  python3 scan.py config.json seen_keys.json out.json [--hours 14] [--intern-hours 72]
  python3 scan.py --check config.json          # verify every watchlist entry resolves

- config.json: the dashboard's engine/config doc (see references/config-schema.md)
- seen_keys.json: JSON list of url keys already scanned (from the dashboard's seen/* docs)
- out.json: written as {"jobs": [...], "new_keys": [...], "source_counts": {...}, "errors": [...]}

Sources (each can be switched off in config.sources):
  * company_boards: Ashby / Greenhouse / Lever / SmartRecruiters public job-board APIs for every watchlist company
  * simplify_newgrad: Simplify's public new-grad listings file on GitHub
  * simplify_internships: Simplify's public internship listings file, window --intern-hours
Only postings published within --hours and not already in seen_keys are returned.
Each job carries a plain-text description when the API gives one.
"""
import json, sys, time, re, html, hashlib, urllib.request, concurrent.futures as cf
import datetime as dt

DEFAULT_FEEDS = {
    'simplify_newgrad': 'https://raw.githubusercontent.com/SimplifyJobs/New-Grad-Positions/dev/.github/scripts/listings.json',
    'simplify_internships': 'https://raw.githubusercontent.com/SimplifyJobs/Summer2026-Internships/dev/.github/scripts/listings.json',
}
UA = {'User-Agent': 'Mozilla/5.0 (job-scanner; personal use)'}


def get(u):
    try:
        return json.load(urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=25))
    except Exception as e:
        return {'__err': str(e)[:120]}


def strip(s):
    return re.sub(r'\s+', ' ', re.sub('<[^>]+>', ' ', html.unescape(html.unescape(s or '')))).strip()


def key(url):
    u = re.sub(r'[?#].*$', '', (url or '').strip().lower()).rstrip('/')
    u = re.sub(r'^https?://(www\.)?', '', u)
    return hashlib.sha1(u.encode()).hexdigest()[:10]


def iso(ts):
    return ts.astimezone(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def board_url(ats, slug):
    return {
        'ashby': f'https://api.ashbyhq.com/posting-api/job-board/{slug}?includeCompensation=true',
        'greenhouse': f'https://boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=true',
        'lever': f'https://api.lever.co/v0/postings/{slug}?mode=json',
        'smartrecruiters': f'https://api.smartrecruiters.com/v1/companies/{slug}/postings?limit=100',
    }.get(ats)


def check(cfg_path):
    """Print ok/FAIL for every watchlist entry so setup can drop bad slugs."""
    cfg = json.load(open(cfg_path, encoding='utf-8'))
    def one(entry):
        ats, slug = entry[0], entry[1]
        u = board_url(ats, slug)
        if not u: return entry, 'FAIL unknown ats'
        r = get(u)
        if isinstance(r, dict) and '__err' in r: return entry, 'FAIL ' + r['__err']
        n = len(r) if isinstance(r, list) else len(r.get('jobs') or r.get('content') or [])
        return entry, f'ok ({n} open jobs)'
    with cf.ThreadPoolExecutor(20) as ex:
        for entry, res in ex.map(one, cfg.get('watchlist', [])):
            print(f'{entry[0]:16} {entry[1]:30} {res}')


def scan(cfg_path, seen_path, out_path, hours, intern_hours):
    cfg = json.load(open(cfg_path, encoding='utf-8'))
    seen = set(json.load(open(seen_path, encoding='utf-8')))
    sources = cfg.get('sources') or {}
    feeds = dict(DEFAULT_FEEDS, **(cfg.get('feeds') or {}))
    interns = cfg.get('internships') or {}
    now = dt.datetime.now(dt.timezone.utc)
    age_h = lambda ts: (now - ts).total_seconds() / 3600
    errors, jobs, counts = [], [], {}

    def pull(entry):
        ats, slug = entry[0], entry[1]
        out = []
        r = get(board_url(ats, slug) or '')
        if isinstance(r, dict) and '__err' in r:
            errors.append(f'{ats}/{slug}: {r["__err"]}'); return out
        if ats == 'ashby':
            for j in r.get('jobs', []):
                if not j.get('publishedAt'): continue
                t = dt.datetime.fromisoformat(j['publishedAt'].replace('Z', '+00:00'))
                if age_h(t) < hours:
                    comp = (j.get('compensation') or {}).get('compensationTierSummary') or ''
                    out.append(dict(source='ashby', company=slug, title=j['title'], location=j.get('location') or '',
                                    remote=bool(j.get('isRemote')), url=j['jobUrl'], posted_at=iso(t), salary=comp,
                                    desc=(j.get('descriptionPlain') or '')[:7000]))
        elif ats == 'greenhouse':
            for j in r.get('jobs', []):
                t = dt.datetime.fromisoformat(j.get('first_published') or j['updated_at'])
                if age_h(t) < hours:
                    out.append(dict(source='greenhouse', company=slug, title=j['title'], location=j['location']['name'],
                                    url=j['absolute_url'], posted_at=iso(t), salary='', desc=strip(j.get('content'))[:7000]))
        elif ats == 'lever':
            for j in r:
                t = dt.datetime.fromtimestamp(j['createdAt'] / 1000, dt.timezone.utc)
                if age_h(t) < hours:
                    d = (j.get('descriptionPlain') or '') + ' ' + ' '.join(strip(l.get('content')) for l in j.get('lists', []))
                    out.append(dict(source='lever', company=slug, title=j['text'], location=(j.get('categories') or {}).get('location') or '',
                                    url=j['hostedUrl'], posted_at=iso(t), salary='', desc=d[:7000]))
        elif ats == 'smartrecruiters':
            for j in r.get('content', []):
                if not j.get('releasedDate'): continue
                t = dt.datetime.fromisoformat(j['releasedDate'].replace('Z', '+00:00'))
                if age_h(t) < hours:
                    loc = j.get('location') or {}
                    out.append(dict(source='smartrecruiters', company=(j.get('company') or {}).get('name') or slug, title=j.get('name', ''),
                                    location=', '.join(x for x in [loc.get('city'), loc.get('region'), loc.get('country')] if x),
                                    remote=bool(loc.get('remote')), url=f'https://jobs.smartrecruiters.com/{slug}/{j["id"]}',
                                    posted_at=iso(t), salary='', desc=''))
        return out

    if sources.get('company_boards', True):
        with cf.ThreadPoolExecutor(20) as ex:
            for res in ex.map(pull, cfg.get('watchlist', [])):
                jobs += res

    if sources.get('simplify_newgrad', True):
        r = get(feeds['simplify_newgrad'])
        if isinstance(r, list):
            for x in r:
                if x.get('active') and x.get('is_visible') and (time.time() - x['date_posted']) < hours * 3600:
                    t = dt.datetime.fromtimestamp(x['date_posted'], dt.timezone.utc)
                    jobs.append(dict(source='simplify-data', company=x['company_name'], title=x['title'],
                                     location='; '.join(x.get('locations', [])), url=x['url'], posted_at=iso(t), salary='',
                                     sponsorship=x.get('sponsorship'), desc=''))
        else:
            errors.append('simplify-newgrad: ' + str(r.get('__err')))

    # Internship feed. internships.terms limits seasons (e.g. ["Winter", "Spring", "Fall"] for off-season only).
    if sources.get('simplify_internships', bool(interns.get('include'))):
        want_terms = set(interns.get('terms') or [])
        r = get(feeds['simplify_internships'])
        if isinstance(r, list):
            for x in r:
                terms = x.get('terms') or []
                if want_terms and not [t for t in terms if t.split(' ')[0] in want_terms]: continue
                if x.get('active') and x.get('is_visible') and (time.time() - x['date_posted']) < intern_hours * 3600:
                    t = dt.datetime.fromtimestamp(x['date_posted'], dt.timezone.utc)
                    jobs.append(dict(source='simplify-intern', company=x['company_name'], title=x['title'],
                                     location='; '.join(x.get('locations', [])), url=x['url'], posted_at=iso(t), salary='',
                                     sponsorship=x.get('sponsorship'), terms=terms, category=x.get('category'),
                                     internship=True, desc=''))
        else:
            errors.append('simplify-internships: ' + str(r.get('__err')))

    uniq, new_keys = {}, []
    for j in jobs:
        k = key(j['url'])
        if k in seen or k in uniq: continue
        j['key'] = k
        uniq[k] = j
        new_keys.append(k)
    for j in uniq.values():
        counts[j['source']] = counts.get(j['source'], 0) + 1
    json.dump({'jobs': list(uniq.values()), 'new_keys': new_keys, 'source_counts': counts,
               'errors': errors, 'window_hours': hours, 'scanned_at': iso(now)}, open(out_path, 'w', encoding='utf-8'))
    print(f'new jobs: {len(uniq)}  by source: {counts}  errors: {len(errors)}')
    for j in sorted(uniq.values(), key=lambda j: j['posted_at'], reverse=True):
        print(f"{j['key']} | {j['source'][:6]} | {j['company'][:20]:20} | {j['title'][:60]:60} | {str(j['location'])[:35]}")


if __name__ == '__main__':
    args = sys.argv[1:]
    if args and args[0] == '--check':
        check(args[1]); sys.exit(0)
    hours, intern_hours = 14.0, 72.0
    if '--hours' in args:
        i = args.index('--hours'); hours = float(args[i + 1]); del args[i:i + 2]
    if '--intern-hours' in args:
        i = args.index('--intern-hours'); intern_hours = float(args[i + 1]); del args[i:i + 2]
    scan(*args[:3], hours, intern_hours)
