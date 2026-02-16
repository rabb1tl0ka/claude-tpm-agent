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

**Verify system is ready:**
```bash
cd /home/rabb1tl0ka/loka/code/claude-tpm-agent
python3 runner.py --dry-run  # Should show 4 roles loaded
ls vaults/peaklogistics/project/  # Should show scope.md, timeline.md, etc.
```

**Clean slate for demo:**
```bash
./demo-reset.sh  # OR manually:

# Clear any existing logs/sessions from previous runs
rm -rf vaults/peaklogistics/agent/logs/delivery/*
rm -rf vaults/peaklogistics/agent/logs/risk/*
rm -rf vaults/peaklogistics/agent/logs/comms/*
rm -rf vaults/peaklogistics/agent/logs/product/*
rm -rf vaults/peaklogistics/agent/memory/*.md
rm -f sessions/sessions.json

# Ensure inboxes are empty
rm -f vaults/peaklogistics/agent/inbox/delivery/*
rm -f vaults/peaklogistics/agent/inbox/risk/*
rm -f vaults/peaklogistics/agent/inbox/comms/*
rm -f vaults/peaklogistics/agent/inbox/product/*
rm -f vaults/peaklogistics/agent/inbox/user/*
```

**Terminal layout (5 terminals recommended):**

1. **Terminal 1 (Runner):** `python3 runner.py` — Shows system activity, inbox checks
2. **Terminal 2 (Delivery logs):** `tail -F vaults/peaklogistics/agent/logs/delivery/$(date +%Y-%m-%d).md` (use -F to wait for file creation)
3. **Terminal 3 (Risk logs):** `tail -F vaults/peaklogistics/agent/logs/risk/$(date +%Y-%m-%d).md` (use -F to wait for file creation)
4. **Terminal 4 (Comms logs):** `tail -F vaults/peaklogistics/agent/logs/comms/$(date +%Y-%m-%d).md` (use -F to wait for file creation)
5. **Terminal 5 (Your working terminal):** For creating trigger files, running commands

**Note:** Use `tail -F` (capital F) instead of `tail -f` - this waits for the file to be created and retries if it doesn't exist yet.

**Alternative setup (3 terminals):**
- Terminal 1: Runner
- Terminal 2: Your working terminal
- Terminal 3: `tail -f` on whichever role is about to run (switch as needed)

**Have ready:**
- Obsidian app open to `vaults/peaklogistics/` (for visual file creation)
- OR pre-written `cat` commands in a scratch file (for speed)

---

## Act 1: System Startup & First Autonomous Run (5-7 min)

### Context for Audience
*"We're at project kickoff. The vault already has project scope, timeline, team info, and initial risk register. The system runs autonomously — it checks for scheduled times and new events every minute. Let me start the runner and show you the architecture."*

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
- `agent/logs/{role}/` = reasoning artifacts (THINK/ACT/REFLECT) — **one file per day**
- `agent/memory/{role}.md` = learned patterns across runs

### Step 1.2: Start the Runner

**Command (Terminal 1):**
```bash
python3 runner.py
```

**Expected output:**
```
[2026-02-15 09:00:00] === Claude TPM Agent Runner ===
[2026-02-15 09:00:00] Roles: comms, delivery, product, risk
[2026-02-15 09:00:00] Vault: /home/.../vaults/peaklogistics
[2026-02-15 09:00:00] [comms] Schedule: every 30 minutes
[2026-02-15 09:00:00] [delivery] Schedule: daily at 09:00
[2026-02-15 09:00:00] [delivery] Schedule: daily at 17:00
[2026-02-15 09:00:00] [product] Schedule: on-demand (inbox-triggered only)
[2026-02-15 09:00:00] [risk] Schedule: daily at 10:00
[2026-02-15 09:00:00] Runner started. Press Ctrl+C to stop.
[2026-02-15 09:00:00] Checking inboxes...
```

**Talk track:**
> "The runner loaded 4 roles with their schedules. Delivery runs at 9am and 5pm. Risk runs at 10am. Comms checks every 30 minutes. Product is on-demand only. Every minute, it checks for new files in role inboxes and runs scheduled jobs if it's time. Watch Terminal 1 — you'll see it check inboxes every 60 seconds."

