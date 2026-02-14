# Claude TPM Agent

A Claude Code-native TPM AI Agent that uses the Agent SDK to manage technical program delivery. Roles run on schedules, communicate through a vault-based message bus, and reason through a structured THINK/ACT/REFLECT cycle.

## Architecture

```
runner.py          — Scheduler + inbox watcher. Spawns Claude Code for each role run.
config.py          — Role config parser + vault path resolver.
roles/             — Markdown configs per role (model, mission, goals, tools, schedule).
vaults/            — Project vaults with shared state (the "message bus").
```

No agent.py. No provider.py. No tools.py. Claude Code replaces all three.

## How to Run

```bash
python3 runner.py                      # Scheduler (long-running)
python3 runner.py --role delivery      # Run one role immediately
python3 runner.py --once               # Check inboxes once, exit
python3 runner.py --dry-run            # Show what would run
python3 runner.py --role comms --once  # Run comms once, then exit
```

## Roles

Each role is a `.md` file in `roles/` defining:

| Field | Purpose |
|-------|---------|
| **Model** | Which Claude model to use (haiku, sonnet, opus) |
| **Mission/Goals** | What the role does |
| **Context Files** | Which vault files to load each run |
| **Tools** | Which Claude Code tools are allowed |
| **Schedule** | When to run (cron-style or on-demand) |
| **Inbox** | Trigger directory for event-driven runs |

Current roles: **Delivery Manager**, **Risk Manager**, **Communication Manager**, **Product Manager**.

## Vault Structure

```
vaults/peaklogistics/
  CLAUDE.md                          — Project context (identity, domain, comms style)
  memory.md                          — Shared vault-wide memory
  context/                           — Live project state (blockers, updates, decisions)
  project/                           — Project artifacts (scope, timeline, team, risks)
  daily/                             — Legacy daily logs
  agent/
    inbox/
      delivery/                      — Delivery Manager inbox
        archive/                     — Processed triggers
      risk/                          — Risk Manager inbox
        archive/
      comms/                         — Communication Manager inbox
        archive/
      product/                       — Product Manager inbox
        archive/
      user/                          — User inbox (questions from roles)
        answered/                    — Answered questions (auto-routed back)
    outbox/
      {role}/drafts/                 — Draft comms for review
      {role}/approved/               — Approved comms ready to send
      {role}/sent/                   — Sent comms archive
    logs/
      {role}/                        — Per-role reasoning logs (THINK/ACT/REFLECT)
      summaries/                     — Daily compiled summaries
    memory/
      {role}.md                      — Per-role persistent memory
```

## THINK / ACT / REFLECT Cycle

Every role run follows three phases:

### Phase 1: THINK
Write structured reasoning to `agent/logs/{role}/YYYY-MM-DDTHH-MM-{trigger}.md`:
- What's in the inbox?
- What changed since last run?
- Highest-priority action and why?
- What will NOT be done and why?

### Phase 2: ACT
Execute: update context files, write triggers to other roles, draft communications, ask questions via `agent/inbox/user/`.

### Phase 3: REFLECT
Append a reflection to the reasoning log. Update `agent/memory/{role}.md` if patterns are noticed.

## Q&A Cycle

Roles can ask the User questions by writing files to `agent/inbox/user/` with YAML frontmatter (`from:`, `to:`, `date:`, `status: open`).

**How to answer questions:**

1. **Read the question:**
   ```bash
   cat agent/inbox/user/YYYY-MM-DDTHH-MM-description.md
   ```

2. **Add your answer to the file:**
   Open the file and append your answer (e.g., add an `## Answer` section at the bottom)

3. **Move to answered folder:**
   ```bash
   mv agent/inbox/user/YYYY-MM-DDTHH-MM-description.md \
      agent/inbox/user/answered/
   ```

4. **Route back to the role:**
   ```bash
   python3 runner.py --once
   ```

On each inbox check, `route_answered_questions()` automatically parses the `from:` field and moves answered files back to the originating role's inbox.

## Per-Role Memory

Each role has a persistent memory file at `agent/memory/{role}.md` with sections for **Patterns Observed** and **Feedback Received**. Roles update this during the REFLECT phase when they notice recurring patterns or receive feedback.

## Daily Compilation

Each scheduler cycle, `compile_daily_summary()` checks if yesterday's logs have been compiled. If not, it spawns a haiku agent to compile all role reasoning logs from the previous day into `agent/logs/summaries/YYYY-MM-DD.md`. The operation is idempotent.

## Adding a New Role

1. Create `roles/{name}.md` with the standard sections (Model, Mission, Goals, Context Files, Tools, Schedule, Inbox, User Preferences)
2. Create inbox directory: `vaults/peaklogistics/agent/inbox/{name}/archive/`
3. Create outbox directories: `vaults/peaklogistics/agent/outbox/{name}/{drafts,approved,sent}/`
4. Create log directory: `vaults/peaklogistics/agent/logs/{name}/`
5. Create memory file: `vaults/peaklogistics/agent/memory/{name}.md`
6. Add `.gitkeep` files to empty directories

## Testing

1. **Dry run**: `python3 runner.py --dry-run` — verifies config parsing, schedules, and inbox detection
2. **Single role**: `python3 runner.py --role delivery` — runs one role via Claude Code
3. **Inbox trigger**: Drop a `.md` file in `vaults/peaklogistics/agent/inbox/<role>/` and run `--once`
4. **Q&A routing**: Place a file with `from: delivery` frontmatter in `agent/inbox/user/answered/`, run `--once`, verify it moved to `agent/inbox/delivery/`
