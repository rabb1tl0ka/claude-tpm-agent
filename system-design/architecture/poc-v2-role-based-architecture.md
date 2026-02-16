---
date: 2026-02-14
type: architecture
status: Accepted
author: Claude (with Bruno)
---

# POC v2: Role-Based Architecture

## Context

POC v1 proved the basic concept: an AI agent that reads vault context, interacts with Slack, and drafts communications. However, the first real test exposed critical problems:

1. **No reasoning step** — the agent follows a scripted SEND → READ → PROCESS → DRAFT → LOG pipeline without thinking about what actually needs attention
2. **Monolithic runs** — every cycle runs everything (read Slack, process, draft, send) regardless of whether anything changed
3. **Context bloat** — all project context is loaded every run, growing cost as features are added
4. **Runaway loops** — 21 cycles in quick succession exhausted the API budget with no throttling or scheduling

These aren't bugs in the implementation — they're limitations of a single-loop, do-everything architecture. Fixing them requires a structural change.

## Key Insight

A TPM doesn't follow a single script. A TPM plays different **roles** that require different thinking modes, different inputs, and run at different frequencies:

| Role | What it does | Thinks about | Frequency |
|------|-------------|--------------|-----------|
| **Delivery Manager** | Keeps delivery on-time and aligned with client priorities | Timeline, tasks, blockers, team velocity | 2x/day |
| **Risk Manager** | Identifies and mitigates project risks | Blockers, delays, dependencies, external factors | 1x/day |
| **Communication Manager** | Handles status updates, Slack, client reports | Messages, updates, drafts, approvals | Every 30 min |
| **Product Manager** | Manages scope, roadmap, feature prioritization | Requirements, priorities, client alignment | On-demand / weekly |

The frequencies above are starting points. They will be tuned based on real usage.

## Architecture Decision: Single Agent, Role-Based Runs

### What we decided

One agent, multiple **role configurations**. Each run activates one role. The role determines:
- What context files to load (small, focused)
- What system prompt and mission to use
- What tools are available
- What vault directories to read/write

### Why not multi-agent (separate agent per role + orchestrator)?

We considered and rejected this. The reasoning:

- **Inter-agent communication is a hard problem.** Shared state, message passing, conflict resolution — this is infrastructure work, not TPM work
- **The orchestrator becomes the hardest piece** — a meta-agent managing agents is a framework, not a product
- **Debugging is painful** — "which agent wrote this file and why?" across N agents and an orchestrator
- **The vault already solves shared state** — roles read and write to the same vault, no coordination protocol needed
- **More total API calls** — orchestrator reasoning on top of N agent runs

The single-agent approach captures ~80% of the multi-agent benefit at ~20% of the complexity.

## System Design

### Components

```
┌─────────────────────────────────────────────────┐
│                    Runner                        │
│  (decides WHEN to run WHICH role)                │
│                                                  │
│  Inputs:                                         │
│    - Schedule (cron-like per role)                │
│    - Inbox triggers (event-driven)               │
│    - Previous run output (chained triggers)       │
│                                                  │
│  Output:                                         │
│    python agent.py --role <role_name>             │
└──────────────────────┬──────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────┐
│                  Agent (agent.py)                 │
│                                                  │
│  1. Load role config (mission, goals, context)   │
│  2. Load role-specific vault context             │
│  3. THINK: What needs attention? What changed?   │
│  4. ACT: Execute tool calls to achieve goals     │
│  5. TRIGGER: Signal if other roles should run    │
│  6. LOG: Write structured run log                │
│                                                  │
│  Same agent.py, provider.py, tools.py            │
└──────────────────────┬──────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────┐
│                    Vault                          │
│  (shared state — the "message bus")              │
│                                                  │
│  project/    — scope, timeline, team, risks,      │
│               blockers, decisions, goals,         │
│               challenges, traffic-lights          │
│  agent/      — TPM AI Agent's workspace          │
│    inbox/    — trigger files per role            │
│  daily/      — run logs                          │
│  memory.md   — persistent agent memory           │
└─────────────────────────────────────────────────┘
```

### Role Configs

Each role is a Markdown file under `roles/` — consistent with the vault-first philosophy where everything is `.md`. The agent reads these the same way it reads any vault file. The human (User) edits them naturally.

```markdown
# roles/delivery.md

# Delivery Manager

## Mission
Keep the project delivery on-time and aligned with client priorities.
Enable the team to deliver by the planned finish date or earlier.

## Goals
- Track progress against timeline and milestones
- Identify blockers that threaten delivery dates
- Recommend adjustments when delivery is at risk

## Context Files
- project/scope.md
- project/timeline.md
- project/team.md
- project/blockers/
- project/traffic-lights/
- memory.md

## Tools
- read_file
- write_file
- append_file
- list_files
- move_file

## Schedule
9am and 5pm, weekdays

## Inbox
agent/inbox/delivery/

## User Preferences
(Configured by the User — how this role should behave)
```