### Step 1.3: Trigger First Run (Manual Trigger)

**Talk track:**
> "Delivery is scheduled for 9am, but let me trigger it now by dropping a file in its inbox. This simulates a human TPM (me) asking Delivery to do an initial assessment."

**Option A: Create trigger via Obsidian (recommended for relatability)**
1. Open Obsidian in `vaults/peaklogistics/`
2. Navigate to `agent/inbox/delivery/`
3. Create new note: `2026-02-15T09-00-kickoff.md`
4. Add content:
```markdown
---
from: user
date: 2026-02-15T09:00:00Z
priority: medium
---

This is project kickoff (Day 0). Please review the project scope, timeline, and team, and create your baseline assessment.
```
5. Save

**Option B: Create trigger via terminal (faster)**
```bash
cat > vaults/peaklogistics/agent/inbox/delivery/2026-02-15T09-00-kickoff.md << 'EOF'
---
from: user
date: 2026-02-15T09:00:00Z
priority: medium
---

This is project kickoff (Day 0). Please review the project scope, timeline, and team, and create your baseline assessment.
EOF
```

### Step 1.4: Watch the System React

**Talk track:**
> "I just dropped a file in Delivery's inbox. The system checks every minute, so within the next 60 seconds it should detect this... watch Terminal 1..."

**Wait for runner output:**
```
[2026-02-15 09:00:30] Checking inboxes...
[2026-02-15 09:00:30] [delivery] inbox trigger
[2026-02-15 09:00:30] [delivery] Model: haiku
```

**Point to Terminal 2 (Delivery logs):**
> "And here's Delivery Manager's reasoning appearing in real-time..."

**Expected log structure (Terminal 2):**
```markdown
## Run 09:00 (inbox)

### Inbox
- 2026-02-15T09-00-kickoff.md: Project kickoff baseline assessment request

### What Changed
- First run of the day
- Project is at Day 0 (kickoff)

### Priority Action
- Review scope.md, timeline.md, team.md
- Establish baseline: what are we building, when, with whom
- Confirm Week 1 milestones are clear

### Not Doing
- No blockers to escalate yet
- No communications to draft
- No adjustments needed (nothing started yet)

### Reflection
Baseline established. Project structure is clear: 6-week MVP with conservative estimates and Week 6 buffer. Timeline looks feasible if database schema is validated in Week 1. Ready to monitor progress starting Week 1.
```

**Talk track:**
> "Notice the structure: Inbox, What Changed, Priority Action, Not Doing, Reflection. Every run follows this THINK/ACT/REFLECT cycle. This isn't a script — Claude reasoned through what matters and documented it."

### Step 1.5: Show Memory Initialization

**Check if memory file was created:**
```bash
cat vaults/peaklogistics/agent/memory/delivery.md
```

**Talk track (if file exists):**
> "The role can update its memory file to accumulate lessons across runs. This becomes institutional knowledge that persists beyond individual sessions."

