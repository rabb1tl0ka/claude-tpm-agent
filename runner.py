#!/usr/bin/env python3
"""Claude TPM Agent Runner — schedules role-based runs using Claude Code.

Usage:
    python3 runner.py                      # Run scheduler (long-running)
    python3 runner.py --once               # Check all roles once, then exit
    python3 runner.py --role delivery      # Run a single role immediately
    python3 runner.py --dry-run            # Show what would run
    python3 runner.py --role comms --once  # Run comms once, then exit
"""

import argparse
import asyncio
import json
import logging
import os
import re
import sys
import time
from datetime import datetime, timedelta, timezone

import schedule

import config
from claude_agent_sdk import (
    ClaudeAgentOptions,
    ResultMessage,
    AssistantMessage,
    query,
)

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

def setup_logging() -> logging.Logger:
    log_dir = os.path.join(os.path.dirname(__file__), "logs")
    os.makedirs(log_dir, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H%M%S")
    log_file = os.path.join(log_dir, f"{timestamp}_runner.log")

    logger = logging.getLogger("tpm-runner")
    logger.setLevel(logging.DEBUG)

    fh = logging.FileHandler(log_file)
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))

    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(logging.Formatter("%(message)s"))

    logger.addHandler(fh)
    logger.addHandler(ch)

    logger.info(f"Runner log: {log_file}")
    return logger


log = setup_logging()


# ---------------------------------------------------------------------------
# Session management — resume same day, fresh next day
# ---------------------------------------------------------------------------

def _sessions_file() -> str:
    os.makedirs(config.SESSIONS_DIR, exist_ok=True)
    return os.path.join(config.SESSIONS_DIR, "sessions.json")


def _load_sessions() -> dict:
    path = _sessions_file()
    if os.path.isfile(path):
        with open(path) as f:
            return json.load(f)
    return {}


def _save_sessions(sessions: dict):
    with open(_sessions_file(), "w") as f:
        json.dump(sessions, f, indent=2)


def get_session_id(role_name: str) -> str | None:
    """Get existing session ID for a role if it's from today. Otherwise None (fresh start)."""
    sessions = _load_sessions()
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    entry = sessions.get(role_name)
    if entry and entry.get("date") == today:
        return entry.get("session_id")
    return None


def save_session_id(role_name: str, session_id: str):
    """Save session ID for a role with today's date."""
    sessions = _load_sessions()
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    sessions[role_name] = {"session_id": session_id, "date": today}
    _save_sessions(sessions)


# ---------------------------------------------------------------------------
# Vault helpers
# ---------------------------------------------------------------------------

def load_vault_system_prompt() -> str:
    """Load the vault's CLAUDE.md as the base system prompt."""
    claude_md = os.path.join(config.VAULT_PATH, "CLAUDE.md")
    if not os.path.isfile(claude_md):
        return "You are a TPM AI agent. Help manage the project."
    with open(claude_md) as f:
        return f.read()


def load_role_context(role_cfg: dict) -> str:
    """Read only the context files specified in the role config."""
    parts = []
    for rel in role_cfg["context_files"]:
        full = os.path.join(config.VAULT_PATH, rel)
        if os.path.isfile(full):
            with open(full) as f:
                content = f.read()
            parts.append(f"--- {rel} ---\n{content}")
        elif os.path.isdir(full):
            entries = sorted(os.listdir(full))
            listing = [e for e in entries if not e.startswith(".")]
            parts.append(f"--- {rel} ---\n(directory: {', '.join(listing) if listing else 'empty'})")
    return "\n\n".join(parts)


def check_inbox(role_cfg: dict) -> str:
    """Read any trigger files in the role's inbox."""
    inbox_path = os.path.join(config.VAULT_PATH, role_cfg["inbox"])
    if not os.path.isdir(inbox_path):
        return ""
    files = []
    for fn in sorted(os.listdir(inbox_path)):
        full = os.path.join(inbox_path, fn)
        if os.path.isfile(full) and fn != ".gitkeep":
            with open(full) as f:
                content = f.read()
            files.append(f"--- inbox: {fn} ---\n{content}")
    return "\n\n".join(files)


def has_inbox_items(role_name: str) -> bool:
    """Check if a role's inbox has unprocessed trigger files."""
    role_cfg = config.load_role(role_name)
    inbox_path = os.path.join(config.VAULT_PATH, role_cfg["inbox"])
    if not os.path.isdir(inbox_path):
        return False
    for fn in os.listdir(inbox_path):
        full = os.path.join(inbox_path, fn)
        if os.path.isfile(full) and fn != ".gitkeep":
            return True
    return False


# ---------------------------------------------------------------------------
# Prompt building
# ---------------------------------------------------------------------------

