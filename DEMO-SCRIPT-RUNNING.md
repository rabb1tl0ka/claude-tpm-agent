# Claude TPM Agent - 30-Minute Demo Script (Runner Mode)

**Demo Goals:**
1. Prove multi-role Claude Code agent concept works in practice
2. Show 24/7 tireless support augmenting human TPM capabilities
3. Demonstrate intuitive human-agent partnership & communication flows

**Audience:** Mixed (technical + non-technical)
**Duration:** 30 minutes
**Project Context:** 6-week logistics platform implementation for Peak Logistics

**Demo Mode:** Runner running continuously with 60-second polling

---

## Demo Narrative

Peak Logistics hired Loka for a 6-week project to build a shipment tracking dashboard. The TPM (you, Bruno) is using the Claude TPM Agent to help manage delivery, monitor risks, coordinate communications, and track product requirements. The system runs autonomously, watching for events and scheduled times. At week 5, the client requests additional features. The agent helps analyze options and successfully navigate to on-time delivery.

---

## Pre-Demo Setup Checklist

```bash
cd /home/rabb1tl0ka/loka/code/claude-tpm-agent
./demo-reset.sh
source .venv/bin/activate
python3 runner.py --dry-run  # Should show 4 roles loaded
```

**Terminal layout (3 terminals):**

- **Terminal 1 (Runner):** `python3 runner.py`
- **Terminal 2 (Logs):** `tail -F vaults/peaklogistics/agent/logs/delivery/$(date +%Y-%m-%d).md`
- **Terminal 3 (Working terminal):** For creating trigger files, running commands

> Use `tail -F` (capital F) — waits for the file to be created if it doesn't exist yet.

**Also open `#peaklogistics-agent` in Slack** — run summaries and questions will appear there automatically.

---

## Act 1: System Startup & First Run (5-7 min)

### Step 1.1: Show the System Architecture

**Talk track:**
> "The TPM Agent uses Claude Code's Agent SDK. Unlike traditional automation, each role is actually Claude — the full LLM — with access to project files, specific tools, and a clear mission. The roles operate independently but coordinate via a 'message bus' — which is just markdown files in the vault."

```bash
tree -L 3 vaults/peaklogistics/
```

**Key points:**
- `project/` = source of truth (scope, timeline, team, risks, blockers, decisions, traffic-lights)
- `agent/inbox/{role}/` = trigger mechanism (event-driven runs)
- `agent/outbox/{role}/` = communication pipeline (drafts → approved → sent)
- `agent/logs/{role}/` = reasoning artifacts (THINK/ACT/REFLECT) — one file per day
- `agent/memory/{role}.md` = learned patterns across runs

### Step 1.2: Start the Runner

**Terminal 1:**
```bash
source .venv/bin/activate
python3 runner.py
```

**Talk track:**
> "The runner loaded 4 roles with their schedules. Delivery runs at 9am and 5pm. Risk runs at 10am. Comms checks every 30 minutes. Product is on-demand only. Every minute, it checks for new files in role inboxes. Watch Terminal 1 — you'll see it check inboxes every 60 seconds."

### Step 1.3: Trigger First Run

**Talk track:**
> "Delivery is scheduled for 9am, but let me trigger it now by dropping a file in its inbox. This simulates a human TPM asking Delivery to do an initial assessment."

**Terminal 3:**
```bash
cat > vaults/peaklogistics/agent/inbox/delivery/$(date +%Y-%m-%dT%H-%M)-kickoff.md << 'EOF'
---
from: user
date: 2026-02-17T09:00:00Z
priority: medium
---

This is project kickoff (Day 0). Please review the project scope, timeline, and team, and create your baseline assessment.
EOF
```

**Talk track:**
> "I just dropped a file in Delivery's inbox. The system checks every minute — watch Terminal 1..."

### Step 1.4: Watch the System React

