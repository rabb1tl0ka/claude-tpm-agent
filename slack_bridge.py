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
import re

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
# State helpers
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


def _save_state(state: dict) -> None:
    """Write state dict to agent/slack/state.json."""
    path = _state_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(state, f, indent=2)


def _get_cached_channel_id() -> str | None:
    """Return cached channel_id from state.json, or None if not set."""
    return _load_state().get("channel_id")


def _set_cached_channel_id(channel_id: str) -> None:
    """Cache channel_id in state.json."""
    state = _load_state()
    state["channel_id"] = channel_id
    _save_state(state)


def _channel_id_prompt_block() -> str:
    """Generate the channel-resolution instruction block for agent prompts."""
    cached = _get_cached_channel_id()
    if cached:
        return f"Channel ID: {cached} (use directly — no search needed)"
    channel_name = SLACK_CHANNEL.lstrip("#")
    return (
        f"Step 0: Use slack_search_channels with query=\"{channel_name}\" to get the channel ID.\n"
        f"Read agent/slack/state.json, add {{\"channel_id\": \"<id>\"}}, write it back before posting."
    )


# ---------------------------------------------------------------------------
# Content helpers (pure Python — no agent turns)
# ---------------------------------------------------------------------------

def _parse_frontmatter_from(content: str) -> str | None:
    """Extract the 'from:' value from YAML frontmatter. Returns None if not found."""
    if not content.startswith("---"):
        return None
    end = content.find("---", 3)
    if end == -1:
        return None
    frontmatter = content[3:end]
    for line in frontmatter.splitlines():
        line = line.strip()
        if line.startswith("from:"):
            return line[5:].strip()
    return None


def _extract_last_run_section(log_full_path: str) -> tuple[str, str] | None:
    """Extract the last ## Run section from a role log file.

    Returns (reflect_text, full_section_text), or None if no ## Run header found.
    reflect_text is the content of the ### Reflection subsection (empty string if absent).
    full_section_text is everything from the last ## Run header to end of file.
    """
    if not os.path.isfile(log_full_path):
        return None

    with open(log_full_path) as f:
        content = f.read()

    lines = content.splitlines()

    # Find index of last ## Run HH:MM header
    last_run_idx = None
    for i, line in enumerate(lines):
        if re.match(r"^## Run \d{2}:\d{2}", line):
            last_run_idx = i

    if last_run_idx is None:
        return None

    section_lines = lines[last_run_idx:]
    full_section_text = "\n".join(section_lines)

    # Extract ### Reflection subsection
    reflect_lines = []
    in_reflection = False
    for line in section_lines:
        if line.startswith("### Reflection"):
            in_reflection = True
            continue
        if in_reflection:
            if line.startswith("### ") or line.startswith("## "):
                break
            reflect_lines.append(line)

    reflect_text = "\n".join(reflect_lines).strip()
    return (reflect_text, full_section_text)


def _find_inter_agent_messages(state: dict) -> list[dict]:
    """Scan all agent/inbox/{role}/ dirs for unposted inter-agent messages.

    An inter-agent message has a `from:` frontmatter value that matches a known
    role name (e.g. 'delivery', 'risk'). Files from 'user (slack)' are excluded.

    Returns list of {rel_path, from_role, to_role, content} dicts.
    """
    posted = state.get("posted", {})
    valid_roles = set(config.list_roles())
    vault = _vault_abs()
    results = []

    for to_role in sorted(valid_roles):
        inbox_dir = os.path.join(vault, "agent", "inbox", to_role)
        if not os.path.isdir(inbox_dir):
            continue
        for fn in sorted(os.listdir(inbox_dir)):
            if not fn.endswith(".md") or fn.startswith(".") or fn == ".gitkeep":
                continue
            full = os.path.join(inbox_dir, fn)
            if not os.path.isfile(full):
                continue
            rel_path = f"agent/inbox/{to_role}/{fn}"
            if rel_path in posted:
                continue
            try:
                with open(full) as f:
                    content = f.read()
            except Exception:
                continue
            from_role = _parse_frontmatter_from(content)
            if from_role and from_role in valid_roles:
                results.append({
                    "rel_path": rel_path,
                    "from_role": from_role,
                    "to_role": to_role,
                    "content": content,
                })

    return results


def _get_persona(role_cfg: dict) -> dict:
    """Return Slack persona dict for a role, with fallbacks."""
    s = role_cfg.get("slack", {})
    return {
        "username": s.get("username", role_cfg.get("display_name", role_cfg["name"])),
        "emoji": s.get("emoji", ":robot_face:"),
        "mention": s.get("mention", f"@{role_cfg['name']}"),
    }


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


