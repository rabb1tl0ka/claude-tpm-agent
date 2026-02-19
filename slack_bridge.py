"""Slack bridge — outbound + inbound Slack integration for TPM Agent.

Python detects conditions and spawns Haiku agents that own all Slack MCP calls.
State is persisted in agent/slack/state.json within the vault.

Pattern (identical to compile_daily_summary):
  Python detects condition
    → spawns Haiku agent (setting_sources=["user"] to inherit Slack MCP OAuth)
      → agent uses slack_send_message / slack_read_channel + Write
        → results written to agent/slack/state.json in vault
          → Python reads state.json for logging / condition checks
"""

import json
import logging
import os
from glob import glob

import config
from claude_agent_sdk import ClaudeAgentOptions, ResultMessage, query

log = logging.getLogger("tpm-runner")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SLACK_CHANNEL = config.SLACK_CHANNEL
_vault_name = os.path.basename(config.VAULT_PATH)

_HAIKU_TOOLS = [
    "mcp__claude_ai_Slack__slack_send_message",
    "mcp__claude_ai_Slack__slack_read_channel",
    "mcp__claude_ai_Slack__slack_search_channels",
    "Read",
    "Write",
    "Glob",
]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def is_enabled() -> bool:
    return bool(SLACK_CHANNEL)


def _vault_abs() -> str:
    return os.path.abspath(config.VAULT_PATH)


def _state_path() -> str:
    return os.path.join(_vault_abs(), "agent", "slack", "state.json")


def _load_state() -> dict:
    path = _state_path()
    if os.path.isfile(path):
        try:
            with open(path) as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def _find_unposted(dir_rel: str, state: dict) -> list[str]:
    """Return .md file paths (relative to vault root) in dir_rel not in state['posted']."""
    posted = state.get("posted", {})
    full_dir = os.path.join(_vault_abs(), dir_rel)
    if not os.path.isdir(full_dir):
        return []
    results = []
    for fn in sorted(os.listdir(full_dir)):
        if not fn.endswith(".md") or fn.startswith(".") or fn == ".gitkeep":
            continue
        full = os.path.join(full_dir, fn)
        if not os.path.isfile(full):
            continue
        rel_path = f"{dir_rel}/{fn}"
        if rel_path not in posted:
            results.append(rel_path)
    return results


def _haiku_options(max_turns: int = 5) -> ClaudeAgentOptions:
    return ClaudeAgentOptions(
        model="haiku",
        allowed_tools=_HAIKU_TOOLS,
        permission_mode="bypassPermissions",
        max_turns=max_turns,
        cwd=_vault_abs(),
        setting_sources=["user"],
    )


async def _run_haiku(prompt: str, max_turns: int = 5, label: str = "slack-bridge") -> float | None:
    """Spawn a Haiku agent, return cost_usd or None on error."""
    cost_usd = None
    try:
        async for message in query(prompt=prompt, options=_haiku_options(max_turns)):
            if isinstance(message, ResultMessage):
                cost_usd = message.total_cost_usd
                log.info(f"[{label}] Done. Cost: ${cost_usd:.4f}")
    except Exception as e:
        log.warning(f"[{label}] Agent error: {e}")
    return cost_usd


# ---------------------------------------------------------------------------
# Outbound: post new user questions to Slack
# ---------------------------------------------------------------------------

async def post_new_user_questions() -> None:
    """Post unposted files from agent/inbox/user/ to Slack."""
    state = _load_state()
    unposted = _find_unposted("agent/inbox/user", state)
    if not unposted:
        return

    log.info(f"[slack-outbound] {len(unposted)} new user question(s) to post")

    files_block = "\n".join(f"- {p}" for p in unposted)
    prompt = f"""You are the TPM Agent Slack bridge. Post new role questions to Slack.

Slack channel: {SLACK_CHANNEL}
Vault root: {_vault_abs()}
State file: agent/slack/state.json

Unposted question files (paths relative to vault root):
{files_block}

Instructions:
1. For each file path listed above:
   a. Read the file content using the Read tool (full path: {_vault_abs()}/<relative_path>)
   b. Post it to {SLACK_CHANNEL} using slack_send_message. Format:
      "*[Question from <role>]* <filename_without_ext>\\n\\n<file_content>"
   c. Note the thread_ts from the response

2. After posting all files, read the current state file (agent/slack/state.json).
   If it doesn't exist, start with: {{"posted": {{}}, "last_inbound_check": null}}

3. Add each posted file to the "posted" dict:
   "<relative_path>": {{
     "thread_ts": "<ts_from_slack_response>",
     "channel": "<channel_id_from_response>",
     "posted_at": "<ISO8601_timestamp_now>"
   }}

4. Write the updated state back to agent/slack/state.json

Do all of this now. Do not skip any file.
"""
    await _run_haiku(prompt, max_turns=5, label="slack-questions")


# ---------------------------------------------------------------------------
# Outbound: post new drafts to Slack for approval
# ---------------------------------------------------------------------------

