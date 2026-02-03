#!/usr/bin/env python3
import csv
import json
from collections import defaultdict

PLACES_CSV = "/Users/DMacleod/Documents/Sandbox/maine-inequality-interactive/data/maine_places_gini.csv"
STATE_CSV = "/Users/DMacleod/Documents/Sandbox/maine-inequality-interactive/data/maine_state_gini.csv"
OUT_JSON = "/Users/DMacleod/Documents/Sandbox/maine-inequality-interactive/data/maine_gini.json"

# Load place data
places = defaultdict(lambda: {"rows": []})
years_set = set()

def to_float(val):
    if val is None:
        return None
    try:
        return float(val)
    except ValueError:
        return None

with open(PLACES_CSV, newline="") as f:
    reader = csv.DictReader(f)
    for row in reader:
        year = int(row["year"])
        years_set.add(year)
        cousub = row["county_subdivision"]
        county = row["county"]
        name = row["name"]
        gini = to_float(row["gini"])
        moe = to_float(row["moe"])
        key = f"{county}-{cousub}"
        places[key]["name"] = name
        places[key]["county_subdivision"] = cousub
        places[key]["county"] = county
        places[key]["rows"].append({
            "year": year,
            "year_range": row["year_range"],
            "gini": gini,
            "moe": moe,
        })

# Load state data
state_rows = []
with open(STATE_CSV, newline="") as f:
    reader = csv.DictReader(f)
    for row in reader:
        state_rows.append({
            "year": int(row["year"]),
            "year_range": row["year_range"],
            "gini": to_float(row["gini"]),
            "moe": to_float(row["moe"]),
            "name": row["name"],
        })

# Normalize display names

def display_name(raw):
    if not raw:
        return raw
    name = raw.replace(", Maine", "")
    # Remove trailing county info
    if " County" in name:
        name = name.split(" County")[0]
    for suffix in [" city", " town", " plantation", " CDP", " village", " unorganized territory"]:
        if name.endswith(suffix):
            name = name[: -len(suffix)]
            break
    return name

# Sort years
years = sorted(years_set)
year_ranges = [f"{y-4}–{y}" for y in years]

# Build place list
place_list = []
for key, info in places.items():
    rows = sorted(info["rows"], key=lambda r: r["year"])
    series = [r["gini"] for r in rows]
    moe = [r["moe"] for r in rows]
    latest = next((v for v in reversed(series) if v is not None), None)
    earliest = next((v for v in series if v is not None), None)
    change = None
    if latest is not None and earliest is not None:
        change = round(latest - earliest, 4)
    place_list.append({
        "id": key,
        "name": info.get("name"),
        "display": display_name(info.get("name")),
        "county": info.get("county"),
        "series": series,
        "moe": moe,
        "latest": latest,
        "change": change,
    })

# Sort places by display name
place_list.sort(key=lambda p: (p["display"] or ""))

state_rows = sorted(state_rows, key=lambda r: r["year"])
state_series = [r["gini"] for r in state_rows]
state_moe = [r["moe"] for r in state_rows]

payload = {
    "years": years,
    "yearRanges": year_ranges,
    "places": place_list,
    "maine": {
        "name": state_rows[0]["name"] if state_rows else "Maine",
        "series": state_series,
        "moe": state_moe,
    },
}

with open(OUT_JSON, "w") as f:
    json.dump(payload, f)

print(f"Wrote {OUT_JSON} with {len(place_list)} places and {len(years)} years")