# ---------------------------------------------------------------------------
# Agent helpers
# ---------------------------------------------------------------------------

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
# Outbound: post role run log (with persona, Reflection as main + full in thread)
# ---------------------------------------------------------------------------

async def post_role_run_log(role_name: str, role_cfg: dict, cost_usd: float | None, log_path: str) -> None:
    """Post the latest run's Reflection as main post + full section as thread reply."""
    log_full_path = os.path.join(_vault_abs(), log_path)
    result = _extract_last_run_section(log_full_path)
    if result is None:
        log.warning(f"[slack-log] No ## Run section in {log_path}, skipping Slack post")
        return

    reflect_text, full_section_text = result
    persona = _get_persona(role_cfg)
    cost_str = f"${cost_usd:.4f}" if cost_usd is not None else "unknown"
    channel_block = _channel_id_prompt_block()

    main_text = f"*[{persona['username']}]* {persona['emoji']} run complete · {cost_str}"
    if reflect_text:
        main_text += f"\n\n### Reflection\n{reflect_text}"

    prompt = f"""You are the TPM Agent Slack bridge. Post a role run log to Slack using the role's persona.

{channel_block}

Slack channel: {SLACK_CHANNEL}
Vault root: {_vault_abs()}
State file: agent/slack/state.json

Main message text:
---
{main_text}
---

Thread reply text (full run section):
---
{full_section_text}
---

Instructions:
1. Resolve the channel ID (see above).
2. Post the main message using slack_send_message:
   - channel: <channel_id>
   - text: <main message text above>
   - username: {persona['username']}
   - icon_emoji: {persona['emoji']}
   Save the ts from the response as main_ts.
3. Post the thread reply using slack_send_message:
   - channel: <channel_id>
   - text: <thread reply text above>
   - thread_ts: <main_ts>
   - username: {persona['username']}
   - icon_emoji: {persona['emoji']}
4. Read agent/slack/state.json (start with {{}} if missing).
   If step 1 found a new channel_id not already in state, add it.
   Write updated state back to agent/slack/state.json.

Post now.
"""
    await _run_haiku(prompt, max_turns=5, label=f"slack-log-{role_name}")


# ---------------------------------------------------------------------------
# Outbound: post inter-agent messages with sender persona
# ---------------------------------------------------------------------------

async def post_inter_agent_messages() -> None:
    """Post unposted inter-agent inbox messages to Slack with sender persona."""
    state = _load_state()
    messages = _find_inter_agent_messages(state)
    if not messages:
        return

    log.info(f"[slack-outbound] {len(messages)} inter-agent message(s) to post")

    # Enrich each message with persona info (resolved in Python)
    enriched = []
    for msg in messages:
        try:
            from_cfg = config.load_role(msg["from_role"])
            to_cfg = config.load_role(msg["to_role"])
            from_persona = _get_persona(from_cfg)
            to_persona = _get_persona(to_cfg)
        except Exception:
            from_persona = {"username": msg["from_role"], "emoji": ":robot_face:", "mention": f"@{msg['from_role']}"}
            to_persona = {"username": msg["to_role"], "emoji": ":robot_face:", "mention": f"@{msg['to_role']}"}
        enriched.append({
            **msg,
            "from_username": from_persona["username"],
            "from_emoji": from_persona["emoji"],
            "to_username": to_persona["username"],
            "to_emoji": to_persona["emoji"],
        })

    channel_block = _channel_id_prompt_block()
    messages_json = json.dumps(enriched, indent=2)

    prompt = f"""You are the TPM Agent Slack bridge. Post inter-agent messages to Slack.

{channel_block}

Slack channel: {SLACK_CHANNEL}
Vault root: {_vault_abs()}
State file: agent/slack/state.json

Messages to post (JSON):
{messages_json}

Instructions:
1. Resolve the channel ID (see above).
2. For each message in the JSON array:
   a. Format the message text as:
      "*[<from_username>]* <from_emoji> → *<to_username>* <to_emoji>\\n\\n<content>"
   b. Post using slack_send_message:
      - channel: <channel_id>
      - text: <formatted text>
      - username: <from_username>
      - icon_emoji: <from_emoji>
   c. Note the thread_ts from the response.
3. Read agent/slack/state.json (start with {{"posted": {{}}, "last_inbound_check": null}} if missing).
   If step 1 found a new channel_id, add it.
   For each posted message, add to "posted" dict:
     "<rel_path>": {{"thread_ts": "<ts>", "channel": "<channel_id>", "posted_at": "<ISO8601_now>"}}
4. Write updated state back to agent/slack/state.json.

Do all of this now. Do not skip any message.
"""
    await _run_haiku(prompt, max_turns=8, label="slack-inter-agent")


