# Claude TPM Agent - 30-Minute Demo Script

**Demo Goals:**
1. Prove multi-role Claude Code agent concept works in practice
2. Show 24/7 tireless support augmenting human TPM capabilities
3. Demonstrate intuitive human-agent partnership & communication flows

**Audience:** Mixed (technical + non-technical)
**Duration:** 30 minutes
**Project Context:** 6-week logistics platform implementation for Peak Logistics

---

## Demo Narrative

Peak Logistics hired Loka for a 6-week project to build a shipment tracking dashboard. The TPM (you, Bruno) is using the Claude TPM Agent to help manage delivery, monitor risks, coordinate communications, and track product requirements. At week 5, the client requests additional features. The agent helps analyze options and successfully navigate to on-time delivery.

---

## Pre-Demo Setup Checklist

**Verify system is ready:**
```bash
cd /home/rabb1tl0ka/loka/code/claude-tpm-agent
python3 runner.py --dry-run  # Should show 4 roles loaded
ls vaults/peaklogistics/project/  # Should show scope.md, timeline.md, etc.
```

**Clean slate for demo:**
```bash
# Clear any existing logs/sessions from previous runs
rm -rf vaults/peaklogistics/agent/logs/delivery/*
rm -rf vaults/peaklogistics/agent/logs/risk/*
rm -rf vaults/peaklogistics/agent/logs/comms/*
rm -rf vaults/peaklogistics/agent/memory/*.md
rm -f sessions/sessions.json

# Ensure inboxes are empty
rm -f vaults/peaklogistics/agent/inbox/delivery/*
rm -f vaults/peaklogistics/agent/inbox/risk/*
rm -f vaults/peaklogistics/agent/inbox/comms/*
rm -f vaults/peaklogistics/agent/inbox/user/*
```

**Have these windows open:**
1. Terminal for running commands
2. File browser showing `vaults/peaklogistics/agent/` structure
3. Text editor ready to create trigger files

**Optional: Live log viewing (advanced demo)**
Open 3 additional terminals with tail to watch reasoning in real-time:
```bash
# Terminal for Delivery logs
tail -f vaults/peaklogistics/agent/logs/delivery/$(date +%Y-%m-%d).md

# Terminal for Risk logs
tail -f vaults/peaklogistics/agent/logs/risk/$(date +%Y-%m-%d).md

# Terminal for Comms logs
tail -f vaults/peaklogistics/agent/logs/comms/$(date +%Y-%m-%d).md
```

As roles run, their reasoning appears live in their windows. Very visual for technical audiences.

---

## Act 1: Project Setup & First Run (5-7 min)

### Context for Audience
*"We're at project kickoff. The vault already has project scope, timeline, team info, and initial risk register. This is day 1. Let's see what happens when we run the Delivery Manager role for the first time."*

### Step 1.1: Show the System Architecture

**Talk track:**
> "The TPM Agent uses Claude Code's Agent SDK. Unlike traditional automation, each role is actually Claude - the full LLM - with access to project files, specific tools, and a clear mission. The roles operate independently but coordinate via a 'message bus' - which is just markdown files in the vault."

**Show vault structure:**
```bash
tree -L 3 vaults/peaklogistics/
```

**Key points to narrate:**
- `project/` = source of truth (scope, timeline, team, risks, blockers, decisions, goals, traffic-lights)
- `agent/inbox/{role}/` = trigger mechanism (event-driven runs)
- `agent/outbox/{role}/` = communication pipeline (drafts → approved → sent)
- `agent/logs/{role}/` = reasoning artifacts (THINK/ACT/REFLECT)
- `agent/memory/{role}.md` = learned patterns across runs

### Step 1.2: Run Delivery Manager (First Run)

**Command:**
```bash
python3 runner.py --role delivery
```

