"""Check every Open Data Centers data file against the rules in data/SCHEMA.md.

Usage:
  python scripts/validate.py              # check everything in data/
  python scripts/validate.py FILE ...     # check only these site files
Exit code 1 if any rule is broken. CI runs this on every pull request.
"""
import csv
import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import registry  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
ITEMS = ["power_use", "water_use", "power_source", "tax_break_size",
         "jobs_promised_vs_actual", "noise_tests", "air_permits", "community_deal"]
STATUSES = {"not_asked", "hidden", "partly", "shared"}
POINTS = {"shared": 1.0, "partly": 0.5, "hidden": 0.0}
STAGES = {"announced", "permitted", "building", "running", "paused", "blocked", "cancelled", "closed"}
TONES = {"good", "bad", "neutral"}
CODES = {st["code"] for st in registry.states()}
REGISTRY_KEYS = ["code", "name", "slug", "fips", "county_word", "file", "sources", "records_law", "local_news"]
DATE = re.compile(r"^\d{4}(-\d{2}(-\d{2})?)?$")
# Which metric backs each transparency item. Items without one need transparency_sources[item].
EVIDENCE = {"power_use": ["power_mw"], "water_use": ["water_use", "cooling_type"], "power_source": ["power_source"],
            "tax_break_size": ["tax_break"], "jobs_promised_vs_actual": ["jobs_promised_perm", "jobs_actual"],
            "community_deal": ["community_deal"], "noise_tests": [], "air_permits": []}


def check_value(where, v, errors):
    if v is None:
        return
    for key in ("value", "source", "date", "kind"):
        if v.get(key) in (None, ""):
            errors.append(f"{where}: missing {key}")
    if v.get("kind") not in ("real", "estimate"):
        errors.append(f"{where}: kind must be real or estimate")
    if v.get("date") and not DATE.match(str(v["date"])):
        errors.append(f"{where}: date {v['date']!r} is not YYYY-MM-DD")


def check_sourced_list(where, items, errors, url_key="source"):
    for n, item in enumerate(items or []):
        if not (item.get(url_key) or item.get("source") or item.get("url")):
            errors.append(f"{where}[{n}]: no source")


def logged_site_ids():
    log = os.path.join(ROOT, "outreach", "log.csv")
    if not os.path.exists(log):
        return set()
    with open(log, encoding="utf-8") as f:
        return {row["site_id"] for row in csv.DictReader(f)}


def status_label(t):
    known = [t.get(i) for i in ITEMS if t.get(i) in POINTS]
    if len(known) < len(ITEMS):
        c = {s: known.count(s) for s in ("shared", "partly", "hidden")}
        return f"{len(known)} of 8 checked: {c['shared']} shared, {c['partly']} partly, {c['hidden']} hidden"
    return f"score {sum(POINTS[s] for s in known) / len(ITEMS):.0%}"


def check_sites(path, errors, all_ids, quiet=False):
    sites = json.load(open(path, encoding="utf-8"))
    logged = logged_site_ids()
    for s in sites:
        sid = s.get("id", "?")
        if sid in all_ids:
            errors.append(f"{sid}: duplicate id")
        all_ids.add(sid)
        if s.get("stage") not in STAGES:
            errors.append(f"{sid}: bad stage {s.get('stage')!r}")
        if s.get("state") not in CODES:
            errors.append(f"{sid}: bad state {s.get('state')!r}")
        elif s.get("county") and not registry.county_fips(s["state"], s["county"]):
            errors.append(f"{sid}: county {s['county']!r} doesn't match a Census county in {s['state']} (use the Census name, e.g. 'Loudoun County', 'Richmond city')")
        metrics = s.get("metrics") or {}
        for k, v in metrics.items():
            check_value(f"{sid}.metrics.{k}", v, errors)
        for k, v in (s.get("before_after") or {}).items():
            if isinstance(v, dict) and "value" in v:
                check_value(f"{sid}.before_after.{k}", v, errors)
        for k in ("official_statements", "opposition", "scrutiny"):
            check_sourced_list(f"{sid}.{k}", s.get(k), errors)
        for n, item in enumerate(s.get("news") or []):
            if not safe(item.get("url")):
                errors.append(f"{sid}.news[{n}]: no url")
            if item.get("tone") not in TONES:
                errors.append(f"{sid}.news[{n}]: tone must be good, bad or neutral")
        for k, d in (s.get("checked") or {}).items():
            if not DATE.match(str(d)):
                errors.append(f"{sid}.checked.{k}: bad date {d!r}")
        t = s.get("transparency") or {}
        extra = s.get("transparency_sources") or {}
        for item in ITEMS:
            st = t.get(item)
            if st not in STATUSES:
                errors.append(f"{sid}.transparency.{item}: bad status {st!r}")
            if st == "hidden" and sid not in logged:
                errors.append(f"{sid}.transparency.{item}: hidden but no request in outreach/log.csv")
            if st in ("shared", "partly"):
                backed = extra.get(item) or any((metrics.get(m) or {}).get("source") for m in EVIDENCE[item])
                if not backed:
                    errors.append(f"{sid}.transparency.{item}: {st} but no evidence (fill {EVIDENCE[item] or 'transparency_sources'})")
        if not quiet:
            filled = sum(1 for v in metrics.values() if v)
            print(f"{os.path.basename(path):18} {sid:52} {s.get('stage',''):10} metrics {filled:2}  {status_label(t)}")


