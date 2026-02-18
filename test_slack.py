#!/usr/bin/env python3
"""Autonomous Slack integration test.

Spawns a single Haiku agent that:
1. Posts a timestamped test message to SLACK_CHANNEL
2. Reads back the last 10 messages from the channel
3. Verifies the test message appears in the results
4. Writes result to agent/slack/test_result.json

Usage:
    python3 test_slack.py
    SLACK_CHANNEL="#other-channel" python3 test_slack.py

Exits 0 on pass, 1 on fail.
"""

import asyncio
import json
import os
import sys
import uuid
from datetime import datetime, timezone

import config
from claude_agent_sdk import ClaudeAgentOptions, ResultMessage, query


SLACK_CHANNEL = os.environ.get("SLACK_CHANNEL", config.SLACK_CHANNEL)
_VAULT_ABS = os.path.abspath(config.VAULT_PATH)
_RESULT_REL = "agent/slack/test_result.json"
_RESULT_PATH = os.path.join(_VAULT_ABS, _RESULT_REL)


async def run_test() -> bool:
    test_id = str(uuid.uuid4())[:8]
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    print(f"[test_slack] test_id: {test_id}")
    print(f"[test_slack] channel: {SLACK_CHANNEL}")
    print(f"[test_slack] vault:   {_VAULT_ABS}")

    # Ensure directory exists
    os.makedirs(os.path.join(_VAULT_ABS, "agent", "slack"), exist_ok=True)

    result_abs = os.path.join(_VAULT_ABS, _RESULT_REL)

    result_abs = os.path.join(_VAULT_ABS, _RESULT_REL)
    channel_name = SLACK_CHANNEL.lstrip("#")  # strip leading # for search

    prompt = f"""You are an automated Slack integration tester. Complete all steps in order.

Test ID: {test_id}
Channel name: {SLACK_CHANNEL}
Result file (absolute path): {result_abs}

STEP 1: Find the channel ID.
  Use slack_search_channels with query="{channel_name}" to find the channel.
  Extract the channel_id (looks like C0XXXXXXXX) from the result.
  If not found, note the error and skip to STEP 4.

STEP 2: Send this exact message to the channel_id from step 1 using slack_send_message:
  "TPM test [{test_id}] — ignore"
  Save the ts value from the response (looks like "1708252500.123456"). Call it posted_ts.
  If sending fails, set posted_ts to "error".

STEP 3: Read the channel using slack_read_channel with the channel_id from step 1 (limit=10).
  Check if the text "{test_id}" appears anywhere in the messages.
  found_in_read = true if found, false otherwise.

STEP 4: Write the result file to this exact path: {result_abs}
  Use the Write tool. The file must be valid JSON:
  {{
    "test_id": "{test_id}",
    "posted_ts": "<ts from step 2, or 'error'>",
    "found_in_read": <true or false>,
    "passed": <same as found_in_read>,
    "error": <null, or error string if something failed>
  }}

IMPORTANT: ALWAYS write the result file in step 4, even if earlier steps failed.
"""

    options = ClaudeAgentOptions(
        model="haiku",
        allowed_tools=[
            "mcp__claude_ai_Slack__slack_search_channels",
            "mcp__claude_ai_Slack__slack_send_message",
            "mcp__claude_ai_Slack__slack_read_channel",
            "Write",
        ],
        permission_mode="bypassPermissions",
        max_turns=10,
        cwd=_VAULT_ABS,
        setting_sources=["user"],
    )

    agent_error = None
    try:
        async for message in query(prompt=prompt, options=options):
            if isinstance(message, ResultMessage):
                print(f"[test_slack] Agent done. Cost: ${message.total_cost_usd:.4f}")
    except Exception as e:
        agent_error = str(e)
        print(f"[test_slack] Agent error: {e}")

    # Read result file
    if not os.path.isfile(_RESULT_PATH):
        print(f"[test_slack] FAIL — result file not written: {_RESULT_PATH}")
        if agent_error:
            print(f"[test_slack] Agent error was: {agent_error}")
        return False

    with open(_RESULT_PATH) as f:
        result = json.load(f)

    passed = result.get("passed", False)
    found = result.get("found_in_read", False)
    posted_ts = result.get("posted_ts", "unknown")
    error = result.get("error")

    print()
    print(f"  test_id:      {result.get('test_id')}")
    print(f"  posted_ts:    {posted_ts}")
    print(f"  found_in_read:{found}")
    print(f"  passed:       {passed}")
    if error:
        print(f"  error:        {error}")
    print()

    if passed:
        print("[test_slack] PASS")
    else:
        print("[test_slack] FAIL")

    return passed


if __name__ == "__main__":
    ok = asyncio.run(run_test())
    sys.exit(0 if ok else 1)
