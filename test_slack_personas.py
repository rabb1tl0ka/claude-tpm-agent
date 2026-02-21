#!/usr/bin/env python3
"""Integration tests for Slack persona support.

Tests all 4 outbound event types:
1. Run log → main message username = "Delivery Manager", thread exists
2. User question → message username = "Risk Manager"
3. Inter-agent message → message username = "Delivery Manager", mentions Risk Manager
4. Draft for approval → message username = "Comms Manager", contains "APPROVE or REJECT"

Each test:
  create fixture → call bridge function → spawn Haiku to verify Slack → clean up

Usage:
    python3 test_slack_personas.py
    python3 test_slack_personas.py --test run_log
    python3 test_slack_personas.py --test question
    python3 test_slack_personas.py --test inter_agent
    python3 test_slack_personas.py --test draft

Exits 0 if all selected tests pass, 1 if any fail.
"""

import argparse
import asyncio
import json
import os
import sys
import uuid
from datetime import datetime, timezone

import config
import slack_bridge
from claude_agent_sdk import ClaudeAgentOptions, ResultMessage, query

_VAULT_ABS = os.path.abspath(config.VAULT_PATH)
_SLACK_CHANNEL = config.SLACK_CHANNEL
_RESULT_REL = "agent/slack/persona_test_result.json"
_RESULT_PATH = os.path.join(_VAULT_ABS, _RESULT_REL)

# ─── Shared Haiku verifier ───────────────────────────────────────────────────

_VERIFY_TOOLS = [
    "mcp__claude_ai_Slack__slack_search_channels",
    "mcp__claude_ai_Slack__slack_read_channel",
    "Write",
]


async def _verify_slack(test_id: str, expected_username: str, expected_text_fragment: str, has_thread: bool = False) -> bool:
    """Spawn Haiku to read recent channel messages and verify a specific post.

    Writes result to agent/slack/persona_test_result.json.
    Returns True if the expected message was found with correct username.
    """
    channel_block = slack_bridge._channel_id_prompt_block()
    has_thread_instruction = (
        "Also verify that the message has at least one reply (thread_reply_count > 0).\n"
        "Set has_thread = true if so, false otherwise.\n"
        if has_thread else
        "Set has_thread = null (not checked).\n"
    )

    prompt = f"""You are an automated Slack integration tester. Verify a recent message.

{channel_block}

Channel: {_SLACK_CHANNEL}
Test ID: {test_id}
Expected username: {expected_username}
Expected text fragment: {expected_text_fragment}
Result file: {_RESULT_PATH}

Instructions:
1. Resolve the channel ID (see above).
2. Read the last 20 messages from the channel using slack_read_channel.
3. Find a message that:
   a. Contains the text fragment: "{expected_text_fragment}"
   b. Has username = "{expected_username}" (check the username field, not the user field)
4. {has_thread_instruction}
5. Write result to {_RESULT_PATH}:
   {{
     "test_id": "{test_id}",
     "found": <true if matching message found, false otherwise>,
     "username_match": <true if username matches, false otherwise>,
     "has_thread": <true/false/null>,
     "passed": <true if found AND username_match AND (has_thread check passed or not required)>,
     "error": <null or error string>
   }}

IMPORTANT: Always write the result file, even if earlier steps failed.
"""

    options = ClaudeAgentOptions(
        model="haiku",
        allowed_tools=_VERIFY_TOOLS,
        permission_mode="bypassPermissions",
        max_turns=8,
        cwd=_VAULT_ABS,
        setting_sources=["user"],
    )

    try:
        async for message in query(prompt=prompt, options=options):
            if isinstance(message, ResultMessage):
                print(f"  [verifier] Done. Cost: ${message.total_cost_usd:.4f}")
    except Exception as e:
        print(f"  [verifier] Agent error: {e}")
        return False

    if not os.path.isfile(_RESULT_PATH):
        print(f"  [verifier] FAIL — result file not written")
        return False

    with open(_RESULT_PATH) as f:
        result = json.load(f)

    passed = result.get("passed", False)
    print(f"  found: {result.get('found')}, username_match: {result.get('username_match')}, "
          f"has_thread: {result.get('has_thread')}, passed: {passed}")
    if result.get("error"):
        print(f"  error: {result['error']}")

    return passed


