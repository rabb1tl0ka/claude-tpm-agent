# Project Decisions Log

## Week 0 (Kickoff)

### Decision: 1-week sprints instead of 2-week
**Date:** 2026-02-14
**Who:** Marcus (CEO), Sarah (CTO), Bruno (TPM)
**Context:** 6-week timeline is tight, need faster feedback cycles
**Decision:** Use 1-week sprints with Friday demos
**Rationale:** Weekly demos allow stakeholders to course-correct faster if something's off track

---

### Decision: React for frontend (not Vue or Angular)
**Date:** 2026-02-14
**Who:** Sarah (CTO), Joao (Backend), Zoran (Web)
**Context:** Choosing frontend framework
**Decision:** React 18+
**Rationale:** Team has React experience, large ecosystem, responsive UI patterns well-supported

---

### Decision: FastAPI for backend (not Django or Flask)
**Date:** 2026-02-14
**Who:** Sarah (CTO), Joao (Backend)
**Context:** Choosing Python backend framework
**Decision:** FastAPI
**Rationale:** Modern async support, automatic OpenAPI docs, type hints, faster than Flask for API-heavy workloads

---

### Decision: PostgreSQL for database
**Date:** 2026-02-14
**Who:** Sarah (CTO), Joao (Backend)
**Context:** Choosing database
**Decision:** PostgreSQL
**Rationale:** Relational model fits marketplace data (users, suppliers, shippers, trips, reservations), mature tooling, great for MVP

---

*This file logs key technical and product decisions. Include date, who made it, context, and rationale.*