**What's happening (narrate while it runs):**
> "Claude is reading the system prompt that defines the Delivery Manager role. It's loading all context files: scope, timeline, team, blockers, updates. It's checking its inbox - which is empty. Now it's writing a reasoning log to agent/logs/delivery/ following the THINK/ACT/REFLECT pattern. Watch the terminal..."

**Expected output:**
- Log file created/appended: `agent/logs/delivery/YYYY-MM-DD.md`
- Terminal shows preview of Claude's reasoning
- Session ID saved for same-day resumption

**Show the reasoning log:**
```bash
cat vaults/peaklogistics/agent/logs/delivery/$(date +%Y-%m-%d).md
```

**Key points in the log:**
- **Run section header:** `## Run 09:00 (manual)`
- **Inbox subsection:** "(empty)"
- **What Changed:** "First run - establishing baseline"
- **Priority Action:** Likely reviewing timeline, checking for immediate concerns
- **Not Doing:** Deferred items
- **Reflection:** Self-assessment of the run

**Talk track:**
> "Notice how Claude structures its thinking. This isn't a black box - every decision is visible. The Delivery Manager read the timeline, saw we're at week 0, confirmed milestones are clear, and established baseline awareness. No actions needed yet because the project just started."

### Step 1.3: Show Memory Initialization

**Check if memory file was created:**
```bash
cat vaults/peaklogistics/agent/memory/delivery.md
```

**Talk track:**
> "The role can update its memory file to accumulate lessons across runs. Think of it as institutional knowledge that persists beyond individual sessions."

---

## Act 2: Normal Operations - Role Coordination (5-7 min)

### Context for Audience
*"Fast forward to week 2. Joao (Backend Lead) reports a blocker: the user authentication implementation is more complex than estimated. JWT token management and role-based access control is taking longer than expected. Let's see how the roles coordinate."*

### Step 2.1: Simulate Blocker Discovery (Manual Trigger to Risk)

**Create trigger file:**
```bash
cat > vaults/peaklogistics/agent/inbox/risk/2026-02-14T14-30-blocker-auth.md << 'EOF'
---
from: user
date: 2026-02-14T14:30:00Z
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

**Show the file:**
```bash
cat vaults/peaklogistics/agent/inbox/risk/2026-02-14T14-30-blocker-auth.md
```

**Talk track:**
> "I just dropped a trigger file in the Risk Manager's inbox. This is how events enter the system. In production, this could come from automated monitoring, Slack webhooks, CI/CD failures, or manual input like this."

### Step 2.2: Run Risk Manager (Inbox-Triggered)

**Command:**
```bash
python3 runner.py --role risk
```

**What's happening:**
> "Risk Manager wakes up, checks inbox, sees the blocker. It reads the project context, assesses severity, creates a mitigation plan, and likely notifies the Delivery Manager."

**Expected behavior:**
- Reads the trigger file
- Creates/updates risk file in `project/risks/`
- Creates blocker file in `project/blockers/`
- Writes reasoning log to `agent/logs/risk/`
- **Likely creates trigger file** in `agent/inbox/delivery/`
- Moves processed trigger to `agent/inbox/risk/archive/`

**Show the Risk log:**
```bash
cat vaults/peaklogistics/agent/logs/risk/$(date +%Y-%m-%d).md
```

**Check if Risk updated project files:**
```bash
ls vaults/peaklogistics/project/risks/
ls vaults/peaklogistics/project/blockers/
```

**Check if Risk notified Delivery:**
```bash
ls vaults/peaklogistics/agent/inbox/delivery/
```

**Talk track:**
> "See what happened? Risk Manager assessed this as medium-high severity, documented it in the risk register, added mitigation steps, and notified Delivery. All without me needing to manually coordinate. The roles are async but coordinated - like a distributed team."

### Step 2.3: Run Delivery Manager (React to Risk Notification)

**Command:**
```bash
python3 runner.py --role delivery
```

**Expected behavior:**
- Reads Risk's trigger from inbox
- Updates `project/timeline.md` to reflect 2-day slip in Week 2 milestone
- Logs reasoning about whether this threatens overall delivery (Week 6 buffer can absorb)
- Moves trigger to archive

**Show Delivery's log:**
```bash
cat vaults/peaklogistics/agent/logs/delivery/$(date +%Y-%m-%d).md
```

**Show updated timeline:**
```bash
cat vaults/peaklogistics/project/timeline.md
```

**Talk track:**
> "Delivery Manager received the notification, assessed impact on overall timeline, updated the Week 2 milestone, and determined this is manageable - we have Week 6 buffer to absorb the slip. If the overall timeline was at risk, it would draft a communication to stakeholders or ask me for guidance. This is the 24/7 awareness I mentioned - these roles are constantly monitoring and coordinating."

---

## Act 3: Week 5 Crisis - Client Requests More Features (8-10 min)

### Context for Audience
*"Now we're at week 5. We're on track. Then the client sends an email: 'We'd love to add real-time shipment notifications before launch.' Classic scope creep. Let's see how the agent helps me navigate this."*

### Step 3.1: Simulate Client Request (Trigger to Comms)

**Create trigger file:**
```bash
cat > vaults/peaklogistics/agent/inbox/comms/2026-02-14T15-00-client-request.md << 'EOF'
---
from: user
date: 2026-02-14T15:00:00Z
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

