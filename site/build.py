"""Build the public Open Data Centers website from data/ into public/.

Usage:
  python site/build.py            # build public/
  python site/build.py --check    # build, then check links, titles and sitemap
Env:
  SITE_URL   absolute base URL for canonical links and the sitemap (default below)
  REPO_URL   link to the public source repo, shown in the header and footer (optional)
"""
import datetime as dt
import glob
import html
import json
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "public")
SITE_URL = os.environ.get("SITE_URL", "https://opendatacenters.vercel.app").rstrip("/")
REPO_URL = os.environ.get("REPO_URL", "https://github.com/sheikhshessi-10/open-data-centers")
TODAY = dt.date.today().isoformat()
sys.path.insert(0, HERE)
from pins import APPROX  # noqa: E402  town-center pins for sites without exact coordinates
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import registry  # noqa: E402  covered states come from data/states/registry.json

REG = registry.by_code()
STATE_NAMES = {c: st["name"] for c, st in REG.items()}


_names = [st["name"] for st in REG.values()]
MANY = len(_names) > 6  # past a handful of states, nav and filters switch to a states index and a dropdown
STATES_TEXT = ("the United States" if len(_names) >= 50 else
               " and ".join(_names) if len(_names) < 3 else ", ".join(_names[:-1]) + " and " + _names[-1])


def county_word(code, plural=False):
    w = REG[code]["county_word"]
    return (w[:-1] + "ies" if w.endswith("y") else w + "es" if w.endswith("h") else w + "s") if plural else w
STAGE_LABEL = {"announced": "Announced", "permitted": "Permitted", "building": "Building", "running": "Running",
               "paused": "Paused", "blocked": "Blocked", "cancelled": "Cancelled", "closed": "Closed"}
ITEMS = [("power_use", "Power use"), ("water_use", "Water use"), ("power_source", "Power source"),
         ("tax_break_size", "Tax break size"), ("jobs_promised_vs_actual", "Jobs promised vs real"),
         ("noise_tests", "Noise tests"), ("air_permits", "Air permits"), ("community_deal", "Deal with the town")]
METRICS = [("investment_usd", "Money invested"), ("power_mw", "Power"), ("water_use", "Water use"),
           ("power_source", "Power source"), ("cooling_type", "Cooling"), ("utility", "Power company"),
           ("acres", "Land"), ("jobs_promised_build", "Building jobs promised"),
           ("jobs_promised_perm", "Long-term jobs promised"), ("jobs_actual", "Jobs so far"),
           ("tax_break", "Tax break"), ("local_tax_paid", "Local tax paid"), ("community_deal", "Deal with the town")]
e = html.escape


# ---------- data ----------
def slug(s):
    s = re.sub(r"[^a-z0-9]+", "-", (s or "").lower()).strip("-")
    return s or "unknown"


def short_name(s):
    # Keep the part in brackets when two sites would otherwise share a name (e.g. three Google Chesterfield campuses).
    return s["name"] if s.get("_same_short") else s["name"].split(" (")[0]


def num(s, k):
    m = (s.get("metrics") or {}).get(k)
    return m["value"] if m and isinstance(m.get("value"), (int, float)) else 0


def money(v):
    if v >= 1e12:
        return f"${v / 1e12:.1f} trillion"
    if v >= 1e9:
        return f"${v / 1e9:.0f}B" if v >= 1e10 else f"${v / 1e9:.1f}B".replace(".0B", "B")
    if v >= 1e6:
        return f"${v / 1e6:.0f}M"
    return f"${v:,.0f}"


def load():
    sites = registry.load_sites()
    states = {}
    for st in STATE_NAMES:
        p = os.path.join(ROOT, "data", "states", f"{st}.json")
        states[st] = json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}
    shorts = {}
    for s in sites:
        shorts.setdefault(s["name"].split(" (")[0], []).append(s)
    for group in shorts.values():
        if len(group) > 1:
            for s in group:
                s["_same_short"] = True
    used = set()
    for s in sites:
        if s.get("lat") is None and s["id"] in APPROX:
            s["lat"], s["lng"] = APPROX[s["id"]]
            s["approx"] = True
        s["county_name"] = s.get("county") or (s.get("town") or "Unknown area").split(" (")[0]
        s["county_fips"] = registry.county_fips(s["state"], s.get("county"))
        st_slug = REG[s["state"]]["slug"]
        c_slug = slug(s["county_name"])
        base = slug(re.sub(r"^(AWS|Amazon / STACK|CleanSpark|xAI / MZX Tech)\s+", "", short_name(s)))[:60].strip("-")
        url = f"/{st_slug}/{c_slug}/{base}/"
        n = 2
        while url in used:
            url = f"/{st_slug}/{c_slug}/{base}-{n}/"
            n += 1
        used.add(url)
        s["url"] = url
        s["county_url"] = f"/{st_slug}/{c_slug}/"
        s["state_url"] = f"/{st_slug}/"
    return sites, states


