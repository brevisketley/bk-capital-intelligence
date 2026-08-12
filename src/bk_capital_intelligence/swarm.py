"""Multi-agent decision pipeline with an adversarial review stage."""
from __future__ import annotations

from dataclasses import dataclass

from .adversarial import AdversarialReview, review as adversarial_review
from .guardian import GuardianPolicy, PolicyDecision, evaluate
from .models import Opportunity, RiskAssessment
from .portfolio import Allocation, construct_risk_adjusted_portfolio
from .risk_engine import assess


@dataclass(frozen=True)
class ResearchFinding:
    opportunity_id: str
    evidence_quality: float
    facts: tuple[str, ...]


@dataclass(frozen=True)
class SwarmResult:
    allocations: tuple[Allocation, ...]
    risk: tuple[RiskAssessment, ...]
    guardian: tuple[PolicyDecision, ...]
    findings: tuple[ResearchFinding, ...]
    adversarial: AdversarialReview


def run(opportunities: list[Opportunity], policy: GuardianPolicy = GuardianPolicy()) -> SwarmResult:
    """Run Research → Risk → Portfolio → Adversarial Critic → Guardian.

    The critic can veto the portfolio recommendation, but neither critic nor other
    agents can authorize transactions.
    """
    findings = tuple(
        ResearchFinding(
            opportunity_id=o.opportunity_id,
            evidence_quality=o.confidence,
            facts=(f"source={o.source}", f"apy={o.gross_apy:.6f}", f"tvl_usd={o.tvl_usd:.2f}"),
        )
        for o in opportunities
    )
    risks = tuple(assess(o) for o in opportunities)
    allocations = tuple(construct_risk_adjusted_portfolio(opportunities))
    weights = {a.opportunity_id: a.weight for a in allocations}
    adversarial = adversarial_review(opportunities, list(risks), weights)
    guardian = tuple(evaluate(o, policy, weights.get(o.opportunity_id, 0.0)) for o in opportunities)
    if not adversarial.passed:
        guardian = tuple(
            PolicyDecision(False, tuple(list(g.reasons) + ["adversarial review failed"]))
            for g in guardian
        )
    return SwarmResult(allocations, risks, guardian, findings, adversarial)
