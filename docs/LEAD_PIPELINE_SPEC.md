# Lead Pipeline Specification

This is infrastructure for the future self-running growth system. It does not authorize indiscriminate scraping or spam.

## Pipeline
1. Ingest permitted lead source.
2. Normalize identity/company/contact fields.
3. Deduplicate.
4. Validate source, freshness and contactability.
5. Enrich only from permitted sources.
6. Score ICP fit.
7. Score intent where evidence exists.
8. Apply suppression, opt-out and compliance rules.
9. Assign segment and next-best action.
10. Queue compliant outreach.
11. Record send/delivery/response.
12. Classify response.
13. Schedule permitted follow-up or stop.
14. Route qualified opportunity to conversion workflow.
15. Record conversion and customer value.
16. Feed results into campaign analytics.

## Required data
lead_id, source, source_timestamp, identity_confidence, company, role, geography, segment, fit_score, intent_score, qualification_state, contactability_state, suppression_state, consent/basis where applicable, campaign_id, touch_count, last_touch, response_state, opportunity_value, lifecycle_state, created_at, updated_at.

## Hard controls
- Deduplication before outreach.
- Suppression before every contact attempt.
- Opt-out immediately terminates outreach.
- No unsupported financial/performance claims.
- Evidence IDs attached to material claims.
- Rate limits and provider policies enforced.
- Human escalation for ambiguous regulatory/safety cases.
- Full audit trail.

## Dashboard views
- New leads
- Vetting queue
- Qualified leads
- Contact queue
- Contacted / awaiting response
- Engaged
- Opportunities
- Converted
- Disqualified
- Suppressed / opted out
- Funnel conversion
- Revenue attribution
- Campaign performance

## Completion test
A lead system is not complete until a synthetic lead can traverse the state machine end-to-end, including invalid/duplicate/opt-out paths, with every state visible in Mission Control and every transition persisted in the audit log.