**Wait for Terminal 1:**
```
[...] [delivery] inbox trigger
[...] [delivery] Model: haiku
```

**Point to Terminal 2:**
> "And here's Delivery Manager's reasoning appearing in real-time..."

**Expected log structure:**
```
## Run HH:MM (inbox)

### Inbox
- kickoff.md: Project kickoff baseline assessment request

### What Changed
- First run of the day / project at Day 0

### Priority Action
- Review scope.md, timeline.md, team.md
- Establish baseline

### Not Doing
- No blockers yet

### Reflection
...
```

> "Notice the structure: Inbox, What Changed, Priority Action, Not Doing, Reflection. Every run follows this THINK/ACT/REFLECT cycle. This isn't a script — Claude reasoned through what matters."

**Also check Slack** — a run summary will have been posted to `#peaklogistics-agent`.

### Step 1.5: Show Memory

```bash
cat vaults/peaklogistics/agent/memory/delivery.md
```

> "Memory files accumulate patterns and lessons across runs. This becomes institutional knowledge."

---

## Act 2: Event-Driven Coordination (8-10 min)

### Context
*"Fast forward to week 2. Joao (Backend Lead) reports a blocker: user authentication is more complex than estimated. JWT + RBAC is taking 2x longer. Let's see how the roles coordinate autonomously."*

### Step 2.1: Create Blocker Trigger

**Terminal 3:**
```bash
cat > vaults/peaklogistics/agent/inbox/risk/$(date +%Y-%m-%dT%H-%M)-blocker-auth.md << 'EOF'
---
from: user
date: 2026-02-24T14:30:00Z
priority: high
---

**Blocker identified:**

Joao (Backend Lead) reports that the user authentication implementation is more complex than estimated. JWT token management, session handling, and role-based access control (supplier vs shipper) is taking 2x longer than estimated.

Originally: 2 days (per scope.md)
Now: likely 4 days

**Impact:**
- Timeline: Pushes Week 2 milestone "User sign-up/login working" by 2 days
- Dependencies: Blocks all user-specific features (posting shipments/trips)
- Critical path: Authentication is a prerequisite for everything else

**Request:**
Assess this as a risk and recommend mitigation.
EOF
```

> "I just dropped this blocker in Risk Manager's inbox. The system will detect it within the next minute... watch Terminal 1..."

### Step 2.2: Watch Risk Manager React

**Wait for Terminal 1:**
```
[...] [risk] inbox trigger
```

> "There — Risk Manager detected the blocker and is analyzing it..."

**Expected reasoning:**
- Creates a risk file in `project/risks/`
- Creates a blocker file in `project/blockers/`
- Assesses impact, proposes mitigation
- Writes a trigger to Delivery's inbox

### Step 2.3: Verify Risk's Actions

```bash
ls vaults/peaklogistics/project/risks/
ls vaults/peaklogistics/project/blockers/
ls vaults/peaklogistics/agent/inbox/delivery/
```

> "Risk updated the project context and notified Delivery. The system will pick that up in the next check..."

### Step 2.4: Watch Delivery React

**Wait for Terminal 1:**
```
[...] [delivery] inbox trigger
```

> "Delivery Manager just received Risk's notification and is assessing the timeline impact..."

**Expected reasoning:**
- Confirms Week 6 buffer absorbs 2-day slip
- Updates timeline
- Decides not to escalate yet

> "Delivery and Risk coordinated asynchronously — no manual intervention. This is the event-driven architecture in action."

---

## Act 3: Week 5 Crisis — Client Requests More Features (10-12 min)

### Context
*"Week 5. On track. Then the client sends an email: 'We'd love to add real-time shipment notifications before launch.' Classic scope creep."*

### Step 3.1: Create Client Request Trigger

