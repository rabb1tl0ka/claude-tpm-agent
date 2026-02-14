# Peak Logistics Movement (PLM) — Risk Register

## Active Risks

### Risk #1: Timeline Aggressive for Marketplace Complexity
**Probability:** Medium
**Impact:** High
**Status:** Monitoring

**Description:**
6 weeks to build a two-sided marketplace (suppliers + shippers) with authentication, data models, and reservation system is aggressive. Marketplace products typically require 8-12 weeks for MVP.

**Mitigation:**
- Conservative estimates built into timeline (2-4 days per feature vs optimistic 1-2)
- Week 6 acts as buffer for slippage
- Scope flexibility: "Browse & Reserve" can be simplified if needed (manual matching vs in-app)
- Weekly demos to catch issues early

**Owner:** Bruno (TPM)
**Review Cadence:** Weekly status check

---

### Risk #2: Database Schema Must Be Right From Day 1
**Probability:** Medium
**Impact:** High
**Status:** Mitigating

**Description:**
Core entities (Users, Suppliers, Shippers, Containers, Trips, Reservations) define the data model. Getting this wrong early requires expensive refactoring later. No time for major DB rework in a 6-week timeline.

**Mitigation:**
- Week 1 priority: Sarah (CTO) reviews database schema before implementation
- Joao (Backend Lead) has marketplace experience, familiar with these patterns
- Build in foreign keys and constraints from start (data integrity)
- Document entity relationships and assumptions

**Owner:** Sarah (CTO) + Joao (Backend Lead)
**Review:** Week 1 architecture review

---

### Risk #3: Two-Sided Adoption (Suppliers + Shippers Both Needed)
**Probability:** Low (post-launch concern)
**Impact:** High
**Status:** Accepted

**Description:**
Marketplace only works if BOTH suppliers and shippers adopt. If only one side shows up, the platform has no value. This is a product-market fit risk, not a delivery risk.

**Mitigation:**
- Out of scope for V1 delivery (PeakLogistics owns go-to-market)
- Build feedback mechanisms so PeakLogistics can learn from real usage
- Instrument analytics from day 1 (user signups, posts, reservations)
- Marcus (CEO) has sales pipeline for initial users

**Owner:** Marcus (CEO) + Jen (VP Product)
**Review:** Post-launch

---

## Risk Monitoring

**Weekly review:**
- Any new risks identified?
- Have probabilities or impacts changed?
- Are mitigations working?

**Escalation triggers:**
- Critical path feature slips by >2 days
- Database schema requires major refactor after Week 1
- Key team member unavailable (illness, emergency)
- Scope creep threatens Week 6 launch date
