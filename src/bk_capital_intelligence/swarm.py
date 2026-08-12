"""Multi-agent decision pipeline.

This first implementation uses deterministic local agents so the safety architecture
is testable before an LLM provider is introduced. LLMs can later replace individual
reasoning components without gaining authority over the Guardian.
"""
from __future__ import annotations

from dataclasses import dataclass

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


def run(opportunities: list[Opportunity], policy: GuardianPolicy = GuardianPolicy()) -> SwarmResult:
    """Run Research → Risk → Portfolio → Guardian without transaction authority."""
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
    guardian = tuple(evaluate(o, policy, weights.get(o.opportunity_id, 0.0)) for o in opportunities)
    return SwarmResult(allocations, risks, guardian, findings)
