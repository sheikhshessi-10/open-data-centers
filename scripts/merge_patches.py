"""Merge agent patch files from data/_incoming/ into the data files.

Agents running in parallel never edit data/{state}.json directly (two writers lose each other's changes).
Each writes one patch file, data/_incoming/<skill>-<target>.json:

{
  "skill": "odc-site-numbers",
  "sites": {
    "<site id>": {
      "metrics": {"power_mw": {...}},          # merged key by key
      "checked": {"metrics": "YYYY-MM-DD"},    # merged key by key
      "transparency_sources": {...},           # merged key by key
      "lat": 32.1, "lng": -90.2,               # any other field: replaced whole
      "news": [...], "before_after": {...}
    }
  },
  "new_sites": [ {full site record}, ... ],
  "leads": [ {full lead record}, ... ],         # replaces the lead with the same id, or adds it
  "state_file": {"state": "MS", "sections": {"dockets": [...]}, "checked": {...}},
  "registry_entries": [ {full registry entry}, ... ],  # odc-add-state: adds or replaces by code, creates the empty data files
  "delete_sites": ["<id>", ...], "delete_reasons": {"<id>": "duplicate of <id>: ..."}  # duplicates only; each needs a reason
}

Usage: python scripts/merge_patches.py [--dry-run] [--upsert] [--only=PREFIX]
  --only=PREFIX  merge only patch files whose name starts with PREFIX (e.g. --only=pins-), leaving others waiting
  --upsert  a new_sites record whose id already exists replaces the old record (use when an agent re-sends
            a finished version of sites an earlier merge already took in). Without it, those are skipped.
Any other argument (including --help) prints this text and merges nothing.
Merged patches move to data/_incoming/merged/. Run validate.py afterwards.
"""
import glob
import json
import os
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
INBOX = os.path.join(DATA, "_incoming")
MERGE_KEYS = {"metrics", "checked", "transparency_sources", "transparency"}


def state_files():
    reg = json.load(open(os.path.join(DATA, "states", "registry.json"), encoding="utf-8"))
    return {s["code"]: os.path.join(DATA, s["file"]) for s in reg["states"]}


def add_registry_entries(patches, dry):
    """Registry entries go in first, so the same run can merge sites for a brand new state."""
    path = os.path.join(DATA, "states", "registry.json")
    reg = json.load(open(path, encoding="utf-8"))
    added = []
    for p in patches:
        for entry in json.load(open(p, encoding="utf-8")).get("registry_entries") or []:
            reg["states"] = [s for s in reg["states"] if s["code"] != entry["code"]] + [entry]
            added.append(entry["code"])
    if not added or dry:
        return added
    json.dump(reg, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    for entry in reg["states"]:
        site_path = os.path.join(DATA, entry["file"])
        if not os.path.exists(site_path):
            json.dump([], open(site_path, "w", encoding="utf-8"))
        st_path = os.path.join(DATA, "states", f"{entry['code']}.json")
        if not os.path.exists(st_path):
            json.dump({"state": entry["code"], "checked": {}}, open(st_path, "w", encoding="utf-8"), indent=2)
    return added


def main(dry, upsert=False, only=""):
    patches = sorted(glob.glob(os.path.join(INBOX, f"{only}*.json")))
    added = add_registry_entries(patches, dry)
    if added:
        print(f"Registry: {len(added)} states added or replaced ({', '.join(added)})")
    files = state_files()
    sites_by_file = {f: json.load(open(f, encoding="utf-8")) for f in files.values() if os.path.exists(f)}
    index = {s["id"]: (f, s) for f, ss in sites_by_file.items() for s in ss}
    leads_path = os.path.join(DATA, "leads.json")
    leads = json.load(open(leads_path, encoding="utf-8")) if os.path.exists(leads_path) else []
    state_docs = {}
    if not patches:
        print("No patches in data/_incoming/.")
        return
    report = []
    for p in patches:
        patch = json.load(open(p, encoding="utf-8"))
        name = os.path.basename(p)
        n_upd = 0
        for sid, fields in (patch.get("sites") or {}).items():
            if sid not in index:
                report.append(f"{name}: unknown site id {sid} (skipped)")
                continue
            rec = index[sid][1]
            for k, v in fields.items():
                if k in MERGE_KEYS and isinstance(v, dict):
                    rec.setdefault(k, {})
                    rec[k].update(v)
                else:
                    rec[k] = v
            n_upd += 1
        n_new = 0
        for s in patch.get("new_sites") or []:
            if s["id"] in index:
                if upsert:
                    f, old = index[s["id"]]
                    sites_by_file[f][sites_by_file[f].index(old)] = s
                    index[s["id"]] = (f, s)
                    report.append(f"{name}: new site {s['id']} replaced the existing record (--upsert)")
                else:
                    report.append(f"{name}: new site {s['id']} already exists (skipped)")
                continue
            f = files.get(s.get("state"))
            if not f:
                report.append(f"{name}: new site {s['id']} has unregistered state {s.get('state')} (skipped)")
                continue
            sites_by_file.setdefault(f, []).append(s)
            index[s["id"]] = (f, s)
            n_new += 1
        for sid in patch.get("delete_sites") or []:
            why = (patch.get("delete_reasons") or {}).get(sid)
            if sid not in index or not why:
                report.append(f"{name}: delete {sid} skipped ({'unknown id' if sid not in index else 'no reason given'})")
                continue
            f, rec = index.pop(sid)
            sites_by_file[f].remove(rec)
            report.append(f"{name}: deleted {sid} ({why})")
        for l in patch.get("leads") or []:
            leads = [x for x in leads if x.get("id") != l.get("id")] + [l]
        sf = patch.get("state_file")
        if sf:
            path = os.path.join(DATA, "states", f"{sf['state']}.json")
            doc = state_docs.get(path) or (json.load(open(path, encoding="utf-8")) if os.path.exists(path) else {"state": sf["state"]})
            doc.update(sf.get("sections") or {})
            doc.setdefault("checked", {}) if isinstance(doc.get("checked"), dict) else doc.__setitem__("checked", {})
            doc["checked"].update(sf.get("checked") or {})
            state_docs[path] = doc
        report.append(f"{name}: {n_upd} sites updated, {n_new} new, {len(patch.get('leads') or [])} leads{', state file' if sf else ''}")
    print("\n".join(report))
    if dry:
        print("(dry run, nothing written)")
        return
    for f, ss in sites_by_file.items():
        json.dump(ss, open(f, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump(leads, open(leads_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    for path, doc in state_docs.items():
        json.dump(doc, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    done = os.path.join(INBOX, "merged")
    os.makedirs(done, exist_ok=True)
    for p in patches:
        shutil.move(p, os.path.join(done, os.path.basename(p)))
    print(f"Merged {len(patches)} patches. Now run: python scripts/validate.py")


if __name__ == "__main__":
    args = set(sys.argv[1:])
    only = next((a.split("=", 1)[1] for a in args if a.startswith("--only=")), "")
    if args - {"--dry-run", "--upsert"} - {a for a in args if a.startswith("--only=") and only}:
        sys.exit(__doc__)
    main("--dry-run" in args, "--upsert" in args, only)