**Talk track:**
> "Classic scenario. Excited client, reasonable request, terrible timing. As the TPM, I need to: analyze timeline impact, assess risks, determine options, and respond professionally. Let's see how the agent helps."

### Step 3.2: Run Comms Manager

**Command:**
```bash
python3 runner.py --role comms
```

**Expected behavior:**
- Reads client request
- Recognizes this affects delivery and risk
- Creates trigger files for Delivery + Risk roles
- Likely drafts acknowledgment to client in `outbox/comms/drafts/`
- Logs reasoning

**Check Comms actions:**
```bash
# Check reasoning
cat vaults/peaklogistics/agent/logs/comms/$(date +%Y-%m-%d).md

# Check if notified other roles
ls vaults/peaklogistics/agent/inbox/delivery/
ls vaults/peaklogistics/agent/inbox/risk/

# Check if drafted response
ls vaults/peaklogistics/agent/outbox/comms/drafts/
```

**Talk track:**
> "Comms Manager processed the request, recognized it needs cross-role coordination, and notified Delivery and Risk. It likely drafted an acknowledgment to Sarah saying 'we're analyzing this and will get back to you soon.' Notice it didn't SEND anything - just drafted it for my approval. Human in the loop for external communications."

### Step 3.3: Run Delivery Manager (Assess Timeline Impact)

**Command:**
```bash
python3 runner.py --role delivery
```

**Expected behavior:**
- Reads Comms' trigger about client request
- Analyzes timeline: 1 week left, is this feasible?
- Likely **asks User a question** via `agent/inbox/user/`
- Example question: *"Client wants real-time notifications. I estimate 4-5 days of work. Options: (A) extend deadline by 1 week, (B) descope something else, (C) decline. What's your preference?"*

**Check Delivery's question:**
```bash
ls vaults/peaklogistics/agent/inbox/user/
cat vaults/peaklogistics/agent/inbox/user/$(ls -t vaults/peaklogistics/agent/inbox/user/ | head -1)
```

**Talk track:**
> "Perfect. Delivery Manager did the math, realized this is tight, and asked ME - the human TPM - for guidance. It's not trying to make this decision alone. It's proposing options and asking for my call. This is the partnership model in action."

### Step 3.4: Run Risk Manager (Assess Risk)

**Command:**
```bash
python3 runner.py --role risk
```

**Expected behavior:**
- Reads trigger about scope increase
- Assesses risk level: HIGH (late scope change)
- Documents mitigation strategies
- Might also ask User a question or provide risk assessment to Delivery