**Terminal 3:**
```bash
cat > vaults/peaklogistics/agent/inbox/comms/$(date +%Y-%m-%dT%H-%M)-client-request.md << 'EOF'
---
from: user
date: 2026-03-17T15:00:00Z
priority: high
---

**Client email received:**

From: Sarah Chen (Peak Logistics CTO)
Subject: Feature request - Real-time notifications

Hi Bruno,

The team is really excited about the dashboard! We've been thinking - would it be possible to add **real-time SMS/email notifications** when shipments reach key milestones (picked up, in transit, delivered)?

We know we're at week 5, but this would be a game-changer for our customers. Let me know if this is feasible before the Feb 28 deadline.

Thanks!
Sarah

**Request:**
Coordinate with Delivery and Risk to assess feasibility and provide options.
EOF
```

> "Client wants real-time notifications at week 5. Classic. Watch the system cascade..."

### Step 3.2: Watch the Cascade

**Comms runs first**, then triggers Delivery and Risk:

```
[...] [comms] inbox trigger
[...] [delivery] inbox trigger
[...] [risk] inbox trigger
```

> "Comms recognized this needs cross-role analysis. It triggered both Delivery and Risk — watch them run one after another."

### Step 3.3: Check for Questions

```bash
ls vaults/peaklogistics/agent/inbox/user/
```

```bash
# Show the question (filename will vary — use the actual filename from ls above)
cat vaults/peaklogistics/agent/inbox/user/<actual-filename>.md
```

> "Delivery analyzed this, realized it's a strategic call, and asked ME — the human TPM. It's not trying to make this decision alone. This is the human-in-the-loop design."

### Step 3.4: Answer the Question

```bash
# Find the question filename
QUESTION=$(ls -t vaults/peaklogistics/agent/inbox/user/*.md | head -1)
QNAME=$(basename "$QUESTION")

# Read the from: field to get the role
FROM=$(grep "^from:" "$QUESTION" | head -1 | awk '{print $2}')

# Write your answer to answered/
cat > "vaults/peaklogistics/agent/inbox/user/answered/$QNAME" << EOF
$(cat "$QUESTION" | sed 's/^status: open/status: answered/')

---

**Bruno's Answer:**

Option B with a twist: **phased approach**

**Phase 1 (by deadline):** SMS notifications only (simpler, faster — 3 days)
**Phase 2 (week after launch):** Email notifications + rich templates

Descope "advanced filtering" (nice-to-have) to make room. This gives the client most of the value, shows we're responsive, and protects the deadline.

Draft an options memo with timeline and trade-offs. I'll review before we send.
EOF

# Remove from open inbox
rm "$QUESTION"
```

> "I've made the call: phased approach. The system will route this answer back to Delivery on the next check..."

### Step 3.5: Watch Delivery Execute

**Wait for next check (up to 60 seconds):**
```
[...] [delivery] inbox trigger
```

> "Delivery received my answer and is drafting the options memo..."

### Step 3.6: Review and Approve Draft

```bash
ls vaults/peaklogistics/agent/outbox/delivery/drafts/
cat vaults/peaklogistics/agent/outbox/delivery/drafts/$(ls -t vaults/peaklogistics/agent/outbox/delivery/drafts/ | head -1)
```

> "Beautiful. Delivery drafted a professional options memo based on my guidance. Now I approve it:"

```bash
DRAFT=$(ls -t vaults/peaklogistics/agent/outbox/delivery/drafts/ | head -1)
mv "vaults/peaklogistics/agent/outbox/delivery/drafts/$DRAFT" \
   "vaults/peaklogistics/agent/outbox/delivery/approved/$DRAFT"
```

> "The full human-agent loop:
> 1. External event enters the system
> 2. Roles coordinate asynchronously
> 3. Agent asks User for the strategic call
> 4. User decides
> 5. Agent executes and drafts
> 6. User reviews and approves
>
> Agent did the analysis and drafting. I made the strategic decision. Perfect partnership."

---

## Act 4: System Features Showcase (3-5 min)