# ─── Test 1: Run log ──────────────────────────────────────────────────────────

async def test_run_log() -> bool:
    """Trigger delivery role run log post and verify persona + thread."""
    print("\n[test 1] Run log — Delivery Manager persona + thread")

    test_id = str(uuid.uuid4())[:8]
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # Create fixture log file
    log_dir = os.path.join(_VAULT_ABS, "agent", "logs", "delivery")
    os.makedirs(log_dir, exist_ok=True)
    log_path_rel = f"agent/logs/delivery/persona-test-{today}.md"
    log_full = os.path.join(_VAULT_ABS, log_path_rel)

    log_content = f"""# Delivery Log — {today} (persona test)

## Run 12:00 (manual)

### Inbox
- empty

### What Changed
- persona test fixture

### Priority Action
- verify Slack posts use correct username

### Not Doing
- nothing

### Reflection
Persona test {test_id} — run log reflection text.
"""
    with open(log_full, "w") as f:
        f.write(log_content)

    try:
        role_cfg = config.load_role("delivery")
        cost = 0.0012
        await slack_bridge.post_role_run_log("delivery", role_cfg, cost, log_path_rel)

        passed = await _verify_slack(
            test_id=test_id,
            expected_username="Delivery Manager",
            expected_text_fragment=test_id,
            has_thread=True,
        )
    finally:
        if os.path.isfile(log_full):
            os.unlink(log_full)

    print(f"[test 1] {'PASS' if passed else 'FAIL'}")
    return passed


# ─── Test 2: User question ────────────────────────────────────────────────────

async def test_user_question() -> bool:
    """Post a user question from Risk Manager and verify persona."""
    print("\n[test 2] User question — Risk Manager persona")

    test_id = str(uuid.uuid4())[:8]
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M")

    # Create fixture question file
    question_dir = os.path.join(_VAULT_ABS, "agent", "inbox", "user")
    os.makedirs(question_dir, exist_ok=True)
    fn = f"{now_str}-persona-test-{test_id}.md"
    full = os.path.join(question_dir, fn)
    rel_path = f"agent/inbox/user/{fn}"

    content = f"""---
id: {now_str}-persona-test-{test_id}
from: risk
to: user
date: {datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}
status: open
---

Persona test question {test_id}: Should this risk register entry be escalated?
"""
    with open(full, "w") as f:
        f.write(content)

    # Clear from posted state so it gets picked up
    state = slack_bridge._load_state()
    state.setdefault("posted", {}).pop(rel_path, None)
    slack_bridge._save_state(state)

    try:
        await slack_bridge.post_new_user_questions()

        passed = await _verify_slack(
            test_id=test_id,
            expected_username="Risk Manager",
            expected_text_fragment=test_id,
        )
    finally:
        if os.path.isfile(full):
            os.unlink(full)
        # Clean up posted state entry
        state2 = slack_bridge._load_state()
        state2.get("posted", {}).pop(rel_path, None)
        slack_bridge._save_state(state2)

    print(f"[test 2] {'PASS' if passed else 'FAIL'}")
    return passed


# ─── Test 3: Inter-agent message ──────────────────────────────────────────────

