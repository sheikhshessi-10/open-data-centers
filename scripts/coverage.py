"""Print what's missing or stale, as a job list for the agent routines.

Usage:
  python scripts/coverage.py            # human-readable report
  python scripts/coverage.py --json     # machine-readable job list
  python scripts/coverage.py --skill odc-news   # only jobs for one skill
Refresh windows match the coverage checklist in MISSION.md.
"""
import datetime as dt
import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import registry  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
TODAY = dt.date.today()

# section -> (skill, refresh window in days)
SITE_SECTIONS = {
    "metrics": ("odc-site-numbers", 30),
    "news": ("odc-news", 7),
    "opposition": ("odc-pushback", 7),
    "before_after": ("odc-before-after", 90),
    "contacts": ("odc-outreach", 90),
}
STATE_SECTIONS = {
    "incentives": 30, "laws_and_bills": 7, "dockets": 30, "rate_cases": 30,
    "local_rules": 7, "ballot_measures": 30, "polls": 30, "utilities": 365, "news": 7,
}
KEY_METRICS = ["investment_usd", "power_mw", "water_use", "power_source", "jobs_promised_perm", "tax_break", "local_tax_paid"]


def age(d):
    try:
        return (TODAY - dt.date.fromisoformat(str(d)[:10])).days
    except ValueError:
        return None


def jobs():
    out = []
    sites = registry.load_sites()
    codes = [st["code"] for st in registry.states()]
    # finding sites: always weekly per state
    for st in codes:
        out.append({"skill": "odc-find-sites", "target": st, "why": "weekly sweep for new sites and lead updates", "priority": 2})
    for s in sites:
        checked = s.get("checked") or {}
        for sec, (skill, window) in SITE_SECTIONS.items():
            d = checked.get(sec)
            a = age(d) if d else None
            if d is None:
                out.append({"skill": skill, "target": s["id"], "why": f"{sec} never checked", "priority": 1})
            elif a is not None and a > window:
                out.append({"skill": skill, "target": s["id"], "why": f"{sec} last checked {a} days ago (window {window})", "priority": 2})
        missing = [k for k in KEY_METRICS if not (s.get("metrics") or {}).get(k)]
        if missing and s.get("tier") != "small":
            out.append({"skill": "odc-outreach", "target": s["id"], "why": "not public yet: " + ", ".join(missing), "priority": 3})
        if s.get("confidence") == "low":
            out.append({"skill": "odc-verify", "target": s["id"], "why": "rests on one weak source", "priority": 1})
        if s.get("approx") or s.get("lat") is None:
            out.append({"skill": "odc-site-numbers", "target": s["id"], "why": "no exact map location", "priority": 3})
    leads_path = os.path.join(DATA, "leads.json")
    if os.path.exists(leads_path):
        for l in json.load(open(leads_path, encoding="utf-8")):
            if l.get("status") == "open":
                a = age(l.get("last_checked") or l.get("added") or "")
                if a is None or a > 7:
                    out.append({"skill": "odc-find-sites", "target": l.get("id"), "why": "open lead not checked in a week", "priority": 2})
    for st in codes:
        p = os.path.join(DATA, "states", f"{st}.json")
        if not os.path.exists(p):
            out.append({"skill": "odc-state-policy", "target": st, "why": "state file missing", "priority": 1})
            continue
        sf = json.load(open(p, encoding="utf-8"))
        checked = sf.get("checked")
        checked_map = checked if isinstance(checked, dict) else {}
        for sec, window in STATE_SECTIONS.items():
            d = checked_map.get(sec) or (checked if isinstance(checked, str) else None)
            a = age(d) if d else None
            if not sf.get(sec):
                out.append({"skill": "odc-state-policy", "target": f"{st}.{sec}", "why": "empty (no entries, no 'none found' note)", "priority": 1})
            elif a is None or a > window:
                out.append({"skill": "odc-state-policy", "target": f"{st}.{sec}", "why": f"stale (window {window} days)", "priority": 2})
    out.append({"skill": "odc-verify", "target": "all", "why": "monthly source and link check", "priority": 3})
    return sorted(out, key=lambda j: (j["priority"], j["skill"], str(j["target"])))


def main(args):
    js = jobs()
    if "--skill" in args:
        name = args[args.index("--skill") + 1]
        js = [j for j in js if j["skill"] == name]
    if "--json" in args:
        print(json.dumps(js, indent=2))
        return
    by = {}
    for j in js:
        by.setdefault(j["skill"], []).append(j)
    print(f"Coverage report {TODAY}: {len(js)} jobs\n")
    for skill, items in by.items():
        print(f"{skill} ({len(items)})")
        for j in items[:12]:
            print(f"  P{j['priority']} {j['target']}: {j['why']}")
        if len(items) > 12:
            print(f"  ... {len(items) - 12} more")
        print()


if __name__ == "__main__":
    main(sys.argv[1:])
