# PeakLogistics RouteRunner — Risk Register

## Active Risks

### RISK-001: Delivery Zones Delay Impacts V2 Launch
- **Probability**: Medium
- **Impact**: High
- **Status**: Open
- **Description**: Delivery Zones is the last major V2 feature still in Shaping. PeakLogistics is debating zone boundary logic (geo-fencing vs postal codes vs custom polygons). Extended deliberation could push implementation past Q1.
- **Mitigation**: Other V2 features progressing in parallel. Can launch V2 without Zones.
- **Owner**: Marcus/Priya (PL) to finalize zone logic

### RISK-002: Fleet Analytics Data Pipeline Dependency
- **Probability**: Low
- **Impact**: Medium
- **Status**: Monitoring
- **Description**: Fleet Analytics depends on telemetry data pipeline being built as part of Dynamic Re-routing. If re-routing work runs long, analytics design may outpace the data layer.
- **Mitigation**: Alex prioritizing shared data pipeline early in Sprint 42.
- **Owner**: Alex + Bruno

### RISK-003: API Auth v2 Must Ship Before ETA Notifications
- **Probability**: Low
- **Impact**: High
- **Status**: Tracking
- **Description**: Customer ETA Notifications will use the public API. Auth v2 with rate limiting must be live first — can't expose customer-facing endpoints on legacy auth.
- **Mitigation**: API auth v2 in active development, on track for Sprint 43.
- **Owner**: Alex