def safe(u):
    return isinstance(u, str) and u.startswith(("http://", "https://"))


def check_leads(path, errors, site_ids):
    leads = json.load(open(path, encoding="utf-8"))
    seen = set()
    for n, l in enumerate(leads):
        lid = l.get("id") or f"lead[{n}]"
        if lid in seen:
            errors.append(f"leads {lid}: duplicate id")
        seen.add(lid)
        if l.get("state") not in CODES:
            errors.append(f"leads {lid}: bad state")
        if l.get("status") not in ("open", "promoted", "dropped"):
            errors.append(f"leads {lid}: status must be open, promoted or dropped")
        if not any(safe(u) for u in l.get("sources") or []):
            errors.append(f"leads {lid}: needs at least one source url")
    print(f"leads.json         {len(leads)} leads ({sum(1 for l in leads if l.get('status') == 'open')} open)")


STATE_LISTS = ["incentives", "laws_and_bills", "dockets", "rate_cases", "local_rules", "ballot_measures", "polls", "news"]


def check_state(path, errors):
    st = json.load(open(path, encoding="utf-8"))
    name = os.path.basename(path)
    for k in STATE_LISTS:
        for n, item in enumerate(st.get(k) or []):
            if not (safe(item.get("source")) or safe(item.get("url"))):
                errors.append(f"{name}.{k}[{n}]: no source url")
    counts = ", ".join(f"{k} {len(st.get(k) or [])}" for k in STATE_LISTS + ["utilities"])
    print(f"{name:18} {counts}")


def check_registry(errors):
    seen = set()
    for st in registry.states():
        for k in REGISTRY_KEYS:
            if not st.get(k):
                errors.append(f"registry {st.get('code', '?')}: missing {k}")
        for k in ("economic_development", "utility_regulator", "environment_agency", "legislature"):
            if not (st.get("sources") or {}).get(k):
                errors.append(f"registry {st.get('code')}: sources.{k} missing")
        if st.get("code") in seen:
            errors.append(f"registry {st.get('code')}: duplicate")
        seen.add(st.get("code"))
        if not os.path.exists(os.path.join(DATA, st.get("file", ""))):
            errors.append(f"registry {st.get('code')}: data/{st.get('file')} does not exist")
        if not os.path.exists(os.path.join(DATA, "states", f"{st.get('code')}.json")):
            errors.append(f"registry {st.get('code')}: data/states/{st.get('code')}.json does not exist")
    print(f"registry.json      {len(seen)} states: {', '.join(sorted(seen))}")


def main(paths):
    errors, ids = [], set()
    if paths:
        for p in paths:
            check_sites(p, errors, ids)
    else:
        check_registry(errors)
        for _, p in registry.site_files():
            if os.path.exists(p):
                check_sites(p, errors, ids)
        if os.path.exists(os.path.join(DATA, "leads.json")):
            check_leads(os.path.join(DATA, "leads.json"), errors, ids)
        for st in registry.states():
            p = os.path.join(DATA, "states", f"{st['code']}.json")
            if os.path.exists(p):
                check_state(p, errors)
    if errors:
        print(f"\n{len(errors)} problems:")
        print("\n".join("  " + e for e in errors))
        sys.exit(1)
    print("\nAll rules pass.")


if __name__ == "__main__":
    main(sys.argv[1:])