# ---------- shared pieces ----------
def shell(title, desc, path, body, scripts="", jsonld=None):
    canon = SITE_URL + path
    repo = f'<a href="{e(REPO_URL)}">Source</a>' if REPO_URL else ""
    ld = f'<script type="application/ld+json">{json.dumps(jsonld)}</script>' if jsonld else ""
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{e(canon)}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{e(canon)}">
<meta property="og:type" content="website">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@600;700&family=IBM+Plex+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap">
<link rel="stylesheet" href="/assets/style.css">
{ld}
</head>
<body>
<header class="top"><div class="wrap">
  <a class="logo" href="/"><i></i>Open Data Centers</a>
  <span class="pill">{"US" if len(REG) >= 50 else " + ".join(REG)}</span>
  <nav class="main"><a href="/">Map</a>{'<a href="/states/">States</a>' if MANY else "".join(f'<a href="/{st["slug"]}/">{e(st["name"])}</a>' for st in REG.values())}<a href="/about/">About</a>{repo}</nav>
</div></header>
<main class="wrap">
{body}
</main>
<footer><div class="wrap">Open Data Centers is an open source, public record. Every number links to its source and is tagged real or estimate; unknown stays blank. Data: CC BY 4.0. Code: MIT. {f'<a href="{e(REPO_URL)}">Help improve it</a>.' if REPO_URL else ''} Last built {TODAY}.</div></footer>
<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.9.0/d3.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/topojson-client@3.1.0/dist/topojson-client.min.js"></script>
<script src="/assets/enhance.js"></script>
{scripts}
</body>
</html>
"""


def link(url, text):
    if isinstance(url, str) and url.startswith(("http://", "https://")):
        return f'<a href="{e(url)}" rel="noopener">{e(text)}</a>'
    return e(text)


def host(u):
    m = re.match(r"https?://(?:www\.)?([^/]+)", u or "")
    return m.group(1) if m else ""


def bgsvg(s, w=400, h=340):
    # Gradient background; enhance.js draws the county outline on top.
    return (f'<svg class="bgsvg" viewBox="0 0 {w} {h}" preserveAspectRatio="xMidYMid slice" aria-hidden="true" '
            f'data-state="{e(s["state"])}" data-fips="{REG[s["state"]]["fips"]}" data-county="{e(s.get("county") or "")}" data-cfips="{s.get("county_fips") or ""}" data-lat="{s.get("lat") or ""}" '
            f'data-lng="{s.get("lng") or ""}" data-stage="{e(s["stage"])}"><rect width="{w}" height="{h}" class="stagefill-{e(s["stage"])}"/></svg>')


def numstr(v):
    # Same text JavaScript's String(v) gives, so client-rendered cards match these byte for byte.
    return str(int(v)) if float(v).is_integer() else repr(v)


def card_data(s, rank):
    # Everything a card shows, precomputed once. card() renders it here; home.js renders the same fields from cards.json.
    inv, mw = num(s, "investment_usd"), num(s, "power_mw")
    return {"id": s["id"], "r": rank, "url": s["url"], "st": s["state"], "fips": REG[s["state"]]["fips"],
            "county": s.get("county") or "", "cfips": s.get("county_fips") or "", "lat": s.get("lat") or "", "lng": s.get("lng") or "",
            "stage": s["stage"], "q": " ".join(str(x or "") for x in (s.get("name"), s.get("owner"), s.get("county"), s.get("town"))).lower(),
            "inv": inv, "mw": mw, "push": len(s.get("opposition") or []), "data": filled(s), "news": len(s.get("news") or []),
            "n": short_name(s), "mn": s["name"].split(" (")[0], "owner": s.get("owner") or "",
            "where": f'{s["county_name"]}, {STATE_NAMES[s["state"]]}',
            "m": money(inv) if inv else "$ unknown", "p": f"{mw:,.0f} MW" if mw else "MW unknown",
            "b": [[round(w * 100), c, t] for _, w, c, t in bar_rows(s)]}


def card_html(d):
    lat, lng = (numstr(d[k]) if d[k] != "" else "" for k in ("lat", "lng"))
    svg = (f'<svg class="bgsvg" viewBox="0 0 400 340" preserveAspectRatio="xMidYMid slice" aria-hidden="true" '
           f'data-state="{e(d["st"])}" data-fips="{d["fips"]}" data-county="{e(d["county"])}" data-cfips="{d["cfips"]}" data-lat="{lat}" '
           f'data-lng="{lng}" data-stage="{e(d["stage"])}"><rect width="400" height="340" class="stagefill-{e(d["stage"])}"/></svg>')
    data = (f'data-id="{e(d["id"])}" data-state="{d["st"]}" data-stage="{e(d["stage"])}" data-q="{e(d["q"])}" data-invest="{numstr(d["inv"])}" '
            f'data-power="{numstr(d["mw"])}" data-push="{d["push"]}" data-data="{d["data"]}" data-news="{d["news"]}"')
    brs = "".join(f'<div class="brow"><span>{l}</span><div class="btrack"><div class="bfill" style="width:{w}%;background:var(--{c})">{e(t)}</div></div></div>'
                  for l, (w, c, t) in zip(BAR_LABELS, d["b"]))
    return (f'<a class="card" href="{e(d["url"])}" {data}>{svg}<div class="shade"></div>'
            f'<span class="rank">{d["r"]}</span><span class="stage">{e(d["stage"])}</span>'
            f'<div class="mid"><div class="name">{e(d["n"])}</div><div class="where">{e(d["where"])}</div></div>'
            f'<div class="foot"><span>{e(d["m"])}</span><span>{e(d["p"])}</span></div>'
            f'<div class="bars">{brs}</div></a>')


def card(s, rank):
    return card_html(card_data(s, rank))


CARD_COLS = ["id", "r", "url", "name", "ss", "owner", "st", "county", "town", "cfips", "lat", "lng", "stage",
             "inv", "mw", "push", "data", "news", "op", "m", "p", "w", "c"]


def home_cards(sites, ranks):
    # Slim data for the home page cards, filters, sort and map: one row per site in data order (the map's dot order),
    # columns in CARD_COLS. home.js rebuilds card_data() from it.
    # sites.json stays as the full public data file.
    rows = []
    for s in sites:
        d = card_data(s, ranks[s["id"]])
        rows.append([s["id"], d["r"], s["url"], s["name"], 1 if s.get("_same_short") else 0, s.get("owner") or "", s["state"],
                     s.get("county") or "", s.get("town") or "", d["cfips"], d["lat"], d["lng"], s["stage"],
                     d["inv"], d["mw"], d["push"], d["data"], d["news"], openness(s), d["m"], d["p"],
                     [w for w, _, _ in d["b"]], "".join(c[0] for _, c, _ in d["b"])])
    return {"cols": CARD_COLS, "metrics": len(METRICS), "states": {c: [st["fips"], st["name"]] for c, st in REG.items()}, "rows": rows}


def openness(s):
    t = s.get("transparency") or {}
    return sum(1 if t.get(k) == "shared" else .5 if t.get(k) == "partly" else 0 for k, _ in ITEMS)


def all_asked(s):
    t = s.get("transparency") or {}
    return all(t.get(k) and t.get(k) != "not_asked" for k, _ in ITEMS)


def filled(s):
    return sum(1 for k, _ in METRICS if (s.get("metrics") or {}).get(k))


BAR_LABELS = ["Data found", "Company openness", "Local pushback", "News coverage", "Size"]


def bar_rows(s):
    # (label, width 0..1, color name, text); color names are CSS variables (--good, --ok, --bad, --muted, --info).
    op, fd = openness(s), filled(s) / len(METRICS)
    push, news, inv = len(s.get("opposition") or []), len(s.get("news") or []), num(s, "investment_usd")
    import math
    size = min(1, max(.06, (math.log10(inv) - 7) / 4)) if inv else 0

    def lvl(x, a, b):
        return "good" if x >= a else "ok" if x >= b else "bad"
    return [
        ("Data found", fd, lvl(fd, .6, .3), f"{filled(s)} of {len(METRICS)}"),
        ("Company openness", max(op / 8, .04), lvl(op / 8, .6, .3) if all_asked(s) else "muted",
         f"{op:g} of 8 so far" if op else "Not asked yet"),
        ("Local pushback", max(min(push / 5, 1), .04), "bad" if push >= 4 else "ok" if push >= 2 else "good",
         f"{push} actions" if push else "None found"),
        ("News coverage", max(min(news / 10, 1), .04), "info", f"{news} stories"),
        ("Size", max(size, .04), "info", money(inv) if inv else "Unknown"),
    ]


def bars(s):
    return "".join(f'<div class="brow"><span>{l}</span><div class="btrack"><div class="bfill" style="width:{w * 100:.0f}%;background:var(--{c})">{e(t)}</div></div></div>'
                   for l, w, c, t in bar_rows(s))


def item_list(items, text_key="what", empty="None found yet."):
    if not items:
        return f'<div class="list"><div class="item">{e(empty)}</div></div>'
    out = []
    for o in sorted(items, key=lambda x: x.get("date") or "", reverse=True):
        src = o.get("source") or o.get("url")
        out.append(f'<div class="item">{e(str(o.get(text_key) or o.get("text") or o.get("title") or ""))}<div class="d"><span>{e(str(o.get("date") or ""))}</span>{link(src, host(src)) if src else ""}</div></div>')
    return '<div class="list">' + "".join(out) + "</div>"


def tile(s, k, label):
    m = (s.get("metrics") or {}).get(k)
    if not m:
        return f'<div class="tile empty"><span class="k">{label}</span><span class="v">Not public yet</span></div>'
    isnum = isinstance(m.get("value"), (int, float))
    v = (money(m["value"]) if k == "investment_usd" else f'{m["value"]:,}') if isnum else str(m["value"])
    unit = f'<span class="u">{e(m.get("unit") or "")}</span>' if isnum and m.get("unit") else ""
    return (f'<div class="tile"><span class="k">{label}</span><span class="v{"" if isnum else " txt"}">{e(v)}</span>{unit}'
            f'<span class="src"><span class="kind {e(m.get("kind", ""))}">{e(m.get("kind", ""))}</span>{e(str(m.get("date") or ""))} {link(m.get("source"), "source")}</span></div>')


# ---------- pages ----------
def site_page(s, states, rank):
    t = s.get("transparency") or {}
    st_name = STATE_NAMES[s["state"]]
    dockets = [d for d in (states.get(s["state"]) or {}).get("dockets") or [] if s["id"] in (d.get("site_ids") or [])]
    weak = s.get("confidence") == "low"
    title = f"{short_name(s)} data center, {s['county_name']}, {st_name}: power, water, jobs, taxes"
    inv, mw = num(s, "investment_usd"), num(s, "power_mw")
    desc = (f"{short_name(s)} ({s.get('owner') or 'owner not public'}) in {s['county_name']}, {st_name}. Stage: {s['stage']}. "
            f"{'Investment ' + money(inv) + '. ' if inv else ''}{f'{mw:,.0f} MW. ' if mw else ''}"
            "Sourced numbers, news, local pushback and what the company has shared.")
    body = f"""<p class="crumb"><a href="/">Map</a> » <a href="{s['state_url']}">{st_name}</a> » <a href="{s['county_url']}">{e(s['county_name'])}</a> » {e(short_name(s))}</p>
