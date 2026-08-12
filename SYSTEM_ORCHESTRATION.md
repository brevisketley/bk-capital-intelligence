# BK Capital Intelligence — Autonomous System Orchestration

## Mission
Build the complete ecosystem before pursuing live lead acquisition. Leads may be stored/displayed when available, but the platform must first be capable of vetting, routing, contacting, tracking, converting and learning from leads without this chat acting as the operator.

## Operating sequence

### Gate 0 — Foundation
Repository isolation, environments, secrets, database, queues, scheduler, observability, CI/CD, health checks.

### Gate 1 — Intelligence
Discovery → provenance → economics → research → risk → portfolio → adversarial swarm → Guardian.

### Gate 2 — Evidence
Historical replay → point-in-time integrity → benchmark comparison → OOS validation → decision ledger.

### Gate 3 — Learning
Forward outcomes → attribution → drift → agent scoring → regression generation → validated recalibration.

### Gate 4 — Product
Mission Control → public site → customer auth → plans → billing → entitlements → customer dashboard → alerts/reports.

### Gate 5 — Growth machine
Strategy → content generation → evidence/claims gate → approval → publishing → attribution → lead capture → enrichment → scoring → segmentation → outreach → response handling → qualification → booking/demo → conversion → onboarding.

### Gate 6 — Retention and revenue loop
Usage events → value delivery → digest/alerts → engagement scoring → churn detection → win-back/referral → revenue analytics → campaign experimentation → product feedback.

### Gate 7 — Autonomous lead operations
Only after Gates 0–6 are operational: continuously discover permitted lead sources, ingest leads, deduplicate, enrich, vet, score, suppress invalid/unwanted contacts, route by segment, contact using compliant channels, record every interaction, follow up according to policy, stop on opt-out, escalate exceptions, and feed results into analytics.

## Lead-state machine
DISCOVERED → ENRICHING → VETTED → QUALIFIED → CONTACT_QUEUED → CONTACTED → ENGAGED → QUALIFIED_OPPORTUNITY → CONVERTED → ONBOARDED → RETAINED.

Negative states: INVALID, DUPLICATE, DISQUALIFIED, SUPPRESSED, OPTED_OUT, BOUNCED, ESCALATED.

No lead may skip vetting. No outreach may bypass suppression/opt-out checks. Financial or regulated claims require the claims gate before publication/outreach.

## Swarm roles
- Data: source integrity, dedupe, freshness.
- Research: evidence and market intelligence.
- Yield: economics.
- Risk: exposure and failure modes.
- Portfolio: allocation.
- Red Team: adversarial challenge.
- Guardian: fail-closed decision policy.
- Validation: OOS historical evidence.
- Feedback: outcome attribution and recalibration.
- Product: customer experience.
- Growth: ICP, offers, campaigns.
- Content: research-to-content pipeline.
- Compliance: claims, permissions, suppression and regulatory controls.
- CRM: lead lifecycle and outreach.
- Analytics: funnel/revenue attribution.
- Security: secrets, access, abuse prevention and incident response.

## Mandatory agent loop
FOR EACH OPEN CHECKLIST ITEM:
1. Inspect existing implementation and dependency state.
2. Implement the smallest production-ready increment.
3. Run unit/integration/e2e tests.
4. Attack the result with negative/adversarial cases.
5. Fix every discovered defect.
6. Rerun tests and health checks.
7. Record evidence and status.
8. Re-scan the master checklist from item 1.
9. Continue to the next open item.

A task cannot become GREEN because code exists. GREEN requires executable evidence.

## Re-entry rule
After every completed item, the coordinator returns to the beginning of MASTER_MISSION_CHECKLIST.md and selects the highest-priority unresolved dependency. This prevents late-stage work from hiding unfinished foundational work.

## Blind-site rule
ChatGPT is not the lead operator. The deployed system must perform the recurring workflow through scheduled jobs/queues and expose state in Mission Control. ChatGPT is used for engineering, review, exception handling and strategic decisions, not as the production lead-processing worker.

## Safety
No autonomous custody, capital movement, token issuance or guaranteed-return claims. Outreach must comply with applicable privacy, anti-spam, platform and local regulatory requirements. Regulated financial activity requires legal/regulatory review before activation.

## Definition of done
The system is done only when all mandatory checklist gates are GREEN, production workflows are observable, failures automatically enter remediation queues, the marketing/sales lifecycle operates without manual chat intervention, and the system can continuously measure and improve itself.
