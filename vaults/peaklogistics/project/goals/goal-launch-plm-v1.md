# Goal: Launch Peak Logistics Movement (PLM) V1

## What is PLM

Peak Logistics Movement (PLM) is a marketplace platform that connects:
- **Suppliers** - Companies with containers/cargo that need to be shipped from location A to location B
- **Shippers** - Transportation companies with trucks, routes, and available capacity

The platform solves the inefficiency of manual matching between suppliers and carriers, reducing empty truck miles and giving suppliers better pricing through a competitive marketplace.

## Tech Stack

- **Web:** React (responsive web app)
- **Backend:** Python + FastAPI
- **Database:** PostgreSQL
- **Hosting:** TBD (likely AWS or GCP)

## The Goal

Launch V1 of PLM as a functional MVP in 6 weeks (target: March 28, 2026).

## Success Criteria

**For Launch (V1):**
- [ ] Suppliers can sign up, log in, and post shipment requests (origin, destination, cargo details)
- [ ] Shippers can sign up, log in, and post available trips (route, capacity, pricing)
- [ ] Suppliers can browse available trips and select/confirm reservations
- [ ] Basic authentication and authorization (user accounts, login sessions)
- [ ] Data persists correctly (suppliers, shippers, containers, trips, reservations)
- [ ] Responsive web UI works on desktop and tablet
- [ ] Deployed to production environment with SSL

**Post-Launch Validation (first 2 weeks):**
- [ ] 5+ suppliers successfully post shipments
- [ ] 3+ shippers successfully post trips
- [ ] At least 10 reservations confirmed through the platform
- [ ] No critical bugs blocking core user flows
- [ ] User feedback collected via in-app mechanism

## What's Out of Scope (V2+)

**Not building in V1:**
- Payment processing (escrow, invoicing)
- Real-time tracking of shipments in transit
- Mobile native apps (iOS/Android)
- Multi-leg routing (A → B → C)
- Shipper ratings/reviews
- Advanced search/filtering
- Notifications (email/SMS alerts)
- Admin dashboard for PeakLogistics team

## Current State

**Project Status:** Kickoff (Week 0)
**Timeline:** Feb 17 - Mar 28, 2026 (6 weeks)
**Team:** Loka engineering team assigned

## Risks to Success

1. **Timeline risk** - 6 weeks is aggressive for a marketplace platform
2. **Adoption risk** - Platform only works if both suppliers AND shippers adopt it
3. **Scope creep risk** - Pressure to add features that threaten timeline
4. **Data model complexity** - Core entities need to be right from the start

## Why This Matters

- **Market opportunity** - PeakLogistics is in a race with 2-3 competitors to own this space
- **Funding dependency** - Series A funding depends on demonstrating product-market fit
- **First-mover advantage** - Getting to market first builds network effects (more suppliers attract more shippers)