<div class="sitehero" data-stage="{e(s['stage'])}">{bgsvg(s, 1200, 260)}<div class="in">
  <h1>{e(short_name(s))}</h1>
  <div class="sub">{e(s.get('owner') or 'Owner not public')}</div>
  <div class="meta"><span>{e(STAGE_LABEL.get(s['stage'], s['stage']))}</span><span>{e(s['county_name'])} {s['state']}</span>{f"<span>{e(s['town'].split(' (')[0])}</span>" if s.get('town') else ''}{f"<span>Announced {e(s['announced'])}</span>" if s.get('announced') else ''}<span>Confidence: {e(s.get('confidence') or '?')}</span>{'<span>Pin approximate</span>' if s.get('approx') else ''}</div>
</div></div>
{'<div class="warn">This site rests on a single source so far. Treat the details as unconfirmed until a second source or an official record backs them up.</div>' if weak else ''}
<div class="cols">
  <div>
    <section><h3>Scores</h3><div class="scores">{bars(s)}</div>
      <p class="note">Company openness only counts what the company has published so far. It isn't a final grade until we've asked for the rest.</p></section>
    <section><h3>Key numbers</h3><div class="tiles">{''.join(tile(s, k, l) for k, l in METRICS)}</div></section>
    <section><h3>What the company says</h3>{item_list(s.get('official_statements'), 'text', 'No official statement found yet.')}</section>
    {f'<section><h3>Regulator cases</h3>{item_list([{"what": (d.get("id") or "") + " · " + (d.get("regulator") or "") + ": " + (d.get("what") or ""), "url": d.get("url"), "date": d.get("date")} for d in dockets])}</section>' if dockets else ''}
  </div>
  <div>
    <section><h3>Company openness checklist</h3><div class="check">{''.join(f'<div><span>{l}</span><span class="st {e(t.get(k) or "not_asked")}">{e((t.get(k) or "not_asked").replace("_", " "))}</span></div>' for k, l in ITEMS)}</div></section>
    <section><h3>Pushback</h3>{item_list(s.get('opposition'), 'what', 'No organized pushback found yet.')}</section>
    {f'<section><h3>Other scrutiny</h3>{item_list(s.get("scrutiny"))}</section>' if s.get('scrutiny') else ''}
    <section><h3>News</h3><div class="list">{''.join(f'<div class="item"><span class="tone {e(n.get("tone") or "neutral")}"></span>{link(n.get("url"), n.get("title") or "")}<div class="d"><span>{e(n.get("outlet") or "")}</span><span>{e(str(n.get("date") or ""))}</span><span>{e(n.get("tone") or "")}</span></div></div>' for n in sorted(s.get('news') or [], key=lambda n: n.get('date') or '', reverse=True)) or '<div class="item">No news linked yet.</div>'}</div></section>
    <section><h3>Local voices</h3><div class="voices"><p class="note" style="margin:0 0 8px">Comments open soon. People who live nearby will verify with a phone number and ZIP code.</p></div></section>
    <section><h3>Where to ask for records</h3>{item_list([{"what": c.get("who"), "source": c.get("value") if str(c.get("value", "")).startswith("http") else None, "date": (c.get("how") or "") + (" · " + c["value"] if c.get("value") and not str(c.get("value")).startswith("http") else "")} for c in s.get('contacts') or []], 'what', 'No contacts found yet.')}</section>
  </div>
