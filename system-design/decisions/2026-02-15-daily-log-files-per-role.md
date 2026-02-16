---
date: 2026-02-15
type: decision
status: Accepted
author: Bruno (main), Claude
---

# Decision: One Log File Per Role Per Day

## Context

The original system created a new log file for **every single role run**:
- Filename pattern: `agent/logs/{role}/YYYY-MM-DDTHH-MM-<trigger>.md`
- Example: `agent/logs/delivery/2026-02-15T09-00-scheduled.md`

If a role ran 5 times in a day (scheduled + inbox triggers), you'd get 5 separate files.

**Problems:**
1. **Fragmentation** — To understand what a role did today, you must read multiple files
2. **Demo unfriendly** — `tail -f` on a specific file won't show new runs (new files created each time)
3. **No narrative continuity** — Each log is isolated; roles can't easily see their own earlier reasoning from the same day
4. **Cognitive overhead** — Hard to quickly scan a role's activity for the day

## Decision

Use **one log file per role per day**:
- Filename pattern: `agent/logs/{role}/YYYY-MM-DD.md`
- Example: `agent/logs/delivery/2026-02-15.md`

Each run **appends** to the daily log as a new section:

```markdown
# Delivery Manager — 2026-02-15

## Run 09:00 (scheduled)

### Inbox
- (empty)

### What Changed
- First run of the day

### Priority Action
- Review timeline against Week 2 milestones

### Not Doing
- No blockers to escalate yet

### Reflection
- Baseline established, all green

## Run 14:30 (inbox)

### Inbox
- New blocker from Risk Manager

[... next run ...]
```

## Consequences

**Easier:**
- **Demo friendly** — `tail -f agent/logs/delivery/2026-02-15.md` shows live reasoning as the role runs
- **Single source of truth** — One file = one day's activity for a role
- **Narrative continuity** — Roles can reference earlier runs in the same day ("As I noted at 09:00...")
- **Quick review** — Open one file to see everything a role did today

**Harder:**
- Slightly larger individual files (but still small — a role with 5 runs/day = ~5-10KB)
- Must use append mode instead of creating new files (trivial for agents)

**No change:**
- Daily summary compilation still works (reads all role logs from yesterday)
- Session management unchanged (same-day resumption logic is separate)

## Alternatives Considered

1. **Keep per-run files** — Rejected. The fragmentation and demo UX problems outweigh any benefits.
2. **Single log file forever** — Rejected. Would grow unbounded. Daily rotation is a natural boundary.
3. **Weekly log files** — Rejected. A week is too long; daily files match the daily summary cadence and are easier to review.

## Implementation

Updated `runner.py` `build_role_system_prompt()` to instruct roles:
- Write to `agent/logs/{role_name}/YYYY-MM-DD.md`
- Append new runs as `## Run HH:MM (trigger-type)` sections
- Use `### Subsection` headers within each run

Demo scripts updated to reference `$(date +%Y-%m-%d).md` for today's log.
