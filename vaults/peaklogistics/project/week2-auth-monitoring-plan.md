# Week 2 Auth Risk Monitoring Plan

**Risk:** RISK-001 (Auth delay: 2→4 days)
**Mitigation:** Hybrid approach — stub API + parallel RBAC work
**Week:** Feb 17-21, 2026 (Week 2)

---

## Daily Monitoring Schedule

### Monday Feb 17 — Kickoff & Alignment

**Critical Milestones:**
- [ ] Joao confirms stub auth API spec (basic JWT, no RBAC yet)
- [ ] Zoran confirms he can start UI work against stubs
- [ ] Stub API contract documented (endpoints, request/response format)

**Check-in Questions:**
- Joao: "Can you deliver stub auth API by EOD Tuesday?"
- Zoran: "Can you start React login/signup UI with stub endpoints?"
- Both: "What could block this plan?"

**Success Signal:** Both confirm feasibility, no blockers identified

**Escalation Trigger:** Either engineer raises concerns about stub approach → escalate to Bruno immediately

---

### Tuesday Feb 18 — Stub API Delivery (CRITICAL)

**Critical Milestone:**
- [ ] Joao delivers stub auth API by EOD (6pm PT / 3am CET+1)

**Stub API Requirements:**
- Basic JWT token generation
- `/signup` endpoint (minimal validation)
- `/login` endpoint (returns JWT)
- `/logout` endpoint (stub only)
- **No RBAC logic yet** — just "user exists" check

**Check-in Questions:**
- Joao (EOD): "Is stub API deployed and documented?"
- Zoran (EOD): "Can you start UI work tomorrow with these endpoints?"

**Success Signal:** Stub API deployed, Zoran has working endpoints to call

**Escalation Trigger:** Stub API NOT delivered by EOD Tuesday → activate fallback plan (absorb 2-day delay, notify Bruno)

---

### Wednesday Feb 19 — UI Progress & RBAC Development

**Critical Milestones:**
- [ ] Zoran: React login/signup UI in progress (forms, API calls, basic error handling)
- [ ] Joao: RBAC backend development in progress (supplier/shipper roles)

**Check-in Questions:**
- Zoran: "Is the stub API working as expected? Any integration issues?"
- Joao: "Is RBAC backend on track for Thursday completion?"

**Success Signal:** Zoran making progress on UI, Joao on track for RBAC

**Escalation Trigger:**
- Stub API has breaking issues → Zoran blocked → escalate to Bruno
- Joao behind on RBAC → won't finish Thursday → notify Bruno (fallback = absorb delay)

---

### Thursday Feb 20 — RBAC Completion

**Critical Milestone:**
- [ ] Joao: Full RBAC backend complete (supplier/shipper roles, permission checks)

**RBAC Requirements:**
- Role assignment on signup (supplier vs shipper)
- JWT includes role claim
- Endpoints check role permissions
- Unit tests for role-based access

**Check-in Questions:**
- Joao (EOD): "Is RBAC backend complete and tested?"
- Zoran: "Are you ready to integrate with full RBAC API tomorrow?"

**Success Signal:** RBAC backend complete, Joao ready to integrate

**Escalation Trigger:** RBAC not complete by EOD Thursday → Friday becomes integration+fix day (demo at risk)

---

### Friday Feb 21 — Integration & Demo

**Critical Milestones:**
- [ ] Integration: Swap stub API → full RBAC API
- [ ] Testing: Login/signup works with RBAC
- [ ] Demo (2pm PT): Show working authentication to stakeholders

**Integration Tasks:**
- Replace stub endpoints with RBAC endpoints
- Test supplier signup/login
- Test shipper signup/login
- Verify role-based access (supplier can't access shipper endpoints, etc.)

**Check-in Questions:**
- Morning: "Integration issues found overnight?"
- Pre-demo (1pm PT): "Are we ready to demo login/signup?"

**Success Signal:** Demo shows working login/signup with RBAC

**Escalation Trigger:** Critical integration bugs → demo postponed → escalate to Bruno

---

## Success Criteria (End of Week 2)

- ✅ Week 2 demo shows working login/signup
- ✅ No further delay beyond 2 days (Week 2 ends on time)
- ✅ Full RBAC scope delivered (no scope reduction)

---

## Fallback Plan (If Stub Approach Fails)

**Trigger:** Stub API not delivered by EOD Wednesday Feb 19

**Actions:**
1. Activate Option 1: Absorb 2-day delay
2. Zoran waits for full RBAC backend (completes Thursday)
3. UI work happens Friday-Monday (spills into Week 3)
4. Week 6 buffer absorbs 2-day slip
5. Notify Bruno → Bruno notifies client at Tuesday sync (Feb 18)

**Timeline Impact:**
- Week 2 milestone "login/signup working" delayed to Monday Feb 24
- Week 3 feature work starts Tuesday Feb 25 (1 day late)
- Uses 2 days of Week 6 buffer

---

## Communication Plan

### Internal (Loka Team)
- **Daily check-ins:** TPM Agent monitors via Slack #plm-daily
- **Blockers:** Escalate to Bruno immediately (no waiting for daily standup)
- **Friday demo prep:** Dry-run demo Thursday afternoon

### Client (PeakLogistics)
- **Bruno decides timing:** Notify Monday vs wait for Tuesday sync
- **Tuesday sync (Feb 18, 10am PT):** Mention auth complexity, mitigation in place
- **Friday demo (Feb 21, 2pm PT):** Show working auth (if successful)

---

## Coordination Checklist (For Bruno)

Before Monday Feb 17:
- [ ] Confirm Joao understands stub API requirements
- [ ] Confirm Zoran ready to work with stub endpoints
- [ ] Ensure both engineers have Monday Feb 17 free for alignment

Monday Feb 17:
- [ ] Morning: Joao/Zoran alignment call (or async confirmation)
- [ ] EOD: Stub API spec documented and shared

Tuesday Feb 18:
- [ ] EOD: Verify stub API delivered
- [ ] Notify client at Tuesday sync (if Bruno decides to mention)

Wednesday-Friday:
- [ ] Daily: Monitor for escalation triggers
- [ ] Friday 1pm PT: Dry-run demo prep

---

**Prepared by:** TPM Agent (Delivery)
**Reviewed by:** [Bruno to review]
**Next Update:** Monday Feb 17 (after team alignment)