</div>"""
    ld = {"@context": "https://schema.org", "@type": "Place", "name": short_name(s),
          "address": {"@type": "PostalAddress", "addressRegion": s["state"], "addressLocality": (s.get("town") or "").split(" (")[0] or None},
          "url": SITE_URL + s["url"]}
    if s.get("lat") and not s.get("approx"):
        ld["geo"] = {"@type": "GeoCoordinates", "latitude": s["lat"], "longitude": s["lng"]}
    return shell(title, desc, s["url"], body, jsonld=ld)


def faq_county(county, sites, state_file):
    st_name = STATE_NAMES[sites[0]["state"]]
    names = ", ".join(short_name(s) for s in sites)
    utilities = sorted({str(s["metrics"]["utility"]["value"]) for s in sites if (s.get("metrics") or {}).get("utility")})
    ids = {s["id"] for s in sites}
    dockets = [d for d in state_file.get("dockets") or [] if ids & set(d.get("site_ids") or [])]
    breaks = [f'{short_name(s)}: {s["metrics"]["tax_break"]["value"]}' for s in sites if (s.get("metrics") or {}).get("tax_break")]
    push = sum(len(s.get("opposition") or []) for s in sites)
    qa = [
        (f"Is there a data center in {county}?",
         f"Yes. {len(sites)} on record: {names}." if len(sites) > 1 else f"Yes: {names}, currently {STAGE_LABEL[sites[0]['stage']].lower()}."),
        ("Who supplies power to it?",
         ("On record: " + "; ".join(utilities) + ".") if utilities else "Not public yet."),
        ("Will my power bill go up?",
         "Nobody can say for sure yet, and this page doesn't guess. "
         + (("Regulator cases on record for this county's sites: " + "; ".join(f'{d.get("id")} ({d.get("what", "")[:140]})' for d in dockets) + ". ") if dockets else "No regulator case is linked to these sites yet. ")
         + "Before-and-after power, rent and home value numbers for this county are being compiled."),
        ("What tax breaks did it get?", " ".join(breaks) if breaks else "Not public yet. Records requests are planned."),
        ("Is anyone opposing it?",
         f"{push} organized actions on record so far. See each site page for lawsuits, petitions, appeals and votes." if push else "No organized pushback found yet."),
    ]
    return qa


def county_page(path, county, sites, state_file, ranks):
    st = sites[0]["state"]
    st_name = STATE_NAMES[st]
    inv = sum(num(s, "investment_usd") for s in sites)
    mw = sum(num(s, "power_mw") for s in sites)
    qa = faq_county(county, sites, state_file)
    title = f"{county} data center{'s' if len(sites) > 1 else ''}: power, water, jobs, taxes ({st_name})"
    desc = f"Every data center in {county}, {st_name}: {', '.join(short_name(s) for s in sites)}. Sourced numbers on power, water, jobs and tax breaks, plus news and local pushback."
    body = f"""<p class="crumb"><a href="/">Map</a> » <a href="{sites[0]['state_url']}">{st_name}</a> » {e(county)}</p>
