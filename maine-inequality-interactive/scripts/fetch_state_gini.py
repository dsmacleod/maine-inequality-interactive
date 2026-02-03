#!/usr/bin/env python3
import csv
import os
import sys
import time
from urllib.parse import urlencode
import json
import urllib.request

API_KEY = os.environ.get("CENSUS_API_KEY")
if not API_KEY:
    print("Missing CENSUS_API_KEY env var", file=sys.stderr)
    sys.exit(1)

START_YEAR = 2014
END_YEAR = 2024
STATE_FIPS = "23"

BASE = "https://api.census.gov/data/{year}/acs/acs5"

rows = []
for year in range(START_YEAR, END_YEAR + 1):
    params = {
        "get": "NAME,B19083_001E,B19083_001M",
        "for": f"state:{STATE_FIPS}",
        "key": API_KEY,
    }
    url = BASE.format(year=year) + "?" + urlencode(params)
    with urllib.request.urlopen(url) as resp:
        data = json.load(resp)
    header = data[0]
    idx_name = header.index("NAME")
    idx_est = header.index("B19083_001E")
    idx_moe = header.index("B19083_001M")
    for row in data[1:]:
        rows.append({
            "year": year,
            "year_range": f"{year-4}–{year}",
            "name": row[idx_name],
            "state": STATE_FIPS,
            "gini": row[idx_est],
            "moe": row[idx_moe],
            "source": f"ACS 5-year {year} (B19083)",
        })
    time.sleep(0.1)

out_path = "/Users/DMacleod/Documents/Sandbox/maine-inequality-interactive/data/maine_state_gini.csv"
with open(out_path, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["year", "year_range", "name", "state", "gini", "moe", "source"])
    writer.writeheader()
    writer.writerows(rows)

print(f"Wrote {len(rows)} rows to {out_path}")
