# Peak Logistics Movement (PLM) — V1 Timeline

## Project Duration
**6 weeks:** Feb 17 - Mar 28, 2026

## Cadence
- **1-week sprints** (faster feedback cycles than typical 2-week)
- **Daily standups** (async in Slack)
- **Weekly stakeholder sync** (Tuesdays 10am PT with Marcus, Sarah, Jen)
- **Weekly demos** (Fridays 2pm PT - show working software)

## Milestones

| Week | Dates | Milestone | Key Deliverables |
|------|-------|-----------|------------------|
| **Week 1** | Feb 17-21 | **Foundation & Design** | - Database schema finalized<br>- API spec reviewed with Sarah<br>- UI wireframes approved by Jen<br>- Dev environment setup<br>- Hosting environment provisioned |
| **Week 2** | Feb 24-28 | **Core Auth & Data Models** | - User sign-up/login working<br>- Database deployed<br>- Core API endpoints (users, suppliers, shippers)<br>- Basic React app scaffolding |
| **Week 3** | Mar 3-7 | **Supplier Flow** | - Suppliers can post shipments<br>- Shipment listing view<br>- Supplier dashboard<br>- Unit tests for shipment APIs |
| **Week 4** | Mar 10-14 | **Shipper Flow** | - Shippers can post trips<br>- Trip listing view<br>- Shipper dashboard<br>- Unit tests for trip APIs |
| **Week 5** | Mar 17-21 | **Reservation Flow & Polish** | - Supplier browse trips (filtering, matching)<br>- Reservation confirmation flow<br>- UI polish and responsive fixes<br>- Integration testing |
| **Week 6** | Mar 24-28 | **QA, Deployment, Launch** | - Full user journey testing<br>- Production deployment<br>- SSL & domain configured<br>- Launch! 🚀 |

## Critical Path

The following dependencies define the critical path (cannot parallelize):

1. **Database schema** → All feature development depends on this
2. **Authentication** → Must work before user-specific features
3. **Supplier posting shipments** → Required before browsing/reserving
4. **Shipper posting trips** → Required before reserving
5. **Production environment** → Required for launch

## Risk Buffer

- **Built-in buffer:** Estimates are conservative (2-4 days per feature vs optimistic 1-2 days)
- **Week 6 flex time:** If features slip into Week 5, Week 6 acts as buffer + QA
- **Scope flexibility:** If timeline at risk, "Browse & Reserve" can be simplified (manual matching via contact info vs in-app confirmation)

## Weekly Demo Schedule

**Every Friday 2pm PT:**
- Week 1: Database + API demo (Postman/Swagger)
- Week 2: Sign-up/login working in UI
- Week 3: Supplier can post a shipment
- Week 4: Shipper can post a trip
- Week 5: Supplier can browse and reserve
- Week 6: Full user journey + production deployment

## Stakeholder Touchpoints

**Weekly Status (Tuesdays 10am PT):**
- What shipped last week
- What's shipping this week
- Blockers or risks
- Decisions needed

**Design Reviews (as needed):**
- Week 1: Wireframes review with Jen
- Week 2: UI components review with Jen
- Week 3-5: Incremental design feedback

**Technical Sync (Fridays after demo):**
- Sarah joins for API/architecture discussions
- Review any technical risks or decisions

## Launch Checklist

**Week 6 - Before Launch:**
- [ ] All core user flows tested (sign-up → post → reserve)
- [ ] Database migrations tested (dev → staging → prod)
- [ ] Production environment SSL verified
- [ ] Domain configured (e.g., app.peaklogistics.com)
- [ ] Monitoring/logging configured
- [ ] Rollback plan documented
- [ ] Team available for post-launch support
- [ ] Stakeholders informed of launch date/time

## Post-Launch Plan

**Week 7 (Post-Launch Stabilization):**
- Monitor for critical bugs
- Collect user feedback
- Prioritize V2 features based on real usage data
- Conduct retrospective with team