def build_role_system_prompt(role_cfg: dict) -> str:
    """Build a role-specific system prompt with THINK/ACT/REFLECT cycle."""
    base = load_vault_system_prompt()
    role_name = role_cfg["name"]
    goals_str = "\n".join(f"- {g}" for g in role_cfg["goals"])

    preferences = role_cfg["preferences"]
    prefs_section = ""
    if preferences and not preferences.startswith("(No preferences"):
        prefs_section = f"\n\n## User Preferences\n{preferences}"

    role_prompt = f"""
## Your Role: {role_cfg['display_name']}

### Mission
{role_cfg['mission']}

### Goals
{goals_str}
{prefs_section}

## Operating Rules

1. **NEVER send communications directly.** Always draft to `agent/outbox/{role_name}/drafts/`. Bruno reviews and approves.
2. **Be concise.** Short, clear updates. No fluff. Logistics people value directness.
3. **Flag risks early.** If something smells like a delay or blocker, surface it immediately.
4. **Update context files.** When you learn something new, update `context/` so future cycles have it.
5. **Respect the vault as source of truth.** Read vault files before making assumptions.

## How to Work — THINK / ACT / REFLECT

Your working directory is the project vault. All file paths are relative to it.

### Phase 1: THINK

Write a structured reasoning log to `agent/logs/{role_name}/YYYY-MM-DDTHH-MM-<trigger>.md` where `<trigger>` is "scheduled", "inbox", or "manual" depending on why you were triggered.

Your reasoning log MUST include these sections:

```
# {role_cfg['display_name']} — YYYY-MM-DDTHH:MM Run

## Inbox
- (list items with priority, or "empty")

## What Changed
- (changes since last run based on context files)

## Priority Action
- (what you will do this run and why)

## Not Doing
- (what you considered but deferred, and why)
```

### Phase 2: ACT

Execute your priority action:
- Update context files (`context/`) when you learn new information
- Write trigger files to other roles' inboxes when they need to know something
- Draft communications to `agent/outbox/{role_name}/drafts/`
- Ask questions to the User via `agent/inbox/user/` (see format below)
- After processing inbox files, move them to `{role_cfg['inbox']}archive/`

### Phase 3: REFLECT

Append a `## Reflection` section to your reasoning log:
- What went well? What was unclear?
- Any patterns you're noticing across runs?

If you noticed a recurring pattern or received feedback, update `agent/memory/{role_name}.md`.

## Question Format (for User)

When you need to ask the User a question, write a file to `agent/inbox/user/`:

Filename: `YYYY-MM-DDTHH-MM-<short-description>.md`

```
---
id: YYYY-MM-DDTHH-MM-<short-description>
from: {role_name}
to: user
date: YYYY-MM-DDTHH:MM:SSZ
status: open
---

<your question here>
```

## Trigger File Format

When writing triggers to other roles' inboxes:

```
---
from: {role_name}
date: YYYY-MM-DDTHH:MM:SSZ
priority: low|medium|high
---

<description of what happened and what the other role should do>
```

## Feedback Processing

If you find answered questions or feedback in your inbox:
1. Read and incorporate the feedback
2. Update `agent/memory/{role_name}.md` with any lessons learned
3. Move the file to `{role_cfg['inbox']}archive/`
"""
    return base + "\n\n" + role_prompt


