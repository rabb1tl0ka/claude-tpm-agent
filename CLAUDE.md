# Claude Code Instructions — Claude TPM Agent

This is the Claude Code-native implementation of the TPM AI Agent.
Unlike the API-based version (tpm-ai-agent), this repo uses Claude Code itself as the execution engine via the Agent SDK.

## Architecture

- **runner.py** — Scheduler + inbox watcher + Q&A router + daily compiler. Spawns Claude Code for each role run.
- **config.py** — Role config parser + vault path resolver.
- **roles/** — Markdown configs per role (mission, goals, model, tools, schedule).
- **vaults/** — Project vaults with shared state (the "message bus").

No agent.py. No provider.py. No tools.py. Claude Code replaces all three.

### Vault Agent Structure

```
agent/
  inbox/{role}/           — Trigger files for event-driven runs
  inbox/{role}/archive/   — Processed triggers
  inbox/user/           — Questions from roles to the User
  inbox/user/answered/  — Answered questions (auto-routed back to roles)
  outbox/{role}/          — drafts/ → approved/ → sent/ communication pipeline
  logs/{role}/            — Per-role reasoning logs (THINK/ACT/REFLECT)
  logs/summaries/         — Daily compiled summaries
  memory/{role}.md        — Per-role persistent memory
```

## How Roles Work

Each role is a `.md` file in `roles/` defining Model, Mission, Goals, Context Files, Tools, Schedule, Inbox, and User Preferences.

Roles follow a **THINK/ACT/REFLECT** cycle each run:
1. **THINK** — Write structured reasoning to `agent/logs/{role}/`
2. **ACT** — Update context, write triggers, draft comms, ask questions
3. **REFLECT** — Append reflection, update `agent/memory/{role}.md`

### Q&A Cycle

Roles ask the User questions via `agent/inbox/user/`. Answered questions in `agent/inbox/user/answered/` are auto-routed back to the originating role's inbox by `route_answered_questions()`.

### Daily Compilation

`compile_daily_summary()` runs each scheduler cycle, compiling yesterday's role logs into `agent/logs/summaries/YYYY-MM-DD.md` (idempotent).

## Running

```bash
python3 runner.py                      # Scheduler (long-running)
python3 runner.py --role delivery      # Run one role immediately
python3 runner.py --once               # Check inboxes once, exit
python3 runner.py --dry-run            # Show what would run
```

## Testing

1. **Dry run**: `python3 runner.py --dry-run` — verifies config parsing + inbox detection
2. **Single role**: `python3 runner.py --role delivery` — runs one role via Claude Code
3. **Inbox trigger**: Drop a `.md` file in `vaults/peaklogistics/agent/inbox/<role>/` and run `--once`
4. **Q&A routing**: Place answered file in `agent/inbox/user/answered/` with `from: delivery` frontmatter, run `--once`, verify it moved to `agent/inbox/delivery/`

## Key Design Decisions

- **Vault-first**: Everything is .md files. No YAML, no JSON configs, no databases.
- **Session management**: Same day = resume context. New day = fresh start.
- **Token exhaustion**: Caught and logged. Agent waits for next scheduled run.
- **MCP tools**: Inherited from user's Claude Code config (`setting_sources=["user"]`).
- **Structured reasoning**: THINK/ACT/REFLECT produces visible reasoning artifacts per run.
- **Per-role memory**: Each role accumulates patterns and feedback across runs.
- **User inbox**: Structured Q&A with auto-routing replaces ad-hoc escalation.

## Authorship Convention for system-design/

Files in `system-design/` (architecture, decisions, thinking) follow a strict authorship model. The goal is to clearly distinguish **100% human-generated content** from everything else.

### Filename prefix

- **`RAW-` prefix** — Bruno is the sole author. 100% human thinking. No LLM touched the content. This is the most important signal to preserve.
- **No prefix** — LLM was involved in some capacity. The `author` metadata inside the file tells the full story.

### Metadata `author` field (4 tiers)

| Author value | Meaning |
|-------------|---------|
| `author: Bruno` | Bruno sole author. Always paired with `RAW-` filename prefix. |
| `author: Bruno (main), Claude` | Bruno's original work that Claude enhanced or added to. |
| `author: Claude (main), Bruno` | Claude's work that Bruno added his own thinking/opinions/writing to. |
| `author: Claude` | Claude sole author. Includes work that Bruno prompted but didn't add intellectual content to. |

### What counts as co-authorship

Prompting Claude to research or write something does **not** make Bruno a co-author. Co-authorship requires adding your own thinking, opinions, research, experiments, or writing to the content.

- Bruno asks Claude to research X → `author: Claude`
- Bruno iterates with Claude on X but doesn't add own thinking → `author: Claude`
- Bruno adds opinions/experiments to Claude's research → `author: Claude (main), Bruno`
- Claude expands Bruno's original note with research → `author: Bruno (main), Claude`
- Bruno writes his own raw thinking → `author: Bruno` + `RAW-` prefix
