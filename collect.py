#!/usr/bin/env python3
"""Collect Google Maps drive-time estimates between Brookline, MA and Chatham, MA.

Calls the Google Routes API (computeRoutes) once per direction with live
traffic and appends one CSV row per direction to data/travel_times.csv.

Requires env var GOOGLE_MAPS_API_KEY. Uses only the Python standard library.
"""

import csv
import json
import os
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

API_URL = "https://routes.googleapis.com/directions/v2:computeRoutes"
FIELD_MASK = "routes.duration,routes.staticDuration,routes.distanceMeters,routes.description"

BROOKLINE = "Brookline, MA"
CHATHAM = "Chatham, MA"

CSV_PATH = Path(__file__).parent / "data" / "travel_times.csv"
CSV_COLUMNS = [
    "timestamp_utc",
    "timestamp_eastern",
    "day_of_week",
    "direction",
    "duration_traffic_sec",
    "duration_static_sec",
    "distance_meters",
    "route",
]


def parse_duration(value):
    # Routes API durations look like "5432s"
    return int(round(float(value.rstrip("s"))))


def get_route(api_key, origin, destination):
    body = {
        "origin": {"address": origin},
        "destination": {"address": destination},
        "travelMode": "DRIVE",
        "routingPreference": "TRAFFIC_AWARE",
    }
    req = urllib.request.Request(
        API_URL,
        data=json.dumps(body).encode(),
        headers={
            "Content-Type": "application/json",
            "X-Goog-Api-Key": api_key,
            "X-Goog-FieldMask": FIELD_MASK,
        },
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read())
    route = data["routes"][0]
    return {
        "duration_traffic_sec": parse_duration(route["duration"]),
        "duration_static_sec": parse_duration(route["staticDuration"]),
        "distance_meters": route["distanceMeters"],
        "route": route.get("description", ""),
    }


def main():
    api_key = os.environ.get("GOOGLE_MAPS_API_KEY")
    if not api_key:
        sys.exit("GOOGLE_MAPS_API_KEY is not set")

    now_utc = datetime.now(timezone.utc)
    now_east = now_utc.astimezone(ZoneInfo("America/New_York"))

    rows = []
    for direction, origin, dest in [
        ("brookline_to_chatham", BROOKLINE, CHATHAM),
        ("chatham_to_brookline", CHATHAM, BROOKLINE),
    ]:
        result = get_route(api_key, origin, dest)
        rows.append({
            "timestamp_utc": now_utc.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "timestamp_eastern": now_east.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "day_of_week": now_east.strftime("%A"),
            "direction": direction,
            **result,
        })
        mins = result["duration_traffic_sec"] / 60
        print(f"{direction}: {mins:.1f} min ({result['route']})")

    CSV_PATH.parent.mkdir(exist_ok=True)
    is_new = not CSV_PATH.exists()
    with open(CSV_PATH, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        if is_new:
            writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