<div class="pagehead"><h1>Data centers in {e(county)}, {st_name}</h1>
<p>What's being built, who owns it, what it uses, what the town gets, and what the companies have shared. Every number links to its source.</p></div>
<div class="statrow"><div class="stat"><b>{len(sites)}</b><span>Sites</span></div><div class="stat"><b>{money(inv) if inv else '?'}</b><span>Announced money</span></div><div class="stat"><b>{f'{mw:,.0f}' if mw else '?'}</b><span>MW known</span></div><div class="stat"><b>{sum(len(s.get('opposition') or []) for s in sites)}</b><span>Pushback actions</span></div></div>
<div class="block"><h2>Sites</h2><div class="grid">{''.join(card(s, ranks[s['id']]) for s in sites)}</div></div>
<div class="block faq"><h2>Questions people ask</h2>{''.join(f'<details open><summary>{e(q)}</summary><p>{e(a)}</p></details>' for q, a in qa)}</div>"""
    ld = {"@context": "https://schema.org", "@type": "FAQPage",
          "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in qa]}
    return shell(title, desc, path, body, jsonld=ld)


def section_list(items, fmt):
    if not items:
        return '<div class="list"><div class="item">Not compiled yet.</div></div>'
    return '<div class="list">' + "".join(fmt(i) for i in sorted(items, key=lambda x: str(x.get("date") or ""), reverse=True)) + "</div>"


def gen_item(text, src, date, extra=""):
    return f'<div class="item">{text}<div class="d"><span>{e(str(date or ""))}</span>{extra}{link(src, host(src)) if src else ""}</div></div>'


def state_page(st, sites, sf, counties, ranks):
    name = STATE_NAMES[st]
    path = f"/{REG[st]['slug']}/"
    inv = sum(num(s, "investment_usd") for s in sites)
    title = f"{name} data centers: every site, tax breaks, power deals and local fights"
    desc = f"All {len(sites)} large data center projects in {name}, plus the state's tax breaks, utility cases, bills, local pauses and polls. Sourced and open."
    secs = [
        ("Tax breaks and incentives", "incentives", lambda i: gen_item(f"<b>{e(i.get('name') or '')}</b> {e(i.get('law') or '')}: {e(i.get('what') or '')}{(' Known value: ' + e(str(i['value_known']))) if i.get('value_known') else ''}", i.get("source"), i.get("date"))),
        ("Laws and bills", "laws_and_bills", lambda i: gen_item(f"<b>{e(i.get('name') or '')}</b> ({e(i.get('status') or '?')}): {e(i.get('what') or '')}", i.get("source"), i.get("date"))),
        ("Utility regulator cases", "dockets", lambda i: gen_item(f"<b>{e(i.get('id') or '')}</b> · {e(i.get('regulator') or '')} · {e(i.get('utility') or '')}: {e(i.get('what') or '')}", i.get("url") or i.get("source"), i.get("date"), f"<span>{e(i.get('status') or '')}</span>")),
        ("Rate cases", "rate_cases", lambda i: gen_item(f"<b>{e(i.get('utility') or '')}</b>: {e(i.get('what') or '')} {e(i.get('impact') or '')}", i.get("source"), i.get("date"))),
        ("Local pauses, zoning and ordinances", "local_rules", lambda i: gen_item(f"<b>{e(i.get('place') or '')}</b> ({e(i.get('type') or '')}, {e(i.get('status') or '')}): {e(i.get('what') or '')}", i.get("source"), i.get("date"))),
        ("Ballot measures", "ballot_measures", lambda i: gen_item(f"<b>{e(i.get('place') or '')}</b>: {e(i.get('what') or '')} {('Vote: ' + e(str(i['vote_date']))) if i.get('vote_date') else ''} {e(str(i.get('result') or ''))}", i.get("source"), i.get("date") or i.get("vote_date"))),
        ("Polls", "polls", lambda i: gen_item(f"<b>{e(i.get('who') or '')}</b>: {e(i.get('what') or '')} {e(str(i.get('result') or ''))}", i.get("source"), i.get("date"))),
        ("News", "news", lambda i: gen_item(f"<span class=\"tone {e(i.get('tone') or 'neutral')}\"></span>{link(i.get('url'), i.get('title') or '')}", None, i.get("date"), f"<span>{e(i.get('outlet') or '')}</span>")),
    ]
    utils = sf.get("utilities") or []
    body = f"""<p class="crumb"><a href="/">Map</a> » {name}</p>
