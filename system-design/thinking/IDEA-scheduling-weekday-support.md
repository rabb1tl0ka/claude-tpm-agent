---
date: 2026-02-14
type: improvement
status: TODO
author: Claude
---

# Improvement: Add Weekday/Weekend Support to Schedule Parser

## Problem

The `parse_schedule()` function in `runner.py` (lines 316-346) only parses:
- `"on-demand"` — inbox-triggered only
- `"every N minutes"` — interval-based
- Time patterns like `"9am"`, `"5pm"` — daily at fixed times

The word **"weekdays"** in schedule strings (e.g., `"9am and 5pm, weekdays"`) is **ignored**. All time-based schedules currently run every day, including weekends.

## Affected Roles

- **Delivery Manager** — `"9am and 5pm, weekdays"` (runs 7 days/week instead of 5)
- **Risk Manager** — `"10am, weekdays"` (runs 7 days/week instead of 5)

## Proposed Fix

Use the `schedule` library's built-in day filtering:

```python
# Current (runs every day):
schedule.every().day.at("09:00").do(run_role, ...)

# Fixed (weekdays only):
for day in [schedule.every().monday, schedule.every().tuesday,
            schedule.every().wednesday, schedule.every().thursday,
            schedule.every().friday]:
    day.at("09:00").do(run_role, ...)
```

Also consider supporting:
- `"weekdays"` — Mon-Fri
- `"weekends"` — Sat-Sun
- `"daily"` — every day (default, current behavior)
- Specific days: `"monday and thursday"`

## Impact

Low risk. Only changes scheduling frequency, not role behavior. Easy to test with `--dry-run`.