async def post_new_drafts() -> None:
    """Post unposted files from agent/outbox/*/drafts/ to Slack for approval."""
    state = _load_state()

    # Find all drafts/ directories under agent/outbox/
    outbox_root = os.path.join(_vault_abs(), "agent", "outbox")
    if not os.path.isdir(outbox_root):
        return

    all_unposted = []
    for role_name in sorted(os.listdir(outbox_root)):
        drafts_rel = f"agent/outbox/{role_name}/drafts"
        unposted = _find_unposted(drafts_rel, state)
        all_unposted.extend(unposted)

    if not all_unposted:
        return

    log.info(f"[slack-outbound] {len(all_unposted)} new draft(s) to post")

    files_block = "\n".join(f"- {p}" for p in all_unposted)
    prompt = f"""You are the TPM Agent Slack bridge. Post new communication drafts to Slack for approval.

Slack channel: {SLACK_CHANNEL}
Vault root: {_vault_abs()}
State file: agent/slack/state.json

Unposted draft files (paths relative to vault root):
{files_block}

Instructions:
1. For each file path listed above:
   a. Read the file content using the Read tool (full path: {_vault_abs()}/<relative_path>)
   b. Post it to {SLACK_CHANNEL} using slack_send_message. Format:
      "*[Draft for approval — <role>]* <filename_without_ext>\\n\\n<file_content>\\n\\n_Reply APPROVE or REJECT in this thread._"
   c. Note the thread_ts from the response

2. After posting all files, read the current state file (agent/slack/state.json).
   If it doesn't exist, start with: {{"posted": {{}}, "last_inbound_check": null}}

3. Add each posted file to the "posted" dict:
   "<relative_path>": {{
     "thread_ts": "<ts_from_slack_response>",
     "channel": "<channel_id_from_response>",
     "posted_at": "<ISO8601_timestamp_now>"
   }}

4. Write the updated state back to agent/slack/state.json

Do all of this now. Do not skip any file.
"""
    await _run_haiku(prompt, max_turns=5, label="slack-drafts")


# ---------------------------------------------------------------------------
# Outbound: post role run summary
# ---------------------------------------------------------------------------

async def post_role_run_summary(role_name: str, cost_usd: float | None, log_path: str) -> None:
    """Post the full latest run section from the role log to Slack."""
    cost_str = f"${cost_usd:.4f}" if cost_usd is not None else "unknown"
    channel_name = SLACK_CHANNEL.lstrip("#")
    prompt = f"""You are the TPM Agent Slack bridge. Post a role run log to Slack.

Slack channel: {SLACK_CHANNEL}
Vault root: {_vault_abs()}

Role: {role_name}
Cost: {cost_str}
Log file: {log_path}

Instructions:
1. Use slack_search_channels with query="{channel_name}" to get the channel ID.

2. Read the log file at {_vault_abs()}/{log_path}

3. Extract the most recent run section — everything from the last "## Run HH:MM" header
   to the end of the file (including Inbox, What Changed, Priority Action, Not Doing, Reflection).

4. Post to the channel ID from step 1 using slack_send_message:
   Header line: "*[{role_name}]* run complete · cost {cost_str}"
   Then the full extracted run section as-is (markdown preserved).

Post now.
"""
    await _run_haiku(prompt, max_turns=4, label=f"slack-summary-{role_name}")


# ---------------------------------------------------------------------------
# Inbound: read Slack for commands → write trigger files
# ---------------------------------------------------------------------------

async def check_slack_inbound() -> None:
    """Read Slack since last_inbound_check. Write trigger files for 'run <role>' commands."""
    state = _load_state()
    last_check = state.get("last_inbound_check", "")
    valid_roles = config.list_roles()
    roles_list = ", ".join(valid_roles)

    prompt = f"""You are the TPM Agent Slack bridge. Check for inbound commands from the user.

Slack channel: {SLACK_CHANNEL}
Vault root: {_vault_abs()}
State file: agent/slack/state.json
Valid roles: {roles_list}
Last check timestamp: {last_check or "none (first run — check recent messages)"}

Instructions:
1. Read the last 20 messages from {SLACK_CHANNEL} using slack_read_channel.
   If last_check is set, only process messages newer than that timestamp.

2. Look for messages matching the pattern: "run <role_name>"
   (case-insensitive, e.g. "run delivery", "Run Delivery", "RUN DELIVERY")
   Only process roles in this list: {roles_list}

3. For each matching command found:
   a. Determine the role name (lowercase)
   b. Write a trigger file to agent/inbox/<role_name>/ with filename:
      slack-run-<timestamp>.md
      Content:
      ---
      from: user (slack)
      date: <ISO8601_now>
      priority: high
      ---

      User requested manual run via Slack.
   c. Log what you wrote

4. Read the current state file (agent/slack/state.json).
   If it doesn't exist, start with: {{"posted": {{}}, "last_inbound_check": null}}

5. Update "last_inbound_check" to the current ISO8601 timestamp.
   Write the updated state back to agent/slack/state.json.

Do all of this now. If no matching commands found, still update last_inbound_check.
"""
    await _run_haiku(prompt, max_turns=5, label="slack-inbound")
