---
date: 2026-02-14
type: thinking
author: Claude
---

# Claude Code as the Agent Engine

## The Question

Can we use Claude Code itself as the execution engine for the TPM AI Agent instead of calling the Anthropic API directly?

## Why This Matters

1. **No API key management** — Claude Code handles auth via subscription
2. **Model routing per role** — different models for different roles (Haiku for simple, Sonnet for complex)
3. **Built-in tools** — Claude Code already has Read, Write, Edit, Bash, Glob, Grep
4. **MCP integration** — Slack, Notion, and other tools are already available via MCP
5. **No API budget concerns** — runs on Claude Code subscription, not per-token API billing

## Two Approaches Analyzed

### Option A: ClaudeCodeProvider (fit Claude Code into current architecture)

Wrap `claude -p --model X` as a provider inside the existing agent.py architecture.

**How it would work:**
- `ClaudeCodeProvider.chat()` calls `claude -p` via subprocess
- Tool definitions embedded in the prompt as instructions
- Model asked to output JSON tool calls
- agent.py parses the JSON and executes through tools.dispatch()

**Problems:**
- `claude -p` (print mode) is text-only — no native tool calling
- Simulating tool_use via prompt engineering is fragile (malformed JSON, hallucinated tool names)
- Square peg, round hole — wrapping a full AI agent behind a completion API interface
- We'd be degrading a first-class capability (Claude Code's tool system) to fit our abstraction

**Verdict: Not recommended.** The abstraction doesn't fit.

### Option B: Claude Code IS the Agent (recommended)

Skip the provider abstraction entirely. The runner spawns Claude Code for each role run, and Claude Code handles everything natively.

**How it would work:**
- runner.py decides which role to run (schedule + inbox triggers)
- For each role, runner.py spawns Claude Code with the role's system prompt
- Claude Code uses its own tools (Read/Write for vault, Slack MCP for comms)
- runner.py captures output for logging/audit

**Architecture change:**
```
CURRENT (API-based):
    runner.py → agent.py → provider.py → Anthropic API
                              ↕
                          tools.py (vault + Slack)

PROPOSED (Claude Code-based):
    runner.py → Claude Code SDK
                    ↕
                Built-in tools (Read/Write/Bash)
                MCP tools (Slack, Notion)
```

**What we gain:**
- No API key needed
- Model routing per role (haiku for simple, sonnet for complex)
- Claude Code's tools are better than ours (edge case handling, sandboxed Bash)
- Dramatically less code to maintain (no agent.py, no provider.py, no tools.py)
- MCP tools give us Slack, Notion, and more out of the box

**What we lose:**
- Vault safety boundary — our tools.py enforces `_resolve()` preventing directory traversal. Claude Code can access any file. Mitigation: system prompt instructions + `--cwd` flag
- Structured tool call logging — our agent loop logs every call. Mitigation: Claude Code's `--output-format json` and SDK message streaming
- Multi-provider flexibility — ties us to Claude Code. But for the POC this is fine; the current repo keeps the API-based approach

**Verdict: Recommended for a new repo.** This is a fundamentally simpler architecture.

## How to Run Claude Code in Full Agent Mode from Python

### The Agent SDK (recommended approach)

There is a proper Python SDK: `pip install claude-agent-sdk`

This runs Claude Code **in-process** — no subprocess needed. Full tool support, full control.

```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions

async def run_role(role_prompt: str, context: str, model: str = "sonnet"):
    options = ClaudeAgentOptions(
        model=model,
        system_prompt=role_prompt,
        allowed_tools=["Read", "Write", "Edit", "Bash", "Glob", "Grep"],
        permission_mode="acceptEdits",
        max_turns=10,
        cwd="/path/to/vault",
    )

    async for message in query(prompt=context, options=options):
        if hasattr(message, "result"):
            return message.result

result = asyncio.run(run_role(
    role_prompt="You are the Delivery Manager...",
    context="Current project state: ...",
    model="haiku",
))
```

### Key SDK Options

| Option | Purpose | Example |
|--------|---------|---------|
| `model` | Model selection | `"opus"`, `"sonnet"`, `"haiku"` |
| `system_prompt` | Role prompt | `"You are the Risk Manager..."` |
| `allowed_tools` | Auto-approve these tools | `["Read", "Write", "Bash"]` |
| `permission_mode` | Permission behavior | `"acceptEdits"`, `"bypassPermissions"` |
| `max_turns` | Safety cap | `10` |
| `max_budget_usd` | Cost cap per run | `5.00` |
| `cwd` | Working directory | Path to vault |
| `mcp_servers` | MCP server configs | Slack, Notion, etc. |
| `output_format` | Structured output | `{"type": "json_schema", "schema": {...}}` |

### CLI Alternative (simpler, less control)

For subprocess-based approach:

```bash
claude -p "context here" \
  --model haiku \
  --system-prompt "You are the Delivery Manager..." \
  --allowedTools "Read,Write,Bash" \
  --max-turns 10 \
  --output-format json \
  --cwd /path/to/vault
```

From Python:
```python
import subprocess, json

result = subprocess.run(
    ["claude", "-p", context,
     "--model", "haiku",
     "--system-prompt", role_prompt,
     "--allowedTools", "Read,Write,Bash",
     "--max-turns", "10",
     "--output-format", "json",
     "--cwd", vault_path],
    capture_output=True, text=True,
)
output = json.loads(result.stdout)
```

