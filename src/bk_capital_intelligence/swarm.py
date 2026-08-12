"""Auditable multi-agent capital-allocation decision pipeline."""
from __future__ import annotations
from dataclasses import dataclass
from .adversarial import AdversarialReview, review as adversarial_review
from .agent_feedback import ProgressiveReview, progressive_review
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
    progressive: ProgressiveReview
    adversarial: AdversarialReview


def _allocations_from_weights(weights: dict[str, float]) -> tuple[Allocation, ...]:
    return tuple(Allocation(k, round(v, 8)) for k, v in sorted(weights.items()) if v > 0)


def run(opportunities: list[Opportunity], policy: GuardianPolicy = GuardianPolicy()) -> SwarmResult:
    """Run Research → Risk → Portfolio → Progressive Swarm → Red Team → Guardian."""
    findings = tuple(
        ResearchFinding(
            o.opportunity_id,
            o.confidence,
            (f"source={o.source}", f"apy={o.gross_apy:.6f}", f"tvl_usd={o.tvl_usd:.2f}"),
        )
        for o in opportunities
    )
    risks = tuple(assess(o) for o in opportunities)
    initial_allocations = tuple(construct_risk_adjusted_portfolio(opportunities))
    initial_weights = {a.opportunity_id: a.weight for a in initial_allocations}

    progressive = progressive_review(opportunities, list(risks), initial_weights)
    final_weights = dict(progressive.final_weights)
    allocations = _allocations_from_weights(final_weights)

    adversarial = adversarial_review(opportunities, list(risks), final_weights)
    guardian = tuple(evaluate(o, policy, final_weights.get(o.opportunity_id, 0.0)) for o in opportunities)

    if progressive.final_decision != "PASS" or not adversarial.passed:
        reason = "progressive swarm did not pass" if progressive.final_decision != "PASS" else "adversarial review failed"
        guardian = tuple(
            PolicyDecision(g.opportunity_id, False, tuple(list(g.reasons) + [reason]), g.risk)
            for g in guardian
        )
    return SwarmResult(allocations, risks, guardian, findings, progressive, adversarial)
