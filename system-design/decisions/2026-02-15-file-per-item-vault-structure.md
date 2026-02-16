---
date: 2026-02-15
type: decision
status: Accepted
author: Claude
---

# Decision: File-Per-Item Vault Structure

## Context

The vault uses monolithic files (`context/blockers.md`, `context/decisions.md`, `project/risks.md`) where agents edit *inside* files to add, update, or archive items. This creates several problems:

1. **Fragile edits** — Agents must parse file structure to insert/remove items. Off-by-one Markdown heading levels, broken separators, and accidental overwrites are common failure modes.
2. **Inconsistent patterns** — The agent inbox/outbox already uses file-per-item (one `.md` per trigger, one per draft). Tracked items like blockers and decisions use a different pattern, forcing agents to switch between two mental models.
3. **No atomic operations** — Adding a blocker means editing a shared file. Two roles editing the same file in the same cycle risks conflicts. Creating a new file is atomic and conflict-free.
4. **Archive friction** — Resolving a blocker means editing it in-place (changing status, moving text within the file). With file-per-item, archiving is just `mv blocker.md archive/`.

## Decision

Convert monolithic tracking files to directories where each item is an individual `.md` file:

| Before | After |
|--------|-------|
| `context/blockers.md` | `project/blockers/` (one file per blocker) |
| `context/decisions.md` | `project/decisions/` (one file per decision) |
| `context/updates.md` | `project/traffic-lights/` (one file per TLU) |
| `project/risks.md` | `project/risks/` (one file per risk) |

Also consolidate scattered top-level directories under `project/`:
- `goals/` → `project/goals/`
- `challenges/` → `project/challenges/`
- `traffic-lights/` → `project/traffic-lights/`

The `context/` directory is eliminated entirely. Everything project-related lives under `project/`.

## Consequences

**Easier:**
- Create/archive operations become atomic file operations (write, move)
- Agents use the same file-per-item pattern everywhere (inbox, outbox, blockers, decisions, risks)
- Glob patterns like `project/blockers/*.md` make it trivial to list/count items
- Runner's `load_role_context()` reads directories by concatenating all `.md` files inside
- Less risk of agents corrupting shared files

**Harder:**
- Slightly more files to manage (4 files → 4 directories with N files each)
- Viewing "all decisions" requires reading multiple files instead of one (mitigated by directory listing)

## Alternatives Considered

1. **Keep monolithic files, improve edit instructions** — Rejected. The root cause is structural: editing inside files is inherently fragile for AI agents. Better prompts don't fix the fundamental problem.
2. **Use YAML/JSON instead of Markdown** — Rejected. Contradicts vault-first philosophy. Markdown files are human-readable and editable in any tool.
3. **Only convert blockers (most-edited file)** — Rejected. Inconsistency is worse than the migration cost. Convert everything at once for a clean, uniform pattern.
