---
to: Bruno (Loka TPM)
from: risk
date: 2026-02-15T23:16:00Z
subject: RISK-001: Auth Delay — Mitigation Plan Ready
priority: high
status: answered
---

**Bruno,**

Joao's auth blocker is now tracked as **RISK-001** (see `project/risks/RISK-001-auth-delay.md`).

## TL;DR
- **Risk:** Auth taking 2x longer (2→4 days), pushes Week 2 milestone by 2 days
- **Impact:** Critical path blocker — delays all user-specific features
- **Recommendation:** Hybrid mitigation (stub API + parallel work) recovers most of the time
- **Action Needed:** Confirm approach with Joao/Zoran by Monday

---

## The Situation

**What Happened:**
Joao reports JWT + RBAC complexity underestimated. Original 2-day estimate now 4 days.

**Why It Matters:**
- Week 2 milestone "User sign-up/login working" at risk
- Auth is a prerequisite for Week 3-5 features (posting shipments/trips, reservations)
- 2-day slip consumes Week 6 buffer

---

## Mitigation Plan (Recommended)

**Hybrid: Stub API + Parallel Work**

1. **Monday-Tuesday (Feb 17-18):** Joao delivers "stub auth" (basic JWT, no RBAC yet)
2. **Tuesday onward:** Zoran builds React auth UI against stubs (parallel work)
3. **Tuesday-Thursday:** Joao completes full RBAC backend
4. **Friday (Feb 21):** Integrate, test, demo working login/signup
5. **Fallback:** If stub approach fails, absorb 2-day delay and lean on Week 6 buffer

**Why This Works:**
- Unblocks Zoran immediately (no idle time waiting for backend)
- Recovers 1-2 days via parallelization
- Maintains full scope (no RBAC reduction)
- Has clear fallback (buffer absorption)

---

## Other Options Considered

**Option 1: Absorb Delay**
- Accept 2-day slip, compress downstream work
- ❌ Puts pressure on Week 3-5 features

**Option 2: Simplify Auth Scope**
- Remove RBAC from V1, add post-MVP
- ❌ Requires client approval (scope change)
- ❌ May limit V1 UX

**Option 3 (Recommended): Parallel Work**
- Stub API unblocks frontend
- ✅ Recovers time, maintains scope

---

## What I Need From You

### Monday Feb 17 (Before Week 2 Kickoff)
1. **Confirm feasibility:** Talk to Joao — can he deliver stub API by EOD Tuesday?
2. **Align Zoran:** Can he start React auth UI with stubs?
3. **Decide on client comms:** Do we notify Marcus/Sarah/Jen now, or wait until Tuesday sync?

### Week 2 Monitoring
- I'll track daily progress (stub delivery, UI progress, integration)
- If stub approach fails by Wednesday, I'll escalate for scope decision

---

## Client Communication (Your Call)

**Options:**
1. **Wait until Tuesday sync:** "We identified a complexity in auth, mitigated with parallel work, on track for Friday demo"
2. **Notify early (Monday):** "Heads up — auth taking longer, here's our mitigation plan"

**My Take:** Marcus values transparency. If we notify Monday, shows we're proactive. If we wait until Tuesday, we'll have 1 day of data (stub delivered or not).

Your decision.

---

## Next Steps

1. You review this plan
2. You align with Joao/Zoran on feasibility
3. You decide client comms timing
4. I monitor daily and escalate if needed

**Risk file:** `project/risks/RISK-001-auth-delay.md` (full details)

Let me know how you want to proceed.

— Risk Manager

---

## Answer

Check with the Delivery Manager agent role.
I am OK with the mitigation plan recommended by you.