# ---------------------------------------------------------------------------
# Outbound: post new user questions to Slack (with asking role persona)
# ---------------------------------------------------------------------------

async def post_new_user_questions() -> None:
    """Post unposted files from agent/inbox/user/ to Slack with the asking role's persona."""
    state = _load_state()
    unposted = _find_unposted("agent/inbox/user", state)
    if not unposted:
        return

    log.info(f"[slack-outbound] {len(unposted)} new user question(s) to post")

    # Enrich each question with persona info (resolved in Python)
    enriched = []
    vault = _vault_abs()
    for rel_path in unposted:
        full = os.path.join(vault, rel_path)
        try:
            with open(full) as f:
                content = f.read()
        except Exception:
            content = "(could not read file)"
        from_role = _parse_frontmatter_from(content)
        if from_role:
            try:
                role_cfg = config.load_role(from_role)
                persona = _get_persona(role_cfg)
            except Exception:
                persona = {"username": from_role, "emoji": ":robot_face:", "mention": f"@{from_role}"}
        else:
            persona = {"username": "Agent", "emoji": ":robot_face:", "mention": "@agent"}
        enriched.append({
            "rel_path": rel_path,
            "content": content,
            "username": persona["username"],
            "emoji": persona["emoji"],
        })

    channel_block = _channel_id_prompt_block()
    messages_json = json.dumps(enriched, indent=2)

    prompt = f"""You are the TPM Agent Slack bridge. Post role questions to Slack.

{channel_block}

Slack channel: {SLACK_CHANNEL}
Vault root: {_vault_abs()}
State file: agent/slack/state.json

Questions to post (JSON):
{messages_json}

Instructions:
1. Resolve the channel ID (see above).
2. For each question in the JSON array:
   a. Format the message as:
      "*[<username>]* <emoji> question for Bruno\\n\\n<content>"
   b. Post using slack_send_message:
      - channel: <channel_id>
      - text: <formatted text>
      - username: <username>
      - icon_emoji: <emoji>
   c. Note the thread_ts from the response.
3. Read agent/slack/state.json (start with {{"posted": {{}}, "last_inbound_check": null}} if missing).
   If step 1 found a new channel_id, add it.
   For each posted question, add to "posted" dict:
     "<rel_path>": {{"thread_ts": "<ts>", "channel": "<channel_id>", "posted_at": "<ISO8601_now>"}}
4. Write updated state back to agent/slack/state.json.

Do all of this now. Do not skip any question.
"""
    await _run_haiku(prompt, max_turns=6, label="slack-questions")


# ---------------------------------------------------------------------------
# Outbound: post new drafts to Slack for approval (with role persona)
# ---------------------------------------------------------------------------

async def post_new_drafts() -> None:
    """Post unposted files from agent/outbox/*/drafts/ to Slack for approval."""
    state = _load_state()

    outbox_root = os.path.join(_vault_abs(), "agent", "outbox")
    if not os.path.isdir(outbox_root):
        return

    # Enrich each draft with persona info (resolved in Python)
    enriched = []
    vault = _vault_abs()
    for role_name in sorted(os.listdir(outbox_root)):
        drafts_rel = f"agent/outbox/{role_name}/drafts"
        unposted = _find_unposted(drafts_rel, state)
        for rel_path in unposted:
            full = os.path.join(vault, rel_path)
            try:
                with open(full) as f:
                    content = f.read()
            except Exception:
                content = "(could not read file)"
            try:
                role_cfg = config.load_role(role_name)
                persona = _get_persona(role_cfg)
            except Exception:
                persona = {"username": role_name, "emoji": ":robot_face:", "mention": f"@{role_name}"}
            enriched.append({
                "rel_path": rel_path,
                "content": content,
                "username": persona["username"],
                "emoji": persona["emoji"],
            })

    if not enriched:
        return

    log.info(f"[slack-outbound] {len(enriched)} new draft(s) to post")

    channel_block = _channel_id_prompt_block()
    messages_json = json.dumps(enriched, indent=2)

    prompt = f"""You are the TPM Agent Slack bridge. Post communication drafts to Slack for approval.

{channel_block}

Slack channel: {SLACK_CHANNEL}
Vault root: {_vault_abs()}
State file: agent/slack/state.json

Drafts to post (JSON):
{messages_json}

Instructions:
1. Resolve the channel ID (see above).
2. For each draft in the JSON array:
   a. Format the message as:
      "*[<username>]* <emoji> draft for approval\\n\\n<content>\\n\\n_Reply APPROVE or REJECT in this thread._"
   b. Post using slack_send_message:
      - channel: <channel_id>
      - text: <formatted text>
      - username: <username>
      - icon_emoji: <emoji>
   c. Note the thread_ts from the response.
3. Read agent/slack/state.json (start with {{"posted": {{}}, "last_inbound_check": null}} if missing).
   If step 1 found a new channel_id, add it.
   For each posted draft, add to "posted" dict:
     "<rel_path>": {{"thread_ts": "<ts>", "channel": "<channel_id>", "posted_at": "<ISO8601_now>"}}
4. Write updated state back to agent/slack/state.json.

Do all of this now. Do not skip any draft.
"""
    await _run_haiku(prompt, max_turns=6, label="slack-drafts")