The agent parses the Markdown sections to extract mission, goals, context files, tools, etc. No YAML, no extra parsing libraries — just Markdown, the same format used everywhere in the vault.

### The Thinking Step

The biggest change from v1. The system prompt for every role now starts with:

> You are the {role display_name} for this project.
> Your mission: {mission}
> Your goals: {goals}
>
> Before taking any action, THINK:
> 1. What has changed since the last run? (check inbox, compare context)
> 2. What needs attention right now?
> 3. What is the most valuable action you can take this run?
>
> Then act on your reasoning. Be efficient — do only what matters, then stop.

This replaces the scripted "do steps 1-5" prompt from v1. The agent reasons about what to do instead of blindly following a checklist.

### Trigger Mechanism: Inbox Pattern

When one role discovers something relevant to another role, it writes a trigger file to that role's inbox:

```
agent/inbox/risk/2026-02-14T17-30-delay-in-auth-module.md
```

Contents:
```markdown
---
from: delivery
date: 2026-02-14T17:30:00Z
priority: high
---

Authentication module delivery is now 3 days behind schedule.
This may delay the overall project timeline by 1 week.
The Delivery Manager has logged the blocker in project/blockers/ with details.
```

**Three trigger sources, one mechanism:**

| Source | How it works |
|--------|-------------|
| **Schedule** | Cron fires at configured time → role runs |
| **Inter-role** | Role writes to `agent/inbox/<other_role>/` → runner detects file → other role runs |
| **Human (User)** | Bruno drops a note in `agent/inbox/<role>/` → runner detects file → role runs |

The runner logic is the same in all cases:
```
for each role:
    if agent/inbox/ has unprocessed files OR schedule says it's time:
        run the role
```

After a role processes its inbox files, it archives or deletes them.

### What Changes from v1

| Component | v1 | v2 (implemented) |
|-----------|-------------|---------------|
| `agent.py` | Hardcoded SEND→READ→PROCESS→DRAFT→LOG | Loads role config, builds role-specific prompt with thinking step |
| `config.py` | Flat env vars | Adds role config loading |
| `tools.py` | No change | No change (roles select from existing tools) |
| `provider.py` | No change | No change |
| **New: `roles/`** | — | Markdown configs per role (`.md`) |
| **New: `runner.py`** | — | Scheduler + inbox watcher, invokes agent.py with --role |
| **New: `agent/inbox/`** | — | Vault directory for trigger files per role |
| Prompt | Scripted steps | Mission + goals + think-first |
| Scheduling | `while True` loop | Cron-like per role + event triggers |
| Context per run | Everything | Only what the role needs |

### What Stays the Same

- **provider.py** — Multi-provider abstraction works as-is
- **tools.py** — All vault and Slack tools work as-is
- **Vault structure** — project/, agent/, daily/ unchanged
- **--vault-only flag** — Still useful for testing without Slack
- **Logging** — Same approach, now per-role per-run

## Migration Path

Incremental steps, each one testable:

1. **Add role configs** — Create `roles/` directory with Markdown files for each role
2. **Add `--role` flag to agent.py** — Load role config, build role-specific prompt with thinking step. Existing behavior (no --role flag) still works as before
3. **Narrow context loading** — Each role loads only its configured context files
4. **Add agent/inbox/ to vault** — Create inbox directories per role
5. **Build runner.py** — Schedule-based + inbox-watching runner that invokes agent.py per role
6. **Add trigger output** — Roles can write to other roles' inboxes after their run
7. **Tune and iterate** — Adjust schedules, role definitions, and prompts based on real runs

Each step can be tested independently. Step 2 alone already solves the "no reasoning" and "monolithic context" problems.

## Resolved Decisions

1. **Runner implementation** — Python script with `schedule` library. Handles both cron-like scheduling and inbox polling in one process.
2. **Inbox file lifecycle** — Agent moves processed files to `agent/inbox/<role>/processed/`. User moves reviewed files to `agent/inbox/<role>/archive/` to keep `processed/` clean.
3. **Memory** — Global `memory.md` at vault root for cross-role learnings and User preferences. Per-role `memory.md` for role-specific learnings. All roles load global `memory.md` in their context files.
4. **User preferences** — Global preferences live in `memory.md` (no separate preferences file). Role-specific preferences live in each role's `.md` under "User Preferences".

## Open

- [ ] TODO: think of how will we demo this.