### Step 4.1: Daily Log — One File Per Role Per Day

```bash
cat vaults/peaklogistics/agent/logs/delivery/$(date +%Y-%m-%d).md
```

> "One log file per day, all runs appended. Trivial to review what a role did today. `tail -F` shows reasoning in real-time as it runs."

### Step 4.2: Memory Accumulation

```bash
cat vaults/peaklogistics/agent/memory/delivery.md
cat vaults/peaklogistics/agent/memory/risk.md
```

> "Each role accumulates patterns and lessons. If I consistently prefer phased approaches, Delivery learns this and proposes it proactively."

### Step 4.3: Session Management

```bash
cat .sessions/sessions.json
```

> "Same-day runs resume the same Claude conversation — it remembers everything from earlier today. Tomorrow it starts fresh with updated context."

### Step 4.4: Slack Integration

**Point to `#peaklogistics-agent`:**
> "Every role run posts its full reasoning log to Slack. Questions from roles appear as top-level messages. You can trigger a role by posting `run delivery` in the channel. The vault is still the source of truth — Slack is just the surface."

### Step 4.5: The Full Artifact Tree

```bash
tree vaults/peaklogistics/agent/
```

> "This runner has been running the whole demo — 24/7 in production. Checks schedules every minute, polls inboxes, compiles daily summaries. I just monitor outputs, answer questions, and make strategic calls."

```
Ctrl+C
```

---

## Wrap-Up (2-3 min)

**For non-technical audience:**
> "Think of this as a tireless project coordinator who monitors project health 24/7, coordinates between concerns, drafts documents for your review, asks smart questions when it needs input, and reacts to events within minutes. You stay in control of all strategic decisions and external communications. The agent amplifies your effectiveness."

**For technical audience:**
> "This is Claude Code as infrastructure. Each role is a full Claude LLM with role-specific system prompts, access to project files, structured reasoning logs, persistent memory, session management, and event-driven + scheduled execution. It's not RPA, not scripting — it's autonomous reasoning with human oversight. The Agent SDK makes this trivial to set up and extend."

### What We Demonstrated

✅ **Autonomous event-driven system** — Roles react to inbox triggers within 60 seconds
✅ **Multi-role coordination** — Risk → Delivery cascade without manual intervention
✅ **Human-in-the-loop** — Agent asks questions, drafts comms, waits for approval
✅ **Scheduled + reactive** — Runs at scheduled times AND reacts to events
✅ **Visible reasoning** — Real-time logs show agent thinking
✅ **Memory & learning** — Accumulates patterns and preferences across runs
✅ **Slack integration** — Run summaries, questions, and commands via `#peaklogistics-agent`

---

## Fallback: If Runner Breaks Mid-Demo

```bash
# Ctrl+C to stop, then:
tail logs/$(ls -t logs/ | head -1)   # Check what went wrong
python3 runner.py                      # Restart — picks up from file state

# Or run roles manually (bypass scheduler):
python3 runner.py --role delivery
python3 runner.py --role risk
```

---

## Common Q&A

**"What if the agent makes a mistake?"**
All external comms go through drafts → approval. Context updates are logged. The agent never takes destructive actions without confirmation.

**"The 60-second wait seems slow."**
Change `time.sleep(60)` to `time.sleep(5)` for 5-second checks, or implement file watching for sub-second reaction. For TPM work 60s is fine.

**"How much does this cost?"**
A role run costs ~$0.05–0.50 depending on model and context. 4 roles × 2x/day ≈ $1–4/day. Compare to TPM hourly rate.

**"Can I customize the roles?"**
Role configs are markdown files in `roles/`. Change mission, goals, tools, schedule — all plaintext. Add new roles by creating a new `.md` file.

**"Does this work for non-software projects?"**
Yes. The roles are domain-agnostic. Customize `project/` files for construction, marketing campaigns, event planning — any project with deliverables and stakeholders.