# ---------------------------------------------------------------------------
# Inbound: read Slack for commands → write trigger files
# ---------------------------------------------------------------------------

_INBOUND_INTERVAL_SECS = 300  # check Slack inbound at most every 5 minutes


async def check_slack_inbound() -> None:
    """Read Slack since last_inbound_check. Write trigger files for commands.

    Matches:
    - 'run <role>' — trigger a role run
    - '@<mention>' — route message to that role's inbox (e.g. @delivery-manager)

    Skips the agent spawn entirely if checked less than _INBOUND_INTERVAL_SECS ago.
    Python owns last_inbound_check — written before spawning the agent so the gate
    works correctly regardless of agent behavior.
    """
    from datetime import datetime, timezone

    state = _load_state()
    last_check = state.get("last_inbound_check", "")

    if last_check:
        try:
            last_dt = datetime.fromisoformat(last_check.replace("Z", "+00:00"))
            elapsed = (datetime.now(timezone.utc) - last_dt).total_seconds()
            if elapsed < _INBOUND_INTERVAL_SECS:
                return
        except Exception:
            pass

    # Python sets the gate BEFORE spawning the agent — no longer delegated to Haiku
    state["last_inbound_check"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    _save_state(state)

    valid_roles = config.list_roles()
    roles_list = ", ".join(valid_roles)

    # Build mention→role mapping from all role configs
    mention_map = {}
    for r in valid_roles:
        try:
            rcfg = config.load_role(r)
            mention = rcfg.get("slack", {}).get("mention", f"@{r}")
            mention_map[mention] = r
        except Exception:
            pass
    mention_map_json = json.dumps(mention_map)
    channel_block = _channel_id_prompt_block()

    prompt = f"""You are the TPM Agent Slack bridge. Check for inbound commands from the user.

{channel_block}

Slack channel: {SLACK_CHANNEL}
Vault root: {_vault_abs()}
State file: agent/slack/state.json
Valid roles: {roles_list}
Last check timestamp: {last_check or "none (first run — check recent messages)"}
Mention→role map: {mention_map_json}

Instructions:
1. Resolve the channel ID (see above).
2. Read the last 20 messages from the channel using slack_read_channel.
   If last_check is set, only process messages newer than that timestamp.

3. Look for two patterns (case-insensitive):
   a. "run <role_name>" — e.g. "run delivery", "Run Risk"
      → role = matched role name (lowercase)
   b. "@<mention>" — e.g. "@delivery-manager", "@risk-manager"
      → use the mention→role map above to find the role
      → route the FULL original message as trigger content

4. For each matched command:
   a. Determine the role name (lowercase)
   b. Write a trigger file to agent/inbox/<role_name>/ with filename:
      slack-<timestamp>.md  (use current UTC timestamp as YYYYMMDDTHHMMSS)
      Content:
      ---
      from: user (slack)
      date: <ISO8601_now>
      priority: high
      ---

      User message via Slack: <original message text>
   c. Log what you wrote

5. If step 1 found a new channel_id not already in state:
   Read agent/slack/state.json, add {{"channel_id": "<id>"}}, write it back.

Do all of this now. Write trigger files for every matching command found.
"""
    await _run_haiku(prompt, max_turns=6, label="slack-inbound")