<div class="pagehead"><h1>Data centers in {name}</h1>
<p>Every large data center project in {name}, at every stage, and the state rules and deals around them.</p></div>
<div class="statrow"><div class="stat"><b>{len(sites)}</b><span>Sites</span></div><div class="stat"><b>{money(inv)}</b><span>Announced money</span></div><div class="stat"><b>{len(counties)}</b><span>{county_word(st, True)}</span></div><div class="stat"><b>{sum(len(s.get('opposition') or []) for s in sites)}</b><span>Pushback actions</span></div></div>
<div class="block"><h2>By {county_word(st).lower()}</h2><div class="list">{''.join(f'<div class="item"><a href="{p}">{e(c)}</a><div class="d"><span>{len(ss)} site{"s" if len(ss) > 1 else ""}</span></div></div>' for c, (p, ss) in sorted(counties.items()))}</div></div>
<div class="block"><h2>Sites</h2><div class="grid">{''.join(card(s, ranks[s['id']]) for s in sorted(sites, key=lambda s: -num(s, 'investment_usd')))}</div></div>
{''.join(f'<div class="block"><h2>{t}</h2>{section_list(sf.get(k), f)}</div>' for t, k, f in secs)}
<div class="block"><h2>Who sells power to homes</h2>{'<div class="list">' + ''.join(f'<div class="item"><b>{e(u.get("name") or "")}</b> ({e(u.get("type") or "")}): {e(str(u.get("serves") or ""))}<div class="d">{link(u.get("url"), host(u.get("url"))) if u.get("url") else ""}</div></div>' for u in utils) + '</div>' if utils else '<div class="list"><div class="item">Not compiled yet.</div></div>'}</div>"""
    return path, shell(title, desc, path, body)


def md_to_html(md):
    """Tiny Markdown converter, enough for MISSION.md (headings, lists, tables, bold, code, paragraphs)."""
    def inline(t):
        t = e(t)
        t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
        t = re.sub(r"`(.+?)`", r"<code>\1</code>", t)
        return t
    out, lines, i = [], md.splitlines(), 0
    while i < len(lines):
        ln = lines[i]
        if ln.startswith("# "):
            out.append(f"<h1>{inline(ln[2:])}</h1>")
        elif ln.startswith("## "):
            out.append(f"<h2>{inline(ln[3:])}</h2>")
        elif ln.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                if not re.match(r"^\|[-| ]+\|$", lines[i]):
                    rows.append([c.strip() for c in lines[i].strip("|").split("|")])
                i += 1
            head, rest = rows[0], rows[1:]
            out.append('<div class="tablewrap"><table><tr>' + "".join(f"<th>{inline(c)}</th>" for c in head) + "</tr>"
                       + "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in rest) + "</table></div>")
            continue
        elif re.match(r"^(\d+\.|-) ", ln):
            tag = "ol" if ln[0].isdigit() else "ul"
            items = []
            while i < len(lines) and re.match(r"^(\d+\.|-) ", lines[i]):
                items.append(re.sub(r"^(\d+\.|-) ", "", lines[i]))
                i += 1
            out.append(f"<{tag}>" + "".join(f"<li>{inline(x)}</li>" for x in items) + f"</{tag}>")
            continue
        elif ln.strip():
            out.append(f"<p>{inline(ln)}</p>")
        i += 1
    return "\n".join(out)


def about_page():
    mission = open(os.path.join(ROOT, "MISSION.md"), encoding="utf-8").read()
    body = f"""<p class="crumb"><a href="/">Map</a> » About</p>