**Check Risk's output:**
```bash
cat vaults/peaklogistics/agent/logs/risk/$(date +%Y-%m-%d).md
ls vaults/peaklogistics/agent/inbox/user/
```

**Talk track:**
> "Risk Manager independently assessed this as high risk - adding features at week 5 threatens quality and timeline. It documented mitigation steps: thorough testing, phased rollout, client expectation management."

### Step 3.5: User Reviews Questions and Answers

**Show questions:**
```bash
ls vaults/peaklogistics/agent/inbox/user/
```

**Talk track:**
> "Now I have questions from both Delivery and Risk in my inbox. As the TPM, this is where I make the strategic call. Let me answer them."

**Create answered question (simulate User's response):**
```bash
# Read Delivery's question first to get the filename
DELIVERY_Q=$(ls vaults/peaklogistics/agent/inbox/user/ | grep -v answered | head -1)

# Create answered version
cat > "vaults/peaklogistics/agent/inbox/user/answered/$DELIVERY_Q" << 'EOF'
---
id: 2026-02-14T15-15-timeline-options
from: delivery
to: user
date: 2026-02-14T15:15:00Z
status: answered
---

**Original Question:**
Client wants real-time notifications. I estimate 4-5 days of work. Options:
(A) Extend deadline by 1 week
(B) Descope something else
(C) Decline politely

What's your preference?

---

**Bruno's Answer:**

Option B with a twist: Let's propose a **phased approach** to the client.

**Phase 1 (by Feb 28):** SMS notifications only (simpler, faster)
**Phase 2 (week after launch):** Email notifications + rich templates

This gives them most of the value, shows we're responsive, and protects the deadline. The team can build Phase 1 in 3 days if we descope the "advanced filtering" feature (which Sarah said was nice-to-have).

Draft an options memo with timeline and trade-offs. I'll review before we send.
EOF

# Move original question to answered folder
mv "vaults/peaklogistics/agent/inbox/user/$DELIVERY_Q" "vaults/peaklogistics/agent/inbox/user/answered/"
```

**Talk track:**
> "I've answered Delivery's question with a strategic call: propose a phased approach. Give the client most of what they want, protect the deadline, descope a nice-to-have feature. Classic TPM trade-off negotiation. Now let's route this answer back to Delivery."

### Step 3.6: Route Answered Questions Back to Roles

**Command:**
```bash
python3 runner.py --once
```

**What happens:**
- `route_answered_questions()` runs
- Finds answered files in `agent/inbox/user/answered/`
- Reads `from:` field (e.g., "delivery")
- Moves file to `agent/inbox/delivery/`
- Then checks all inboxes and runs roles with pending items

**Show routing:**
```bash
ls vaults/peaklogistics/agent/inbox/delivery/
ls vaults/peaklogistics/agent/inbox/user/answered/
```

**Talk track:**
> "The system automatically routed my answer back to Delivery's inbox. Now let's run Delivery again to see it act on my guidance."

### Step 3.7: Delivery Creates Options Memo

**Command:**
```bash
python3 runner.py --role delivery
```

**Expected behavior:**
- Reads User's answer from inbox
- Implements the strategy: phased approach
- Drafts options memo to `agent/outbox/delivery/drafts/`
- Memo includes timeline, trade-offs, recommendation

**Check draft:**
```bash
ls vaults/peaklogistics/agent/outbox/delivery/drafts/
cat vaults/peaklogistics/agent/outbox/delivery/drafts/$(ls -t vaults/peaklogistics/agent/outbox/delivery/drafts/ | head -1)
```

**Talk track:**
> "Beautiful. Delivery Manager took my guidance and drafted a professional options memo. It includes the phased approach, timeline implications, and the trade-off (descope advanced filtering). Now I review this, make any tweaks, and 'approve' it by moving to the approved folder. Then Comms would use this to craft the client response."

**Simulate approval (manual step):**
```bash
DRAFT=$(ls -t vaults/peaklogistics/agent/outbox/delivery/drafts/ | head -1)
mv "vaults/peaklogistics/agent/outbox/delivery/drafts/$DRAFT" "vaults/peaklogistics/agent/outbox/delivery/approved/"
```

### Step 3.8: Wrap Up This Scenario

**Talk track:**
> "Let's imagine the client accepts the phased approach. The project delivers on time with Phase 1. Success! This showed the full human-agent loop:
> 1. External event (client request) enters system
> 2. Roles coordinate asynchronously (Comms → Delivery + Risk)
> 3. Roles analyze and ask User for strategic guidance
> 4. User makes the call (phased approach)
> 5. Role executes on User's guidance (draft options memo)
> 6. User reviews and approves before external communication
>
> The agent did the analysis, coordination, drafting - I made the strategic decision. Perfect partnership."

---

## Act 4: System Features Showcase (5 min)

### Step 4.1: Memory Accumulation

**Show memory files:**
```bash
cat vaults/peaklogistics/agent/memory/delivery.md
cat vaults/peaklogistics/agent/memory/risk.md
```

**Talk track:**
> "Each role accumulates patterns and lessons in its memory file. Over time, this becomes institutional knowledge. For example, if I consistently prefer phased approaches over deadline extensions, Delivery learns this and starts proposing it proactively."

### Step 4.2: Daily Summaries

**Explain daily compilation:**
```bash
ls vaults/peaklogistics/agent/logs/summaries/
```

**Talk track:**
> "Every day, the runner compiles all role logs into a single summary. This is your daily digest - what happened, what decisions were made, what's at risk. Perfect for standups or weekly reports. In production, this runs automatically at midnight."

### Step 4.3: Session Management

**Explain session concept:**
```bash
cat sessions/sessions.json
```

**Talk track:**
> "Notice each role has a session ID tied to today's date. If I run Delivery again right now, it will RESUME the same conversation - Claude remembers everything from earlier runs today. Tomorrow, it starts fresh with updated context. This balances continuity with avoiding stale context."

**Demonstrate (optional if time):**
```bash
python3 runner.py --role delivery
# Show that it references earlier runs in the same day
```

### Step 4.4: Scheduler Concept (Production Mode)

**Talk track:**
> "Everything we just did manually - I can let run automatically. Look at the role configs:"

```bash
cat roles/delivery.md | grep -A1 "## Schedule"
cat roles/risk.md | grep -A1 "## Schedule"
```

**Talk track:**
> "Delivery runs at 9am and 5pm weekdays. Risk runs at 10am. Comms is on-demand only. If I start the scheduler with just `python3 runner.py`, it runs forever:
> - Checks schedules every minute
> - Runs roles at their scheduled times
> - Polls inboxes for trigger files
> - Compiles daily summaries
> - All autonomously, 24/7.
>
> The TPM (me) just monitors the outputs, answers questions, and makes strategic calls. The agent handles the continuous monitoring, coordination, and documentation."

---

## Wrap-Up (2-3 min)

### Key Takeaways

**For non-technical audience:**
> "Think of this as having a tireless project coordinator who:
> - Monitors project health 24/7
> - Coordinates between different concerns (delivery, risk, communication)
> - Drafts documents and communications for your review
> - Asks smart questions when it needs your input
> - Never forgets, never gets emotional, never misses a scheduled check-in
>
> You (the human TPM) stay in control of all strategic decisions and external communications. The agent amplifies your effectiveness."

**For technical audience:**
> "This is Claude Code as infrastructure. Each role is a full Claude LLM instance with:
> - Role-specific system prompts (mission, goals, tools)
> - Access to project files (vault as message bus)
> - Structured reasoning (THINK/ACT/REFLECT logs)
> - Persistent memory across runs
> - Session management for context continuity
>
> It's not RPA, not scripting - it's autonomous reasoning with human oversight. The Agent SDK makes this trivial to set up and extend."

### What We Demonstrated

✅ **Multi-role coordination** - Roles operate independently but communicate via inboxes
✅ **Human-in-the-loop** - Agent asks questions, drafts communications, waits for approval
✅ **Event-driven + scheduled** - Responds to triggers AND runs proactively on schedule
✅ **Visible reasoning** - Every decision is logged and auditable
✅ **Memory & learning** - Accumulates patterns, preferences, lessons learned
✅ **Real-world scenario** - Handled scope creep at week 5 with strategic guidance

### Next Steps / Q&A

**Common questions to anticipate:**

**Q: "What if the agent makes a mistake?"**
A: "All external communications go through drafts → approval flow. Context updates are logged and reversible. The agent never takes destructive actions without explicit user confirmation."

**Q: "How much does this cost to run?"**
A: "Depends on frequency. A role run costs ~$0.01-0.10 depending on model and context size. Running 4 roles 2x/day = ~$1-2/day. Compare that to TPM time cost."

**Q: "Can I customize the roles?"**
A: "Absolutely. Role configs are markdown files. Change the mission, goals, tools, schedule - it's all plaintext configuration. Add new roles by creating a new .md file in roles/."

**Q: "What if I don't use Obsidian?"**
A: "The vault is just markdown files. Use any text editor, any note-taking tool, or even a git repo. The agent just reads and writes .md files."

**Q: "Does this work for non-software projects?"**
A: "Yes! The roles are domain-agnostic. Customize the project context files (scope, timeline, risks) for construction, marketing campaigns, event planning - any project with deliverables and stakeholders."

---

## Demo Artifacts to Preserve

After the demo, these files tell the story:

```bash
# Reasoning logs (the "thought process")
vaults/peaklogistics/agent/logs/delivery/
vaults/peaklogistics/agent/logs/risk/
vaults/peaklogistics/agent/logs/comms/

# Updated project context
vaults/peaklogistics/project/risks/
vaults/peaklogistics/project/timeline.md
vaults/peaklogistics/project/blockers/

# Role memory
vaults/peaklogistics/agent/memory/

# Draft communications
vaults/peaklogistics/agent/outbox/delivery/drafts/
vaults/peaklogistics/agent/outbox/delivery/approved/

# Inbox archives (processed triggers)
vaults/peaklogistics/agent/inbox/*/archive/
```

**Pro tip:** Run `tree vaults/peaklogistics/agent/` at the end to show the full artifact tree.

---

## Backup Scenarios (If Time Permits)

### Bonus: Show Product Manager Role

If there's extra time, run the Product role to show:
- Another perspective (product prioritization vs delivery vs risk)
- More role coordination examples

```bash
python3 runner.py --role product
```

### Bonus: Simulate a Real Schedule Run

If technical audience wants to see the scheduler:

```bash
python3 runner.py --dry-run  # Show what would run
# Or actually start it and let it run for 1-2 minutes
python3 runner.py
# Ctrl+C to stop
```

---

## Troubleshooting

**If a role doesn't produce expected output:**
- Check the reasoning log to see what it actually did
- Role behavior depends on current context - it reads files and makes decisions
- This is AI, not scripting - some variance is expected and valuable!

**If inbox routing doesn't work:**
- Verify YAML frontmatter has `from:` field
- Check role name matches exactly (case-sensitive)

**If session management seems off:**
- Check `sessions/sessions.json` for stale entries
- Delete sessions file to force fresh starts

---

## Final Notes

This demo script is **narrative-driven, not deterministic.** Claude's responses will vary based on context and reasoning. That's a feature, not a bug! Embrace the variance and point it out: *"See how it reasoned through this? Another run might phrase it differently, but the key decisions would be similar."*

The goal is to show the **system in action**, not to follow a rigid script. Be ready to improvise based on what the agent actually does.

**Good luck with the demo! 🚀**