def build_role_message(role_cfg: dict) -> str:
    """Build the initial user message for a role-based run."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    context = load_role_context(role_cfg)
    inbox = check_inbox(role_cfg)

    parts = [
        f"Current time: {now}",
        f"Today's date: {today}",
        f"Role: {role_cfg['display_name']}",
        "",
        "## Project Context",
        context,
    ]

    if inbox:
        parts += ["", "## Inbox (trigger messages for you)", inbox]
    else:
        parts += ["", "## Inbox", "(empty — no pending triggers)"]

    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Running a role via Claude Code SDK
# ---------------------------------------------------------------------------

async def run_role_async(role_name: str, reason: str):
    """Invoke Claude Code for a role run via the Agent SDK."""
    role_cfg = config.load_role(role_name)

    log.info(f"[{role_name}] Triggered — {reason}")
    log.info(f"[{role_name}] Model: {role_cfg['model']}")

    system_prompt = build_role_system_prompt(role_cfg)
    user_message = build_role_message(role_cfg)

    log.debug(f"[{role_name}] System prompt: {len(system_prompt)} chars")
    log.debug(f"[{role_name}] User message: {len(user_message)} chars")
    log.debug(f"[{role_name}] Tools: {role_cfg['tools']}")

    # Session management: resume same day, fresh next day
    session_id = get_session_id(role_name)
    if session_id:
        log.info(f"[{role_name}] Resuming session: {session_id[:12]}...")
    else:
        log.info(f"[{role_name}] Starting fresh session")

    vault_abs = os.path.abspath(config.VAULT_PATH)

    options = ClaudeAgentOptions(
        model=role_cfg["model"],
        system_prompt=system_prompt,
        allowed_tools=role_cfg["tools"],
        permission_mode="bypassPermissions",
        max_turns=10,
        cwd=vault_abs,
        setting_sources=["user"],
        resume=session_id,
    )

    try:
        new_session_id = None
        async for message in query(prompt=user_message, options=options):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if hasattr(block, "text") and block.text:
                        preview = block.text[:300]
                        log.info(f"[{role_name}] {preview}{'...' if len(block.text) > 300 else ''}")
                        log.debug(f"[{role_name}] Full: {block.text}")
                # Track session ID from assistant messages
                if hasattr(message, "session_id") and message.session_id:
                    new_session_id = message.session_id

            elif isinstance(message, ResultMessage):
                log.info(f"[{role_name}] Done. Duration: {message.duration_ms}ms, Cost: ${message.total_cost_usd:.4f}")
                if hasattr(message, "session_id") and message.session_id:
                    new_session_id = message.session_id

        # Save session for same-day resumption
        if new_session_id:
            save_session_id(role_name, new_session_id)

    except Exception as e:
        error_str = str(e).lower()
        if "rate" in error_str or "limit" in error_str or "quota" in error_str or "token" in error_str:
            log.warning(f"[{role_name}] Token/rate limit hit: {e}. Will retry next scheduled run.")
        else:
            log.error(f"[{role_name}] Error: {e}")


def run_role(role_name: str, reason: str, dry_run: bool = False):
    """Sync wrapper for run_role_async. Used by the scheduler."""
    log.info(f"[{role_name}] Triggered — {reason}")

    if dry_run:
        role_cfg = config.load_role(role_name)
        log.info(f"[{role_name}] DRY RUN — model: {role_cfg['model']}, tools: {role_cfg['tools']}")
        return

    asyncio.run(run_role_async(role_name, reason))


# ---------------------------------------------------------------------------
# Schedule parsing
# ---------------------------------------------------------------------------

def parse_schedule(role_name: str, schedule_text: str, dry_run: bool = False):
    """Parse a human-readable schedule and register with the schedule library."""
    text = schedule_text.lower().strip()

    if "on-demand" in text:
        log.info(f"[{role_name}] Schedule: on-demand (inbox-triggered only)")
        return

    # "every N minutes"
    match = re.search(r"every\s+(\d+)\s+minute", text)
    if match:
        minutes = int(match.group(1))
        schedule.every(minutes).minutes.do(run_role, role_name, f"scheduled (every {minutes}min)", dry_run)
        log.info(f"[{role_name}] Schedule: every {minutes} minutes")
        return

    # Time-based: "9am", "9am and 5pm", "10am"
    times = re.findall(r"(\d{1,2})\s*(am|pm)", text)
    if times:
        for hour_str, ampm in times:
            hour = int(hour_str)
            if ampm == "pm" and hour != 12:
                hour += 12
            if ampm == "am" and hour == 12:
                hour = 0
            time_str = f"{hour:02d}:00"
            schedule.every().day.at(time_str).do(run_role, role_name, f"scheduled ({time_str})", dry_run)
            log.info(f"[{role_name}] Schedule: daily at {time_str}")
        return

    log.warning(f"[{role_name}] Could not parse schedule: '{schedule_text}' — inbox-triggered only")


# ---------------------------------------------------------------------------
# Inbox polling
# ---------------------------------------------------------------------------

def route_answered_questions():
    """Route answered questions from user inbox back to the asking role.

    Scans agent/inbox/user/answered/ for files, parses the `from:` field
    from YAML frontmatter, and moves each file to the originating role's inbox.
    """
    answered_dir = os.path.join(config.VAULT_PATH, "agent", "inbox", "user", "answered")
    if not os.path.isdir(answered_dir):
        return

    valid_roles = config.list_roles()

    for fn in sorted(os.listdir(answered_dir)):
        full = os.path.join(answered_dir, fn)
        if not os.path.isfile(full) or fn.startswith("."):
            continue

        # Parse from: field from YAML frontmatter
        from_role = None
        try:
            with open(full) as f:
                content = f.read()
            # Simple frontmatter parsing: look for from: between --- delimiters
            if content.startswith("---"):
                end = content.find("---", 3)
                if end != -1:
                    frontmatter = content[3:end]
                    for line in frontmatter.splitlines():
                        line = line.strip()
                        if line.startswith("from:"):
                            from_role = line[5:].strip()
                            break
        except Exception as e:
            log.warning(f"[user-routing] Could not read {fn}: {e}")
            continue

        if not from_role:
            log.warning(f"[user-routing] No 'from:' field in {fn}, skipping")
            continue

        if from_role not in valid_roles:
            log.warning(f"[user-routing] Unknown role '{from_role}' in {fn}, skipping")
            continue

        # Move to the originating role's inbox
        dest = os.path.join(config.VAULT_PATH, "agent", "inbox", from_role, fn)
        os.rename(full, dest)
        log.info(f"[user-routing] Routed {fn} → agent/inbox/{from_role}/")


async def compile_daily_summary():
    """Compile yesterday's role logs into a single daily summary.

    Idempotent — skips if summary already exists for yesterday.
    Spawns a haiku agent with Write-only access to produce the summary.
    """
    yesterday = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d")
    summaries_dir = os.path.join(config.VAULT_PATH, "agent", "logs", "summaries")
    summary_path = os.path.join(summaries_dir, f"{yesterday}.md")

    # Idempotent: skip if already compiled
    if os.path.isfile(summary_path):
        return

    # Collect all role logs from yesterday
    logs_dir = os.path.join(config.VAULT_PATH, "agent", "logs")
    log_contents = []
    for role_name in config.list_roles():
        role_logs_dir = os.path.join(logs_dir, role_name)
        if not os.path.isdir(role_logs_dir):
            continue
        for fn in sorted(os.listdir(role_logs_dir)):
            if fn.startswith(yesterday) and fn.endswith(".md"):
                full = os.path.join(role_logs_dir, fn)
                with open(full) as f:
                    content = f.read()
                log_contents.append(f"--- {role_name}/{fn} ---\n{content}")

    if not log_contents:
        return

    vault_abs = os.path.abspath(config.VAULT_PATH)
    prompt = (
        f"Compile the following role reasoning logs from {yesterday} into a single daily summary.\n"
        f"Write the summary to agent/logs/summaries/{yesterday}.md\n\n"
        "The summary should include:\n"
        "- Key actions taken by each role\n"
        "- Decisions made\n"
        "- Questions raised\n"
        "- Risks or blockers surfaced\n\n"
        "Be concise — this is a reference document, not a narrative.\n\n"
        + "\n\n".join(log_contents)
    )

    options = ClaudeAgentOptions(
        model="haiku",
        allowed_tools=["Write"],
        permission_mode="bypassPermissions",
        max_turns=3,
        cwd=vault_abs,
    )

    try:
        async for message in query(prompt=prompt, options=options):
            if isinstance(message, ResultMessage):
                log.info(f"[daily-summary] Compiled {yesterday} summary. Cost: ${message.total_cost_usd:.4f}")
    except Exception as e:
        log.warning(f"[daily-summary] Failed to compile {yesterday}: {e}")


def check_all_inboxes(dry_run: bool = False):
    """Check all role inboxes and trigger runs for any with pending items."""
    route_answered_questions()
    for role_name in config.list_roles():
        if has_inbox_items(role_name):
            run_role(role_name, "inbox trigger", dry_run)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Claude TPM Agent Runner")
    parser.add_argument("--role", type=str, default=None, help="Run a specific role immediately")
    parser.add_argument("--once", action="store_true", help="Check once and exit (or run --role once)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would run, don't execute")
    args = parser.parse_args()

    roles = config.list_roles()
    log.info(f"=== Claude TPM Agent Runner ===")
    log.info(f"Roles: {', '.join(roles)}")
    log.info(f"Vault: {os.path.abspath(config.VAULT_PATH)}")

    # Single role mode
    if args.role:
        if args.role not in roles:
            log.error(f"Unknown role: {args.role}. Available: {', '.join(roles)}")
            sys.exit(1)
        run_role(args.role, "manual", args.dry_run)
        return

    # Once mode: check inboxes, run what's needed, exit
    if args.once:
        log.info("Mode: single check")
        check_all_inboxes(dry_run=args.dry_run)
        log.info("Done.")
        return

    # Scheduler mode: register schedules + poll inboxes
    for role_name in roles:
        role_cfg = config.load_role(role_name)
        parse_schedule(role_name, role_cfg["schedule"], dry_run=args.dry_run)

    log.info("Runner started. Press Ctrl+C to stop.")
    try:
        while True:
            schedule.run_pending()
            check_all_inboxes(dry_run=args.dry_run)
            asyncio.run(compile_daily_summary())
            time.sleep(60)
    except KeyboardInterrupt:
        log.info("Runner stopped.")


if __name__ == "__main__":
    main()
