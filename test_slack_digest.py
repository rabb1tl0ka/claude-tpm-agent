#!/usr/bin/env python3
"""Integration test for post_digest().

Creates fixture files (question + inter-agent message), calls post_digest(),
then spawns a Haiku agent to verify the digest appeared in Slack with correct format.

Must be run OUTSIDE Claude Code (from terminal directly).

Usage:
    python3 test_slack_digest.py

Exits 0 on pass, 1 on fail.
"""

import asyncio
import json
import os
import sys
import uuid
from datetime import datetime, timezone

import config
import slack_bridge
from claude_agent_sdk import ClaudeAgentOptions, ResultMessage, query

_VAULT = os.path.abspath(config.VAULT_PATH)
_RESULT_PATH = os.path.join(_VAULT, "agent", "slack", "digest_test_result.json")


async def run_test() -> bool:
    test_id = str(uuid.uuid4())[:8]
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M")
    print(f"[test_digest] test_id: {test_id}")
    print(f"[test_digest] channel: {slack_bridge.SLACK_CHANNEL}")

    os.makedirs(os.path.join(_VAULT, "agent", "slack"), exist_ok=True)

    # ── Fixture 1: question from risk ──────────────────────────────────
    q_dir = os.path.join(_VAULT, "agent", "inbox", "user")
    os.makedirs(q_dir, exist_ok=True)
    q_fn = f"{now}-digest-test-{test_id}.md"
    q_rel = f"agent/inbox/user/{q_fn}"
    with open(os.path.join(_VAULT, q_rel), "w") as f:
        f.write(
            f"---\nfrom: risk\nto: user\ndate: 2026-02-21T00:00:00Z\nstatus: open\n---\n\n"
            f"Digest test {test_id}: Should we escalate the Week 3 capacity risk to the client?\n"
        )

    # ── Fixture 2: inter-agent (delivery → risk) ───────────────────────
    ia_dir = os.path.join(_VAULT, "agent", "inbox", "risk")
    os.makedirs(ia_dir, exist_ok=True)
    ia_fn = f"{now}-digest-ia-{test_id}.md"
    ia_rel = f"agent/inbox/risk/{ia_fn}"
    with open(os.path.join(_VAULT, ia_rel), "w") as f:
        f.write(
            f"---\nfrom: delivery\ndate: 2026-02-21T00:00:00Z\npriority: medium\n---\n\n"
            f"Digest inter-agent test {test_id}: flagging capacity concern for your review.\n"
        )

    # Ensure fixtures not already in posted state
    state = slack_bridge._load_state()
    for r in [q_rel, ia_rel]:
        state.setdefault("posted", {}).pop(r, None)
    slack_bridge._save_state(state)

    # ── Call post_digest() ─────────────────────────────────────────────
    print("[test_digest] Calling post_digest()...")
    await slack_bridge.post_digest()

    # ── Verify in Slack ────────────────────────────────────────────────
    channel_id = slack_bridge._get_cached_channel_id()
    channel = slack_bridge.SLACK_CHANNEL

    verify_prompt = f"""Read the last 20 messages from Slack channel {channel} (channel_id: {channel_id}).

Find a message that contains the text "{test_id}".

Check:
1. Does a message with "{test_id}" exist? (found = true/false)
2. Does it look like a digest (contains "Digest" or bullet points)? (is_digest = true/false)
3. Does it have thread replies? (has_thread = true/false)

Write result to {_RESULT_PATH}:
{{
  "test_id": "{test_id}",
  "found": <true/false>,
  "is_digest": <true/false>,
  "has_thread": <true/false>,
  "passed": <true if found AND is_digest>,
  "error": null
}}

ALWAYS write the result file even if earlier steps fail.
"""
    opts = ClaudeAgentOptions(
        model="haiku",
        allowed_tools=[
            "mcp__claude_ai_Slack__slack_read_channel",
            "mcp__claude_ai_Slack__slack_search_channels",
            "Write",
        ],
        permission_mode="bypassPermissions",
        max_turns=8,
        cwd=_VAULT,
        setting_sources=["user"],
    )

    agent_error = None
    try:
        async for msg in query(prompt=verify_prompt, options=opts):
            if isinstance(msg, ResultMessage):
                print(f"[verifier] cost: ${msg.total_cost_usd:.4f}")
    except Exception as e:
        agent_error = str(e)
        print(f"[verifier] error: {e}")

    # ── Read result ────────────────────────────────────────────────────
    if not os.path.isfile(_RESULT_PATH):
        print(f"[test_digest] FAIL — result file not written")
        if agent_error:
            print(f"  agent error: {agent_error}")
        return False

    with open(_RESULT_PATH) as f:
        result = json.load(f)

    passed = result.get("passed", False)
    print(f"  found: {result.get('found')}")
    print(f"  is_digest: {result.get('is_digest')}")
    print(f"  has_thread: {result.get('has_thread')}")
    print(f"  passed: {passed}")
    if result.get("error"):
        print(f"  error: {result['error']}")

    os.unlink(_RESULT_PATH)

    # ── Cleanup fixtures ───────────────────────────────────────────────
    for path in [os.path.join(_VAULT, q_rel), os.path.join(_VAULT, ia_rel)]:
        try:
            os.unlink(path)
        except FileNotFoundError:
            pass
    # Clean up posted state entries
    state2 = slack_bridge._load_state()
    for r in [q_rel, ia_rel]:
        state2.get("posted", {}).pop(r, None)
    slack_bridge._save_state(state2)

    print(f"\n[test_digest] {'PASS' if passed else 'FAIL'}")
    return passed


if __name__ == "__main__":
    ok = asyncio.run(run_test())
    sys.exit(0 if ok else 1)
