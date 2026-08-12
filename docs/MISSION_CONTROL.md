# BK Capital Intelligence — Mission Control

Mission Control is the authoritative project-progress contract. It is intentionally deterministic: a gate is GREEN only when its acceptance criteria are verified by code, tests, deployment state, or an explicit evidence artifact.

## Swarm board

| Agent | Mission | Completion gate | Status |
|---|---|---|---|
| A1 Data | Live + point-in-time opportunity data | Immutable snapshots with provenance, timestamp integrity, validation | GREEN/YELLOW via automated report |
| A2 Yield | Net economics | Comparable yield decomposition and stale/invalid-data rejection | GREEN/YELLOW via tests |
| A3 Risk | Deterministic risk | Reproducible scores, hard overrides, explainable output | GREEN |
| A4 Portfolio | Allocation | Position/protocol/chain caps and cash handling enforced | GREEN |
| A5 Validation | Historical proof | Genuine paired OOS periods; no hindsight/survivorship leakage | YELLOW until data sufficiency |
| A6 Red Team | Adversarial review | Failed assumptions trigger remediation and re-review | GREEN |
| A7 Research | Evidence | Source provenance, conflicts, freshness and confidence recorded | YELLOW |
| A8 Guardian | Final policy | Fail-closed, deterministic, non-bypassable | GREEN |
| A9 Feedback | Learning loop | Decision → outcome → attribution → regression/recalibration | YELLOW |
| A10 Product | Mission Control/API/UI | User can inspect current gates, evidence, blockers and next action | BUILDING |
| A11 Security | Production controls | Secret isolation, dependency checks, fail-safe deployment | YELLOW |

## Dependency order

DATA → YIELD → RISK → PORTFOLIO → CRITICS → GUARDIAN → VALIDATION → FEEDBACK → PRODUCT → SECURITY → controlled execution.

Independent lanes may proceed in parallel. A downstream gate may not be marked complete because an upstream gate is incomplete.

## Mandatory loop for every agent

1. Build.
2. Run tests.
3. Inspect the result against acceptance criteria.
4. If failed: identify root cause, remediate, retest.
5. Repeat until the gate passes or an external dependency is explicitly recorded.
6. Record evidence.
7. Only then hand off to the next lane.

## Non-negotiable safety gates

- No user funds.
- No custody.
- No token launch.
- No profit guarantees.
- No autonomous capital movement before security, legal and risk approval.

## Current mission objective

Reach a working, tested, observable MVP that can ingest real opportunities, produce risk-adjusted allocations, adversarially challenge those allocations, simulate point-in-time decisions, compare against benchmark strategies, learn from forward outcomes, and expose the complete state through Mission Control.

## Completion definition

The mission is NOT complete merely because code exists. Completion requires all required gates GREEN, a working deployed product, passing tests, validated OOS evidence, documented audit trail, and production/security gates passed for the intended operating model.
