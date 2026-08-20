# Cape Traffic

Half-hourly Google Maps drive-time estimates between Brookline, MA and Chatham, MA, both directions, collected 24/7 via GitHub Actions.

## How it works

- [collect.py](collect.py) calls the Google Routes API (`computeRoutes`, `TRAFFIC_AWARE`) once per direction and appends two rows to [data/travel_times.csv](data/travel_times.csv).
- [.github/workflows/collect.yml](.github/workflows/collect.yml) runs it every half hour at :07 and :37 UTC and commits the updated CSV.
- ~2,880 API calls/month — within the Routes API free tier (10,000/month).

## Data columns

| Column | Meaning |
|---|---|
| `timestamp_utc` | Sample time, UTC |
| `timestamp_eastern` | Sample time, America/New_York |
| `date_est` | Eastern date (YYYY-MM-DD) |
| `time_est` | Eastern time, 12-hour with AM/PM |
| `day_of_week` | Day name in Eastern time |
| `direction` | `brookline_to_chatham` or `chatham_to_brookline` |
| `duration_traffic_sec` | Drive time with live traffic (seconds) |
| `duration_static_sec` | Drive time without traffic (seconds) |
| `distance_meters` | Route distance |
| `route` | Route summary (e.g. "MA-3 S and US-6 E") |

## Setup

1. Add the API key as a repo secret named `GOOGLE_MAPS_API_KEY` (Settings → Secrets and variables → Actions, or `gh secret set GOOGLE_MAPS_API_KEY`).
2. Trigger a test run: Actions tab → "Collect travel times" → Run workflow.

## Local run

```
GOOGLE_MAPS_API_KEY=your-key python3 collect.py
```
