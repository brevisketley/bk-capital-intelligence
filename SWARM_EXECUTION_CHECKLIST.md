# BK CAPITAL INTELLIGENCE — SWARM EXECUTION CONTROL BOARD

Mission: reach a working, evidence-backed, non-custodial capital-intelligence MVP without stopping at documentation.

## Operating rule
Each agent owns a deliverable, a measurable acceptance test, and a remediation loop. A task is not DONE because code exists. It is DONE only when the acceptance test passes and an independent re-check confirms the expected behaviour. If it fails: diagnose → fix → retest → repeat.

## Agent lanes

### A1 DATA ENGINE — LIVE + POINT-IN-TIME DATA
Goal: reliable opportunity snapshots with timestamps, provenance, deduplication and schema validation.
Acceptance: collector succeeds; malformed records are rejected; snapshots are immutable; timestamp is source/collection time, not filesystem mtime; repeated collection is deterministic.
Next: backfill/collect enough point-in-time observations for validation.

### A2 YIELD ENGINE — NET ECONOMICS
Goal: calculate comparable net yield from base/reward yield, fees, lockups and known costs.
Acceptance: reward-only/incentive-heavy opportunities are flagged; missing values cannot silently become attractive yield; calculations have unit tests and explainability output.

### A3 RISK ENGINE — DETERMINISTIC SAFETY
Goal: score contract, protocol, asset, oracle, governance, liquidity, counterparty, chain, concentration and sustainability risks.
Acceptance: hard vetoes work; score is reproducible; no LLM can bypass policy.

### A4 PORTFOLIO ENGINE — CONSTRUCTION
Goal: construct diversified allocations subject to explicit risk/liquidity/exposure constraints.
Acceptance: allocations sum correctly; every constraint is enforced; zero/empty investable universe fails closed.

### A5 HISTORICAL VALIDATION — OUT-OF-SAMPLE PROOF
Goal: prove or disprove BK allocation against highest-APY and equal-weight baselines using genuine point-in-time observations.
Acceptance: no hindsight leakage; paired periods; sufficient sample gate; metrics include return proxy, volatility, drawdown, concentration and failure events; result can be PASS, FAIL or INSUFFICIENT_DATA.

### A6 ADVERSARIAL RED TEAM — ATTACK THE SYSTEM
Goal: actively find reasons a proposed allocation should fail.
Acceptance: attacks extreme APY, liquidity, concentration, source quality, protocol/asset risk, stale data and model uncertainty; failed review triggers remediation.

### A7 CRITIC / RESEARCH — INDEPENDENT EVIDENCE
Goal: independently challenge protocol claims and evidence quality.
Acceptance: every material recommendation has source/provenance; conflicting evidence lowers confidence or blocks the opportunity.

### A8 GUARDIAN — FINAL POLICY GATE
Goal: deterministic final approval/rejection.
Acceptance: Guardian cannot be bypassed by agent output; any critical veto blocks paper allocation.

### A9 FEEDBACK / LEARNING LOOP
Goal: feed forward outcomes back into risk/yield/portfolio evaluation.
Acceptance: every decision has a decision_id, evidence, model/version, policy result and later outcome; errors create regression tests.

### A10 PRODUCT / API / DASHBOARD
Goal: expose the working intelligence system to a user through a clean dashboard/API.
Acceptance: live data, ranking rationale, risk score, portfolio proposal, critic findings, Guardian result and audit trail are visible.

### A11 SECURITY / OPERATIONS
Goal: production-grade boundaries and monitoring before any capital execution.
Acceptance: no secrets in repo, least-privilege deployment, health checks, logging, failure-safe behaviour and explicit execution gate.

## Dependency order
1. Data Engine
2. Yield Engine
3. Risk Engine
4. Portfolio Engine
5. Adversarial + Critic
6. Guardian
7. Historical Validation
8. Feedback Loop
9. Product/API/Dashboard
10. Security/Operations
11. Only after all gates: controlled non-custodial execution research

## Definition of mission completion
The MVP is COMPLETE only when a user can view a current opportunity universe, see explainable net-yield/risk rankings, generate a paper portfolio, inspect adversarial criticism and Guardian decision, and see historical/out-of-sample benchmark evidence. The system must remain non-custodial and must not claim guaranteed returns.

## Status protocol
The system should report exact blockers. Never report DONE when the acceptance test is not met. Never manufacture historical observations. Never modify repositories/services outside this project boundary.
