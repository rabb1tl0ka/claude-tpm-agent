# Peak Logistics Test Vault - Setup Summary

## ✅ Vault Restructured for Demo

The test vault at `vaults/peaklogistics/` has been completely restructured to represent a realistic **6-week project at kickoff (Day 0)**.

## 📁 Directory Structure

```
vaults/peaklogistics/
├── stakeholders/          Client team profiles
│   ├── marcus-reed.md     - CEO (speed, competitive pressure)
│   ├── sarah-chen.md      - CTO (technical rigor, API design)
│   └── jen-walsh.md       - VP Product (UX, user validation)
├── project/               Core project docs + tracked items
│   ├── scope.md           - 5 core features, 6-week timeline
│   ├── timeline.md        - Weekly milestones (Feb 17 - Mar 28)
│   ├── team.md            - Loka team (Joao, Zoran, Gorjan, Elena, Bruno)
│   ├── goals/             - Project objectives (1 file per goal)
│   ├── risks/             - Risk register (1 file per risk)
│   ├── blockers/          - Active blockers (1 file per blocker, archive/ subdir)
│   ├── decisions/         - Key decisions (1 file per decision)
│   ├── challenges/        - Project challenges (1 file per challenge)
│   └── traffic-lights/    - Weekly TLU reports (1 file per week)
├── templates/             Templates (TLU template, etc.)
├── agent/                 Agent workspace
│   ├── inbox/{role}/      - Trigger files
│   ├── outbox/{role}/     - Draft communications
│   ├── logs/{role}/       - Reasoning logs (THINK/ACT/REFLECT)
│   └── memory/{role}.md   - Per-role persistent memory
├── meetings/
├── daily/
├── memory.md
└── CLAUDE.md              Agent system prompt
```

## 🎭 The Scenario

**Project:** Peak Logistics Movement (PLM)
**Client:** PeakLogistics (startup)
**Goal:** Build marketplace connecting cargo suppliers with transportation shippers
**Timeline:** 6 weeks (Feb 17 - Mar 28, 2026)
**Status:** Day 0 (project kickoff)

**Core Features (V1):**
1. User sign-up
2. User login
3. Supplier posts shipments
4. Shipper posts trips
5. Supplier browses and reserves trips

**Tech Stack:** React (web) + FastAPI (backend) + PostgreSQL (database)

## 👥 Stakeholders

### PeakLogistics (Client)
- **Marcus Reed** - CEO - Wants speed, competitive pressure
- **Sarah Chen** - CTO - Technical rigor, API design decisions
- **Jen Walsh** - VP Product - UX focus, user validation

### Loka Team
- **Joao** - Backend Lead (FastAPI, PostgreSQL)
- **Zoran** - Web Lead (React, responsive UI)
- **Gorjan** - Design Lead (wireframes, UI design)
- **Elena** - QA (testing, Week 3-6)
- **Bruno** - TPM (oversight, stakeholder management)

## 🎬 Demo Narrative (from DEMO-SCRIPT.md)

**Act 1:** Project kickoff - First role runs, establish baseline
**Act 2:** Week 2 - Blocker discovered, roles coordinate
**Act 3:** Week 5 - Client requests new features, scope negotiation
**Act 4:** System features - Memory, summaries, sessions

## 🔄 Reset Mechanism

**Script:** `demo-reset.sh`

Resets the vault to pristine "Day 0" state:
- Git checkout to restore project files
- Cleans agent/ artifacts (logs, memory, inbox, outbox)
- Removes sessions.json

**Usage:**
```bash
./demo-reset.sh
python3 runner.py --dry-run  # Verify
```

## 🧪 Testing the Demo

**Pre-demo checklist:**
```bash
# 1. Verify structure
tree -L 2 vaults/peaklogistics/

# 2. Test config parsing
python3 runner.py --dry-run

# 3. Test single role
python3 runner.py --role delivery

# 4. Reset and verify
./reset-demo.sh
```

## 📋 Next Steps

1. **Commit this state:**
   ```bash
   git add .
   git commit -m "Demo-ready vault: PLM 6-week project kickoff state"
   ```

2. **Test the full demo flow:**
   - Follow DEMO-SCRIPT.md step by step
   - Validate agent behavior matches expectations
   - Adjust narrative if needed

3. **Practice the demo:**
   - Run through once solo
   - Time each section
   - Prepare talking points

## 🔑 Key Differences from Previous Vault

| Aspect | Before | After |
|--------|--------|-------|
| **Project state** | Week 5-6 (active) | Day 0 (kickoff) |
| **Timeline** | Sprint 42, Feb 10 start | Week 0, Feb 17 start |
| **Product** | RouteRunner V2 (7+ features) | PLM V1 (5 features) |
| **Stakeholders** | Referenced but not documented | 3 detailed profiles |
| **Goals** | Implied | Explicit goals/ directory |
| **Team** | Generic names (Alex, Nina, Leo) | Real Loka leads (Joao, Zoran, Gorjan, Elena) |
| **Blockers** | 2 active blockers | Clean slate (none) |
| **Structure** | Missing actions, challenges, traffic-lights | Complete real-world structure |

## 🎯 What This Enables

✅ **Realistic demo** - Vault matches real project kickoff state
✅ **Compelling narrative** - 6-week project mirrors Loka engagements
✅ **Repeatable** - Reset script allows unlimited demo runs
✅ **Credible** - Stakeholder profiles, goals, risks feel authentic
✅ **Educational** - Shows full project lifecycle (kickoff → crisis → resolution)

---

**Ready for demo!** 🚀
