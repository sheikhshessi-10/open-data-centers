"""Shared helpers: the list of covered states, and the map cut for them.

Every script reads the covered states from data/states/registry.json, so adding a state never means editing code.
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
GEO_SRC = os.path.join(ROOT, "site", "geo", "us-counties-10m.json")


def states():
    """Covered states, in registry order."""
    return json.load(open(os.path.join(DATA, "states", "registry.json"), encoding="utf-8"))["states"]


def by_code():
    return {s["code"]: s for s in states()}


def site_files():
    return [(s["code"], os.path.join(DATA, s["file"])) for s in states()]


def load_sites():
    out = []
    for _, path in site_files():
        if os.path.exists(path):
            out += json.load(open(path, encoding="utf-8"))
    return out


_COUNTIES = None
_SUFFIXES = (" city and borough", " census area", " municipality", " borough", " parish", " county")


def county_fips(state_code, county):
    """5-digit Census code for a site's county, matched against the map file. None if it can't be matched.

    Independent cities share names with counties (Richmond city vs Richmond County, Virginia), so a name ending
    in " city" matches the independent city (codes 500+) and any other name matches the county (codes below 500).
    """
    global _COUNTIES
    st = by_code().get(state_code)
    if not st or not county:
        return None
    if _COUNTIES is None:
        topo = json.load(open(GEO_SRC, encoding="utf-8"))
        _COUNTIES = [(g["id"], g["properties"]["name"].lower()) for g in topo["objects"]["counties"]["geometries"]]
    name = county.strip().lower()
    mine = [(i, n) for i, n in _COUNTIES if i[:2] == st["fips"]]
    exact = [i for i, n in mine if n == name]
    if len(exact) == 1:
        return exact[0]
    if name.endswith(" city"):
        base = name[:-5]
        hits = [i for i, n in mine if n == base and int(i[2:]) >= 500]
    else:
        base = next((name[:-len(x)] for x in _SUFFIXES if name.endswith(x)), name)
        hits = [i for i, n in mine if n == base and int(i[2:]) < 500] or [i for i, n in mine if n == base]
    return hits[0] if len(hits) == 1 else None


def _arcs_of(geom):
    """Every arc index a topojson geometry uses (negative indices are reversed arcs)."""
    def walk(a):
        if isinstance(a, int):
            yield a if a >= 0 else ~a
        else:
            for x in a:
                yield from walk(x)
    return set(walk(geom.get("arcs", [])))


def _remap(a, table):
    if isinstance(a, int):
        return table[a] if a >= 0 else ~table[~a]
    return [_remap(x, table) for x in a]


def geo_subset(host_fips=None):
    """Topojson with the covered states' counties, the covered states, and every state that borders them.

    Neighbors are found by shared borders (shared arcs), so a new state brings its own neighbors automatically.
    Unused arcs are dropped to keep the file small.
    With host_fips, the counties object holds only those counties (the small file the home map draws first).
    """
    topo = json.load(open(GEO_SRC, encoding="utf-8"))
    fips = {s["fips"] for s in states()}
    st_geoms = topo["objects"]["states"]["geometries"]
    covered = [g for g in st_geoms if g.get("id") in fips]
    covered_arcs = set().union(*(_arcs_of(g) for g in covered)) if covered else set()
    neighbors = [g for g in st_geoms if g.get("id") not in fips and _arcs_of(g) & covered_arcs]
    counties = [g for g in topo["objects"]["counties"]["geometries"] if str(g.get("id", ""))[:2] in fips
                and (host_fips is None or g.get("id") in host_fips)]
    keep = covered + neighbors
    used = sorted(set().union(*(_arcs_of(g) for g in keep + counties)))
    table = {old: new for new, old in enumerate(used)}
    out = {"type": "Topology", "transform": topo.get("transform"), "arcs": [topo["arcs"][i] for i in used], "objects": {
        "counties": {"type": "GeometryCollection", "geometries": [dict(g, arcs=_remap(g["arcs"], table)) for g in counties]},
        "states": {"type": "GeometryCollection", "geometries": [dict(g, arcs=_remap(g["arcs"], table)) for g in keep]},
    }}
    if out["transform"] is None:
        del out["transform"]
    return out
