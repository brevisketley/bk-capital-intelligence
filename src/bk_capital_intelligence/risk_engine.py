from .models import Opportunity, RiskAssessment


WEIGHTS = {
    "contract": 0.17,
    "protocol": 0.13,
    "asset": 0.11,
    "oracle": 0.08,
    "governance": 0.07,
    "counterparty": 0.11,
    "chain": 0.08,
    "sustainability": 0.13,
    "liquidity": 0.12,
}


def assess(opportunity: Opportunity) -> RiskAssessment:
    reasons: list[str] = []
    blocked = False

    if opportunity.gross_apy < 0:
        reasons.append("negative gross APY")
        blocked = True
    if opportunity.tvl_usd <= 0:
        reasons.append("missing or zero TVL")
        blocked = True
    if opportunity.liquidity_usd <= 0:
        reasons.append("missing or zero exit liquidity")
        blocked = True
    if opportunity.leverage > 3:
        reasons.append("leverage exceeds initial policy ceiling")
        blocked = True
    if opportunity.lockup_days > 90:
        reasons.append("lock-up exceeds initial policy ceiling")

    components = {
        "contract": max(0.0, min(1.0, 1.0 - opportunity.contract_risk)),
        "protocol": max(0.0, min(1.0, 1.0 - opportunity.protocol_risk)),
        "asset": max(0.0, min(1.0, 1.0 - opportunity.asset_risk)),
        "oracle": max(0.0, min(1.0, 1.0 - opportunity.oracle_risk)),
        "governance": max(0.0, min(1.0, 1.0 - opportunity.governance_risk)),
        "counterparty": max(0.0, min(1.0, 1.0 - opportunity.counterparty_risk)),
        "chain": max(0.0, min(1.0, 1.0 - opportunity.chain_risk)),
        "sustainability": max(0.0, min(1.0, 1.0 - opportunity.sustainability_risk)),
        "liquidity": max(0.0, min(1.0, 1.0 - opportunity.liquidity_risk)),
    }

    score = 100.0 * sum(components[key] * weight for key, weight in WEIGHTS.items())

    # Hard overrides prevent attractive yield from masking unacceptable risk.
    if opportunity.contract_risk >= 0.9:
        reasons.append("contract risk exceeds hard threshold")
        blocked = True
    if opportunity.asset_risk >= 0.9:
        reasons.append("asset risk exceeds hard threshold")
        blocked = True
    if opportunity.sustainability_risk >= 0.9:
        reasons.append("yield sustainability risk exceeds hard threshold")
        blocked = True
    if opportunity.liquidity_risk >= 0.9:
        reasons.append("liquidity risk exceeds hard threshold")
        blocked = True

    return RiskAssessment(
        opportunity_id=opportunity.opportunity_id,
        score=round(score, 4),
        blocked=blocked,
        reasons=tuple(reasons),
        components=components,
    )


def risk_adjusted_rank(opportunities: list[Opportunity]) -> list[tuple[Opportunity, RiskAssessment, float]]:
    ranked = []
    for opportunity in opportunities:
        assessment = assess(opportunity)
        yield_factor = max(0.0, opportunity.net_apy)
        score = 0.0 if assessment.blocked else yield_factor * (assessment.score / 100.0)
        ranked.append((opportunity, assessment, round(score, 6)))
    return sorted(ranked, key=lambda item: item[2], reverse=True)