**Talk track (if file doesn't exist yet):**
> "Memory files are created when a role learns a recurring pattern or receives feedback. We'll see this later when roles start coordinating."

---

## Act 2: Event-Driven Coordination (8-10 min)

### Context for Audience
*"Fast forward to week 2. Joao (Backend Lead) reports a blocker: the user authentication implementation is more complex than estimated. JWT token management and role-based access control is taking longer than expected. Let's see how the system coordinates autonomously."*

### Step 2.1: Create Blocker Trigger (Visual via Obsidian)

**Talk track:**
> "As the TPM, I notice a blocker. Let me add a note to the Risk Manager's inbox..."

**Create via Obsidian:**
1. Navigate to `agent/inbox/risk/`
2. Create: `2026-02-15T14-30-blocker-auth.md`
3. Add content:
```markdown
---
from: user
date: 2026-02-15T14:30:00Z
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
```
4. Save

**Talk track:**
> "I just dropped this blocker in Risk Manager's inbox. The system will detect it within the next minute... watch Terminal 1..."

### Step 2.2: Watch Risk Manager React

**Wait for runner output (up to 60 seconds):**
```
[2026-02-15 14:31:00] Checking inboxes...
[2026-02-15 14:31:00] [risk] inbox trigger
[2026-02-15 14:31:00] [risk] Model: haiku
```

**Point to Terminal 3 (Risk logs):**
> "There — Risk Manager detected the blocker and is analyzing it now..."

**Expected log output (Terminal 3):**
```markdown
## Run 14:31 (inbox)

### Inbox
- 2026-02-15T14-30-blocker-auth.md: High priority — auth implementation 2x estimate

### What Changed
- New blocker: Authentication taking 4 days instead of 2
- Week 2 milestone at risk

### Priority Action
- Create risk entry in project/risks/
- Create blocker entry in project/blockers/
- Assess impact: 2-day slip on critical path
- Notify Delivery Manager (auth delay affects timeline)

### Not Doing
- Not escalating to User yet (Week 6 buffer can absorb 2 days)
- Not recommending descope (auth is non-negotiable)

### Reflection
This blocker is manageable but needs monitoring. Mitigation: Joao has marketplace experience, Sarah (CTO) available for review. If this slips another 2 days, we'll need to descope Week 5 features.
```

**Talk track:**
> "Risk Manager assessed severity, documented it, and decided to notify Delivery. Watch — it should create a trigger file for Delivery in the next few seconds..."

### Step 2.3: Check Risk's Actions

**Command:**
```bash
ls vaults/peaklogistics/agent/inbox/delivery/
```

**Expected:**
```
2026-02-15T14-31-auth-blocker-risk-assessment.md
```

**Talk track:**
> "There it is! Risk created a notification for Delivery. The system will pick this up in the next check... watch Terminal 1 again..."

### Step 2.4: Watch Delivery React

**Wait for runner output (up to 60 seconds):**
```
[2026-02-15 14:32:00] Checking inboxes...
[2026-02-15 14:32:00] [delivery] inbox trigger
[2026-02-15 14:32:00] [delivery] Model: haiku
```

**Point to Terminal 2 (Delivery logs):**
> "And now Delivery Manager is responding to Risk's notification..."

**Expected log output (Terminal 2):**
```markdown
## Run 14:32 (inbox)

### Inbox
- Auth blocker notification from Risk Manager

### What Changed
- Week 2 milestone "User sign-up/login working" delayed by 2 days
- Critical path affected (all user features depend on auth)

### Priority Action
- Confirm Week 6 buffer can absorb this slip
- Update timeline.md with revised Week 2 date
- Monitor: if auth slips further, Week 6 launch at risk

### Not Doing
- Not drafting stakeholder communication yet (within buffer)
- Not recommending descope (auth is MVP requirement)

### Reflection
2-day slip is manageable with current buffer. Week 6 still feasible if no additional delays. Next check: monitor auth progress daily.
```

**Talk track:**
> "Perfect! Delivery Manager received the notification, assessed timeline impact, updated the project timeline, and determined this is manageable with the Week 6 buffer. Notice how the roles coordinated **asynchronously** — Risk → Delivery — without any manual intervention. This is the autonomous event-driven architecture in action."

### Step 2.5: Verify Context Updates

**Show updated files:**
```bash
# Check new risk file
ls vaults/peaklogistics/project/risks/

# Check new blocker file
ls vaults/peaklogistics/project/blockers/

# Check archived trigger
ls vaults/peaklogistics/agent/inbox/risk/archive/
```

**Talk track:**
> "The roles updated the project context. Risk created a new risk file, a new blocker file, and archived the processed trigger. Delivery updated the timeline. All of this happened autonomously."

---

## Act 3: Week 5 Crisis - Client Request (10-12 min)

### Context for Audience
*"Now we're at week 5. We're on track. Then the client sends an email: 'We'd love to add real-time shipment notifications before launch.' Classic scope creep. Let's see how the system helps me navigate this."*

### Step 3.1: Create Client Request Trigger

**Talk track:**
> "I just received an email from the client. Let me forward this to the Comms Manager..."

**Create via Obsidian (or cat):**
```markdown
---
from: user
date: 2026-02-15T15-00:00Z
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
```

Save to: `agent/inbox/comms/2026-02-15T15-00-client-request.md`

**Talk track:**
> "Client wants real-time notifications at week 5. Classic. The system should detect this in the next check..."

### Step 3.2: Watch Comms Manager React

**Wait for runner:**
```
[2026-02-15 15:01:00] Checking inboxes...
[2026-02-15 15:01:00] [comms] inbox trigger
```

**Point to Terminal 4 (Comms logs):**
> "Comms Manager is processing this now..."

**Expected reasoning:**
- Recognize this affects delivery timeline and risk
- Create triggers for both Delivery and Risk roles
- Draft acknowledgment for client (for Bruno's approval)

**Talk track:**
> "Comms recognized this needs cross-role analysis. It should create triggers for Delivery and Risk..."

### Step 3.3: Watch Cascade of Coordination

**Within next 1-2 minutes, you should see:**

1. **Delivery runs** (triggered by Comms):
   - Analyzes timeline: 1 week left, notifications = 4-5 days work
   - Likely asks User a question via `agent/inbox/user/`

2. **Risk runs** (triggered by Comms):
   - Assesses: Late scope change = HIGH risk
   - Documents mitigation strategies

**Point to Terminal 1:**
> "Watch the cascade — Comms triggered both Delivery and Risk, and the system is running them one after another..."

**Point to Terminals 2 and 3:**
> "See their reasoning appearing in real-time. Delivery is doing the math... Risk is assessing severity..."

### Step 3.4: Check User Inbox (Questions)

**After both roles finish:**
```bash
ls vaults/peaklogistics/agent/inbox/user/
```

**Expected:**
- Question from Delivery about timeline options
- (Possibly) Question from Risk about risk tolerance

**Show one question:**
```bash
cat vaults/peaklogistics/agent/inbox/user/2026-02-15T15-02-timeline-options.md
```

**Expected content:**
```markdown
---
id: 2026-02-15T15-02-timeline-options
from: delivery
to: user
date: 2026-02-15T15:02:00Z
status: open
---

Client wants real-time notifications (SMS/email). I estimate 4-5 days of work.

**Options:**
(A) Extend deadline by 1 week (new launch: March 5)
(B) Descope another feature to fit this in
(C) Decline politely and propose for V2

**Timeline impact:**
- Option A: Low risk, but misses original deadline
- Option B: Feasible if we cut "advanced filtering" (nice-to-have)
- Option C: Zero timeline risk, but disappointed client

What's your preference?
```

**Talk track:**
> "Perfect. Delivery analyzed this, realized it's tight, and asked ME — the human TPM — for a strategic call. It's not trying to make this decision alone. This is the **human-in-the-loop** design. Now, as the TPM, I make the call..."

### Step 3.5: Answer the Question

**Create answered file:**
```bash
# Copy question to answered folder with your response
cat > vaults/peaklogistics/agent/inbox/user/answered/2026-02-15T15-02-timeline-options.md << 'EOF'
---
id: 2026-02-15T15-02-timeline-options
from: delivery
to: user
date: 2026-02-15T15:02:00Z
status: answered
---

Client wants real-time notifications. I estimate 4-5 days of work.

**Options:**
(A) Extend deadline by 1 week
(B) Descope another feature
(C) Decline and propose V2

---

**Bruno's Answer:**

Option B with a twist: **phased approach**

**Phase 1 (by Feb 28):** SMS notifications only (simpler, faster)
**Phase 2 (week after launch):** Email notifications + rich templates

This gives them most of the value, shows we're responsive, and protects the deadline. The team can build Phase 1 in 3 days if we descope the "advanced filtering" feature (which Sarah said was nice-to-have).

Draft an options memo with timeline and trade-offs. I'll review before we send.
EOF
```

**Talk track:**
> "I've decided on a phased approach: give them SMS notifications by the deadline, email templates post-launch. This is a classic TPM negotiation move. Now the system will route this answer back to Delivery..."

### Step 3.6: Watch Delivery Receive Answer

**Wait for next check (up to 60 seconds):**
```
[2026-02-15 15:04:00] Checking inboxes...
[2026-02-15 15:04:00] [delivery] inbox trigger
```

**Point to Terminal 2:**
> "Delivery just received my answer and is implementing the strategy..."

**Expected log output:**
- Reads User's phased approach decision
- Drafts options memo to `agent/outbox/delivery/drafts/`
- Memo includes phased timeline, trade-offs, recommendation

### Step 3.7: Show Draft Communication

**Check draft:**
```bash
ls vaults/peaklogistics/agent/outbox/delivery/drafts/
cat vaults/peaklogistics/agent/outbox/delivery/drafts/[latest-file]
```

**Talk track:**
> "Beautiful. Delivery took my guidance and drafted a professional options memo. It includes the phased approach, timeline implications, and the trade-off. Now I review this, make any tweaks, and 'approve' it by moving to the approved folder. Then Comms would craft the actual client response."

**Simulate approval:**
```bash
DRAFT=$(ls -t vaults/peaklogistics/agent/outbox/delivery/drafts/ | head -1)
mv "vaults/peaklogistics/agent/outbox/delivery/drafts/$DRAFT" "vaults/peaklogistics/agent/outbox/delivery/approved/"
```

**Talk track:**
> "This showed the full human-agent loop:
> 1. External event (client request) enters system
> 2. Roles coordinate asynchronously (Comms → Delivery + Risk)
> 3. Roles analyze and ask User for strategic guidance
> 4. User makes the call (phased approach)
> 5. Role executes on User's guidance (draft options memo)
> 6. User reviews and approves before external communication
>
> The agent did the analysis, coordination, drafting — I made the strategic decision. Perfect partnership."

---

## Act 4: System Features Showcase (3-5 min)

### Step 4.1: Daily Log Files

**Show today's logs:**
```bash
# Check if log file exists first
ls vaults/peaklogistics/agent/logs/delivery/$(date +%Y-%m-%d).md && \
cat vaults/peaklogistics/agent/logs/delivery/$(date +%Y-%m-%d).md
```

**Talk track:**
> "Notice each role has ONE log file per day. All runs are appended to the same file with section headers. This makes it trivial to review what a role did today. And for the demo, `tail -F` (capital F) shows reasoning in real-time as the role runs, even waiting for the file to be created first."

### Step 4.2: Memory Accumulation

**Show memory files:**
```bash
cat vaults/peaklogistics/agent/memory/delivery.md
cat vaults/peaklogistics/agent/memory/risk.md
```

**Talk track:**
> "Each role accumulates patterns and lessons in its memory file. Over time, this becomes institutional knowledge. For example, if I consistently prefer phased approaches over deadline extensions, Delivery learns this and starts proposing it proactively."

### Step 4.3: Session Management

**Show sessions:**
```bash
cat sessions/sessions.json
```

**Talk track:**
> "Each role has a session ID tied to today's date. If Delivery runs again right now, it RESUMES the same conversation — Claude remembers everything from earlier runs today. Tomorrow, it starts fresh with updated context. This balances continuity with avoiding stale context."

### Step 4.4: The Runner (Production Mode)

**Point to Terminal 1 (still running):**
> "This runner has been running the whole demo. In production, you start it once and it runs forever:
> - Checks schedules every minute
> - Runs roles at their scheduled times
> - Polls inboxes for trigger files
> - Compiles daily summaries
> - All autonomously, 24/7.
>
> The TPM (me) just monitors the outputs, answers questions, and makes strategic calls. The agent handles the continuous monitoring, coordination, and documentation."

**Stop the runner:**
```
Ctrl+C
```

**Talk track:**
> "And it shuts down cleanly when you stop it."

---

## Wrap-Up (2-3 min)

### Key Takeaways

**For non-technical audience:**
> "Think of this as having a tireless project coordinator who:
> - Monitors project health 24/7
> - Coordinates between different concerns (delivery, risk, communication)
> - Drafts documents and communications for your review
> - Asks smart questions when it needs your input
> - Reacts to events within minutes
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
> - Event-driven + scheduled execution
>
> It's not RPA, not scripting — it's autonomous reasoning with human oversight. The Agent SDK makes this trivial to set up and extend."

### What We Demonstrated

✅ **Autonomous event-driven system** - Roles react to inbox triggers within 60 seconds
✅ **Multi-role coordination** - Risk → Delivery cascade without manual intervention
✅ **Human-in-the-loop** - Agent asks questions, drafts communications, waits for approval
✅ **Scheduled + reactive** - Roles run at scheduled times AND react to events
✅ **Visible reasoning** - Real-time logs via tail show agent thinking
✅ **Memory & learning** - Accumulates patterns, preferences, lessons learned
✅ **Real-world scenario** - Handled scope creep at week 5 with strategic guidance

### Next Steps / Q&A

**Common questions to anticipate:**

**Q: "What if the agent makes a mistake?"**
A: "All external communications go through drafts → approval flow. Context updates are logged and reversible. The agent never takes destructive actions without explicit user confirmation."

**Q: "The 60-second wait seems slow. Can you make it faster?"**
A: "Absolutely. Change `time.sleep(60)` to `time.sleep(5)` for 5-second checks, or implement file watching for sub-second reaction times. For TPM work, 60 seconds is usually fine — humans don't react instantly either."

**Q: "How much does this cost to run?"**
A: "Depends on frequency. A role run costs ~$0.01-0.10 depending on model and context size. Running 4 roles 2x/day = ~$1-2/day. Compare that to TPM time cost."

**Q: "Can I customize the roles?"**
A: "Absolutely. Role configs are markdown files. Change the mission, goals, tools, schedule — it's all plaintext configuration. Add new roles by creating a new .md file in roles/."

**Q: "What if I don't use Obsidian?"**
A: "The vault is just markdown files. Use any text editor, any note-taking tool, or even a git repo. The agent just reads and writes .md files."

**Q: "Does this work for non-software projects?"**
A: "Yes! The roles are domain-agnostic. Customize the project context files (scope, timeline, risks) for construction, marketing campaigns, event planning — any project with deliverables and stakeholders."

---

## Demo Artifacts to Preserve

After the demo, these files tell the story:

```bash
# Daily reasoning logs (one file per role per day)
vaults/peaklogistics/agent/logs/delivery/2026-02-15.md
vaults/peaklogistics/agent/logs/risk/2026-02-15.md
vaults/peaklogistics/agent/logs/comms/2026-02-15.md

# Updated project context
vaults/peaklogistics/project/risks/
vaults/peaklogistics/project/blockers/
vaults/peaklogistics/project/timeline.md

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

## Timing Tips

**Act 1 (5-7 min):** Don't wait for scheduled time — use manual trigger. Explain you're speeding things up for the demo.

**Act 2 (8-10 min):** This is where the autonomous behavior shines. The 60-second waits create natural pause points for narration:
- While waiting for Risk to detect the blocker: Explain the inbox watching mechanism
- While waiting for Delivery to detect Risk's notification: Highlight the role coordination pattern

**Act 3 (10-12 min):** Most complex. If timing gets tight, you can manually trigger roles:
```bash
python3 runner.py --role delivery  # Override autonomous mode
```
Explain: "For time, let me trigger this manually rather than wait for the next check..."

**Total runtime with waits:** ~28-32 minutes (fits 30-minute slot with Q&A)

---

## Fallback Plan (If Runner Breaks Mid-Demo)

If the runner crashes or hangs:

1. **Ctrl+C** to stop it
2. **Check logs:** `tail logs/[latest]_runner.log`
3. **Restart runner:** `python3 runner.py`
4. **Or switch to manual mode:** Use DEMO-SCRIPT-MANUAL.md approach (manually run `--role` commands)

The system is resilient — all state is in files, so restarting the runner picks up where it left off.

---

**Good luck with the demo! 🚀**
