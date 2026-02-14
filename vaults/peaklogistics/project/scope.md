# Peak Logistics Movement (PLM) — V1 Scope

## Product
Peak Logistics Movement (PLM) — Marketplace platform connecting cargo suppliers with transportation shippers.

## V1 Features (6-week timeline: Feb 17 - Mar 28, 2026)

### Core User Flows

| # | Feature | Description | Estimate |
|---|---------|-------------|----------|
| 1 | **User Sign-Up** | Suppliers and shippers can create accounts with email, password, company name, role selection | 2 days |
| 2 | **User Login** | Authentication system with sessions, logout, basic auth guards | 2 days |
| 3 | **Supplier: Post Shipment** | Suppliers can create shipment requests (origin, destination, cargo type, weight, desired pickup date) | 4 days |
| 4 | **Shipper: Post Trip** | Shippers can create available trips (route, available capacity, pricing, departure date) | 4 days |
| 5 | **Supplier: Browse & Reserve** | Suppliers can view available trips matching their shipment needs and confirm reservation | 5 days |

### Technical Foundation

| Component | Description | Estimate |
|-----------|-------------|----------|
| **Database Schema** | Core entities: Users, Suppliers, Shippers, Containers, Trips, Reservations | 3 days |
| **REST API** | FastAPI endpoints for all CRUD operations + authentication | Included in features |
| **Web UI** | React responsive web app (desktop + tablet) | Included in features |
| **Deployment** | Production environment setup (hosting, SSL, CI/CD pipeline) | 3 days |

### Testing & QA

- **Unit tests** - Backend API endpoints
- **Integration tests** - Key user flows (sign-up → post → reserve)
- **Manual QA** - Full user journey testing by team

## Technical Requirements

**Backend:**
- Python 3.11+
- FastAPI framework
- PostgreSQL database
- JWT or session-based authentication
- RESTful API design

**Frontend:**
- React 18+
- Responsive design (desktop + tablet)
- Form validation
- API integration

**DevOps:**
- Production hosting environment
- SSL/TLS enabled
- Automated deployment pipeline
- Database migrations

## Out of Scope (V2+)

**Not in V1:**
- Payment processing
- Real-time shipment tracking
- Mobile native apps
- Email/SMS notifications
- Multi-leg routing
- Advanced search/filtering
- Admin dashboard
- Shipper ratings/reviews

## Dependencies & Assumptions

**Assumptions:**
- Loka provides full-stack team (backend, frontend, design)
- PeakLogistics team available for weekly sync and design review
- Hosting environment decision made by week 1
- No third-party API integrations required for V1

**External Dependencies:**
- Design assets from Loka design team (Week 1)
- Hosting account provisioning (Week 1)
- Domain/SSL certificate setup (Week 1-2)

## Success Metrics (Post-Launch)

- 5+ suppliers successfully post shipments
- 3+ shippers successfully post trips
- 10+ reservations confirmed
- < 5 critical bugs in first 2 weeks
- 80%+ user satisfaction (post-launch survey)
