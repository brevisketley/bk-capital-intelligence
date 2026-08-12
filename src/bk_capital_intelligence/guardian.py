"""Deterministic Guardian policy layer.

The Guardian is intentionally separate from the AI/research layer. Model output cannot
bypass these controls. It returns policy decisions; it never signs transactions.
"""
from __future__ import annotations

from dataclasses import dataclass

from .models import Opportunity, RiskAssessment
from .risk_engine import assess


@dataclass(frozen=True)
class GuardianPolicy:
    min_risk_score: float = 60.0
    min_confidence: float = 0.60
    max_single_exposure: float = 0.35
    max_protocol_exposure: float = 0.50
    max_chain_exposure: float = 0.60
    max_sustainability_risk: float = 0.75
    blocked_protocols: tuple[str, ...] = ()
    blocked_chains: tuple[str, ...] = ()


@dataclass(frozen=True)
class PolicyDecision:
    opportunity_id: str
    approved: bool
    reasons: tuple[str, ...]
    risk: RiskAssessment


def evaluate(opportunity: Opportunity, policy: GuardianPolicy = GuardianPolicy(), proposed_weight: float = 0.0) -> PolicyDecision:
    risk = assess(opportunity)
    reasons = list(risk.reasons)
    if risk.blocked:
        reasons.append("risk engine blocked opportunity")
    if risk.score < policy.min_risk_score:
        reasons.append("risk score below Guardian minimum")
    if opportunity.confidence < policy.min_confidence:
        reasons.append("evidence confidence below Guardian minimum")
    if opportunity.sustainability_risk > policy.max_sustainability_risk:
        reasons.append("sustainability risk above Guardian maximum")
    if proposed_weight > policy.max_single_exposure:
        reasons.append("proposed single-opportunity exposure exceeds policy")
    if opportunity.protocol.lower() in {p.lower() for p in policy.blocked_protocols}:
        reasons.append("protocol is explicitly blocked")
    if opportunity.chain.lower() in {c.lower() for c in policy.blocked_chains}:
        reasons.append("chain is explicitly blocked")
    return PolicyDecision(opportunity.opportunity_id, not reasons, tuple(reasons), risk)