async def test_inter_agent() -> bool:
    """Post an inter-agent message from Delivery to Risk and verify persona + mention."""
    print("\n[test 3] Inter-agent — Delivery Manager → Risk Manager")

    test_id = str(uuid.uuid4())[:8]
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M")

    # Create fixture in risk's inbox from delivery
    inbox_dir = os.path.join(_VAULT_ABS, "agent", "inbox", "risk")
    os.makedirs(inbox_dir, exist_ok=True)
    fn = f"{now_str}-persona-test-{test_id}.md"
    full = os.path.join(inbox_dir, fn)
    rel_path = f"agent/inbox/risk/{fn}"

    content = f"""---
from: delivery
date: {datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}
priority: medium
---

Inter-agent persona test {test_id}: Delivery flagging a new dependency risk for Risk Manager review.
"""
    with open(full, "w") as f:
        f.write(content)

    # Ensure not in posted state
    state = slack_bridge._load_state()
    state.setdefault("posted", {}).pop(rel_path, None)
    slack_bridge._save_state(state)

    try:
        await slack_bridge.post_inter_agent_messages()

        passed = await _verify_slack(
            test_id=test_id,
            expected_username="Delivery Manager",
            expected_text_fragment=test_id,
        )
    finally:
        if os.path.isfile(full):
            os.unlink(full)
        state2 = slack_bridge._load_state()
        state2.get("posted", {}).pop(rel_path, None)
        slack_bridge._save_state(state2)

    print(f"[test 3] {'PASS' if passed else 'FAIL'}")
    return passed


# ─── Test 4: Draft for approval ───────────────────────────────────────────────

async def test_draft() -> bool:
    """Post a Comms Manager draft and verify persona + APPROVE/REJECT prompt."""
    print("\n[test 4] Draft — Comms Manager persona + APPROVE/REJECT")

    test_id = str(uuid.uuid4())[:8]
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M")

    # Create fixture draft file
    drafts_dir = os.path.join(_VAULT_ABS, "agent", "outbox", "comms", "drafts")
    os.makedirs(drafts_dir, exist_ok=True)
    fn = f"{now_str}-persona-test-{test_id}.md"
    full = os.path.join(drafts_dir, fn)
    rel_path = f"agent/outbox/comms/drafts/{fn}"

    content = f"""# Draft: Weekly Status Update

Draft persona test {test_id}.

Team — quick status update:
- All milestones on track
- No blockers this week
"""
    with open(full, "w") as f:
        f.write(content)

    # Ensure not in posted state
    state = slack_bridge._load_state()
    state.setdefault("posted", {}).pop(rel_path, None)
    slack_bridge._save_state(state)

    try:
        await slack_bridge.post_new_drafts()

        passed = await _verify_slack(
            test_id=test_id,
            expected_username="Comms Manager",
            expected_text_fragment=test_id,
        )
    finally:
        if os.path.isfile(full):
            os.unlink(full)
        state2 = slack_bridge._load_state()
        state2.get("posted", {}).pop(rel_path, None)
        slack_bridge._save_state(state2)

    print(f"[test 4] {'PASS' if passed else 'FAIL'}")
    return passed


# ─── Main ─────────────────────────────────────────────────────────────────────

ALL_TESTS = {
    "run_log": test_run_log,
    "question": test_user_question,
    "inter_agent": test_inter_agent,
    "draft": test_draft,
}


async def run_tests(selected: list[str]) -> bool:
    os.makedirs(os.path.join(_VAULT_ABS, "agent", "slack"), exist_ok=True)

    print(f"[test_slack_personas] channel: {_SLACK_CHANNEL}")
    print(f"[test_slack_personas] vault:   {_VAULT_ABS}")
    print(f"[test_slack_personas] tests:   {', '.join(selected)}")

    results = {}
    for name in selected:
        fn = ALL_TESTS[name]
        results[name] = await fn()

    print("\n─── Summary ───────────────────────────────")
    all_passed = True
    for name, passed in results.items():
        status = "PASS" if passed else "FAIL"
        print(f"  {name}: {status}")
        if not passed:
            all_passed = False

    print(f"\n[test_slack_personas] {'ALL PASS' if all_passed else 'SOME FAILED'}")
    return all_passed


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Slack persona integration tests")
    parser.add_argument(
        "--test",
        choices=list(ALL_TESTS.keys()),
        default=None,
        help="Run a specific test (default: all)",
    )
    args = parser.parse_args()

    selected = [args.test] if args.test else list(ALL_TESTS.keys())
    ok = asyncio.run(run_tests(selected))
    sys.exit(0 if ok else 1)