### Custom Tools via SDK

We can define our OWN tools (vault-safe wrappers) as MCP tools and inject them:

```python
from claude_agent_sdk import tool, create_sdk_mcp_server

@tool("vault_read", "Read a file from the project vault", {"path": str})
async def vault_read(args):
    # Our vault-safe read logic here
    safe_path = resolve_vault_path(args["path"])
    content = open(safe_path).read()
    return {"content": [{"type": "text", "text": content}]}

vault_server = create_sdk_mcp_server(name="vault", tools=[vault_read, vault_write, ...])

options = ClaudeAgentOptions(
    mcp_servers={"vault": vault_server},
    allowed_tools=["mcp__vault__vault_read", "mcp__vault__vault_write"],
)
```

This means we CAN have vault safety boundaries even with Claude Code — by defining custom MCP tools that enforce the `_resolve()` path check, and only allowing those tools (not the built-in Read/Write).

## Architecture for the New Repo (Claude-TPM-Agent)

```
Claude-TPM-Agent/
├── runner.py          # Schedule + inbox watching (same as current)
├── roles/             # Role configs as .md (same as current)
│   ├── delivery.md
│   ├── risk.md
│   ├── comms.md
│   └── product.md
├── vault_tools.py     # Custom MCP tools with vault safety (optional)
├── config.py          # Minimal: vault path, role loading
└── vaults/            # Project vaults
```

Key simplification: **no agent.py, no provider.py, no tools.py**. Claude Code replaces all three.

The runner.py becomes:
```python
async def run_role(role_name: str):
    role_cfg = config.load_role(role_name)
    context = build_role_context(role_cfg)

    options = ClaudeAgentOptions(
        model=role_cfg.get("model", "sonnet"),
        system_prompt=build_role_prompt(role_cfg),
        allowed_tools=role_cfg["tools"],  # Now Claude Code tool names
        permission_mode="acceptEdits",
        max_turns=10,
        cwd=config.VAULT_PATH,
    )

    async for message in query(prompt=context, options=options):
        if hasattr(message, "result"):
            log.info(f"[{role_name}] Complete: {message.result[:200]}")
```

## Model Routing Per Role

Add `## Model` section to each role .md:

```markdown
## Model
haiku
```

Role-to-model mapping (starting point):
| Role | Model | Reasoning |
|------|-------|-----------|
| Communication Manager | haiku | Routine: read messages, draft updates, send approved comms |
| Delivery Manager | sonnet | Moderate: analyze timeline, identify blockers, recommend adjustments |
| Risk Manager | sonnet | Moderate: assess risks, create mitigation plans |
| Product Manager | sonnet | Moderate: scope analysis, priority alignment |

Can be tuned based on real output quality.

## Decision

- **This repo (tpm-ai-agent)**: Keep as-is with API-based provider architecture
- **New repo (Claude-TPM-Agent)**: Build Option B using Claude Code Agent SDK
- Both repos share the same vault structure, role configs, and inbox pattern
- The new repo is a clean reimplementation, not a port

## Open Questions

1. **MCP tool configuration** — Do we pass Bruno's existing MCP config (Slack, Notion) to the SDK? Or define them inline in runner.py?
2. **Vault safety** — Use built-in Read/Write with `--cwd` + prompt instructions? Or define custom vault MCP tools with path enforcement?
3. **Cost tracking** — The SDK provides `total_cost_usd` per run. Should we log/cap this per role?
4. **Session persistence** — Should role runs persist sessions (resume context from last run) or start fresh each time?

## Resolved Decisions

### 1. MCP tool configuration — use existing Claude Code plugins

Bruno asked: "where did you find the MCP config? I thought those existed per vault."

Clarification: MCP configs in Claude Code are NOT per vault — they're installed as **user-level plugins** at `~/.claude/plugins/`. Bruno's Slack MCP is at:
```
~/.claude/plugins/.../external_plugins/slack/.mcp.json
→ {"slack": {"type": "sse", "url": "https://mcp.slack.com/sse"}}
```

When using the Agent SDK, we set `setting_sources=["user"]` and the SDK automatically picks up all installed plugins (Slack, Notion, etc.). No need to pass MCP configs manually — the SDK inherits what Claude Code already has.

If we use the CLI approach, same thing — `claude` already has access to the user's plugins.

**Decision: inherit existing plugins via `setting_sources=["user"]`. No manual MCP config needed.**

### 2. Vault safety — built-in Read/Write with `--cwd`

Use Claude Code's built-in tools + `cwd` pointed at the vault. The system prompt instructs the agent to stay within the vault. Good enough for POC.

### 3. Cost tracking — handle token exhaustion, no cap

Bruno's subscription covers costs. No `max_budget_usd` needed. Instead:
- Catch token exhaustion errors (rate limit / quota exceeded)
- Implement backoff: wait and retry, or skip the role run and try next scheduled time
- Log when runs are skipped due to exhaustion so Bruno has visibility

### 4. Session persistence — resume same day, fresh next day

- Within the same day: use `--resume` / `resume=session_id` to maintain context across role runs
- New day: start fresh session (no stale context from yesterday)
- runner.py tracks session IDs per role per day (simple dict or small file)
- This means morning runs start with clean reasoning, afternoon runs build on morning context
