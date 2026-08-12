# BK Capital Intelligence — Swarm Control Board

## Active specialist agents

| Agent | Mission | Output | Gate |
|---|---|---|---|
| Research | provenance, source quality, opportunity facts | evidence findings | no unknown/weak evidence in allocated capital |
| Yield | APY/base/reward/net-yield decomposition | normalized yield | headline APY never used alone |
| Risk | protocol, contract, oracle, asset, governance, liquidity, counterparty and chain risk | 0–100 quality score | hard risk veto |
| Portfolio | risk-adjusted allocation and diversification | candidate weights | hard caps |
| Sustainability | incentive dependence, extreme APY, yield persistence | revision/veto findings | remove unsustainable allocation |
| Liquidity | exit depth, lockups and concentration | revision findings | concentration remediation |
| Red Team | attacks the whole decision for hidden failure modes | adversarial review | fail closed |
| Guardian | deterministic policy enforcement | APPROVE/REJECT | final authority before any execution |
| Auditor | decision evidence, model/version, source timestamp and outcome | immutable audit record | no untraceable decisions |

## Progressive loop

`Research → Yield → Risk → Portfolio → Sustainability/Liquidity → Red Team → remediation → re-review → Guardian → outcome → attribution → feedback`

A REVISE finding must produce a deterministic remediation before re-review. A VETO terminates the decision path. No agent has transaction authority.

## Historical-validation gate

The system distinguishes three states:

1. `INSUFFICIENT_DATA` — not enough paired point-in-time periods.
2. `NOT_ELIGIBLE_CONDITIONAL_DATASET` — replay is useful for engineering, but current-universe backfill has survivorship bias.
3. `PASS` / `FAIL` — only after enough point-in-time paired periods are available and the benchmark comparison is out-of-sample.

Current research replay is an APY-implied proxy, not realized P&L. Token price movement, gas, slippage, depegs and other path-dependent effects must be added before production capital decisions.

## Completion definition

The intelligence MVP is not complete until:
- specialist feedback is integrated into every decision;
- adversarial review can veto the Guardian;
- snapshot collection is automated;
- historical validation is reproducible and auditable;
- the model has sufficient point-in-time data for a legitimate benchmark;
- the dashboard/API exposes evidence, risk, allocation, decision and validation state;
- all tests are green;
- no user funds or custody are involved until separate security/legal gates pass.