<div class="prose">{md_to_html(mission)}
<h2>How to help</h2>
<p>Spot a wrong number, a missing site or a dead link? {f'Open an issue or a pull request on <a href="{e(REPO_URL)}">the project repo</a>.' if REPO_URL else 'The source repo opens soon.'} Every change needs a source.</p>
<h2>Credits and licenses</h2>
<p>Data is shared under CC BY 4.0, code under the MIT license. County and state shapes come from the us-atlas project (ISC license), built from U.S. Census Bureau boundary files.</p></div>"""
    return shell("About Open Data Centers", f"Why this public record of data centers in {STATES_TEXT} exists, what it covers, and how it stays sourced and fresh.", "/about/", body)


def state_filter(sites):
    if not MANY:
        return "".join(f'  <button class="chip" data-state="{c}" aria-pressed="false">{e(st["name"])}</button>\n' for c, st in REG.items())
    n = {c: sum(1 for s in sites if s["state"] == c) for c in REG}
    opts = "".join(f'<option value="{c}">{e(REG[c]["name"])} ({n[c]})</option>' for c in sorted(REG, key=lambda c: REG[c]["name"]))
    return f'  <select id="statesel" aria-label="State"><option value="all">All states</option>{opts}</select>\n'


def states_index(sites):
    rows = []
    for c in sorted(REG, key=lambda c: (-sum(1 for s in sites if s["state"] == c), REG[c]["name"])):
        ss = [s for s in sites if s["state"] == c]
        inv = sum(num(s, "investment_usd") for s in ss)
        rows.append(f'<div class="item"><a href="/{REG[c]["slug"]}/">{e(REG[c]["name"])}</a><div class="d"><span>{len(ss)} site{"" if len(ss) == 1 else "s"}</span>'
                    f'{f"<span>{money(inv)} announced</span>" if inv else ""}</div></div>')
    body = (f'<p class="crumb"><a href="/">Map</a> » States</p><div class="pagehead"><h1>Data centers by state</h1>'
            f'<p>{len(sites)} large data center sites across {len(REG)} states and DC, most first.</p></div>'
            f'<div class="block"><div class="list">{"".join(rows)}</div></div>')
    return shell("Data centers by state · Open Data Centers", f"Every large data center in {STATES_TEXT}, by state: site counts and announced money.", "/states/", body)


HOME_CARDS = 48  # cards in the home page HTML; home.js renders the rest from /assets/cards.json


def home_page(sites, ranks):
    # Server-rendered top cards for search engines and no-JS readers; home.js takes over for filtering and "Show more".
    # Every site is still linked from its state and county pages and the sitemap.
    inv = sum(num(s, "investment_usd") for s in sites)
    tpl = open(os.path.join(HERE, "home.html"), encoding="utf-8").read()
    top = sorted(sites, key=lambda s: -num(s, "investment_usd"))[:HOME_CARDS]
    grid = "".join(card(s, ranks[s["id"]]) for s in top)
    more = "/states/" if MANY else f'/{next(iter(REG.values()))["slug"]}/'
    body = (tpl.replace("{{GRID}}", grid).replace("{{N}}", str(len(sites))).replace("{{MONEY}}", money(inv)).replace("{{STATES}}", e(STATES_TEXT))
            .replace("{{STATE_CHIPS}}", state_filter(sites)).replace("{{MORE_HREF}}", more)
            .replace("{{KICKER}}", "50 states + DC" if len(REG) >= 51 else f"{len(REG)} states" if MANY else " + ".join(REG)))
    if MANY:
        body = body.replace('<button class="chip" data-state="all" aria-pressed="true">All states</button>', "")
    desc = f"Map of all {len(sites)} large data centers in {STATES_TEXT}, about {money(inv)} in announced money. Sourced numbers on power, water, jobs, tax breaks, news and local pushback."
    return shell(f"Open Data Centers: every data center in {STATES_TEXT}", desc, "/", body,
                 scripts='<script src="/assets/home.js"></script>')


def write(path, content):
    full = os.path.join(OUT, path.strip("/"), "index.html") if path.endswith("/") else os.path.join(OUT, path.lstrip("/"))
    os.makedirs(os.path.dirname(full), exist_ok=True)
    open(full, "w", encoding="utf-8").write(content)


def build():
    r = subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "validate.py")], capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stdout[-3000:])
        sys.exit("validate.py failed; fix the data before building.")
    sites, states = load()
    if os.path.exists(OUT):
        shutil.rmtree(OUT)
    os.makedirs(os.path.join(OUT, "assets"))
    ranks = {s["id"]: i + 1 for i, s in enumerate(sorted(sites, key=lambda s: -num(s, "investment_usd")))}
    pages = ["/", "/about/"]
    write("/", home_page(sites, ranks))
    write("/about/", about_page())
    if MANY:
        write("/states/", states_index(sites))
        pages.append("/states/")
    for st in STATE_NAMES:
        ss = [s for s in sites if s["state"] == st]
        counties = {}
        for s in ss:
            counties.setdefault(s["county_name"], (s["county_url"], []))[1].append(s)
        path, htmlp = state_page(st, ss, states.get(st) or {}, counties, ranks)
        write(path, htmlp)
        pages.append(path)
        for c, (cpath, cs) in counties.items():
            write(cpath, county_page(cpath, c, cs, states.get(st) or {}, ranks))
            pages.append(cpath)
    for s in sites:
        write(s["url"], site_page(s, states, ranks[s["id"]]))
        pages.append(s["url"])
    # assets
    for f in ("style.css", "home.js", "enhance.js"):
        shutil.copy(os.path.join(HERE, "static", f), os.path.join(OUT, "assets", f))
    json.dump(registry.geo_subset(), open(os.path.join(OUT, "assets", "geo.json"), "w", encoding="utf-8"), separators=(",", ":"))
    # Small cut for the first map draw and the card outlines: states plus only the counties that hold a site.
    json.dump(registry.geo_subset({s["county_fips"] for s in sites if s.get("county_fips")}),
              open(os.path.join(OUT, "assets", "map.json"), "w", encoding="utf-8"), separators=(",", ":"))
    json.dump([{k: st[k] for k in ("code", "name", "slug", "fips", "county_word")} for st in REG.values()],
              open(os.path.join(OUT, "assets", "states.json"), "w", encoding="utf-8"))
    json.dump([{k: s.get(k) for k in ("id", "name", "owner", "state", "county", "county_name", "county_fips", "town", "lat", "lng", "approx", "stage",
                                       "announced", "confidence", "metrics", "transparency", "opposition", "news", "url")} for s in sites],
              open(os.path.join(OUT, "assets", "sites.json"), "w", encoding="utf-8"), ensure_ascii=False)
    json.dump(home_cards(sites, ranks), open(os.path.join(OUT, "assets", "cards.json"), "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    write("/404.html", shell("Page not found · Open Data Centers", "This page doesn't exist.", "/404.html",
                             '<div class="pagehead"><h1>Page not found</h1><p><a href="/">Back to the map</a>.</p></div>'))
    write("/robots.txt", f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n")
    write("/sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
          + "".join(f"  <url><loc>{e(SITE_URL + p)}</loc><lastmod>{TODAY}</lastmod></url>\n" for p in pages) + "</urlset>\n")
    n_c = len([p for p in pages if p.count("/") == 3])
    print(f"Built {len(pages)} pages (1 home, 1 about, {len(STATE_NAMES)} states, {n_c} counties, {len(sites)} sites) -> public/")
    return pages


def check(pages):
    problems, titles = [], {}
    for root, _, files in os.walk(OUT):
        for f in files:
            if not f.endswith(".html"):
                continue
            p = os.path.join(root, f)
            txt = open(p, encoding="utf-8").read()
            t = re.search(r"<title>(.*?)</title>", txt)
            if t:
                titles.setdefault(t.group(1), []).append(p)
            for href in re.findall(r'(?:href|src)="(/[^"#?]*)', txt):
                target = os.path.join(OUT, href.strip("/"))
                if not (os.path.isfile(target) or os.path.isfile(os.path.join(target, "index.html"))):
                    problems.append(f"broken link {href} in {os.path.relpath(p, OUT)}")
    for t, ps in titles.items():
        if len(ps) > 1:
            problems.append(f"duplicate title '{t}' on {len(ps)} pages")
    sm = open(os.path.join(OUT, "sitemap.xml"), encoding="utf-8").read().count("<url>")
    if sm != len(pages):
        problems.append(f"sitemap has {sm} urls, built {len(pages)} pages")
    print(f"Sitemap: {sm} urls. Broken links: {sum(1 for x in problems if x.startswith('broken'))}.")
    if problems:
        print("\n".join(sorted(set(problems))[:40]))
        sys.exit(1)


if __name__ == "__main__":
    built = build()
    if "--check" in sys.argv:
        check(built)
