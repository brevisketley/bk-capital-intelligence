"""Adversarial review layer for allocation decisions.

The critic swarm deliberately attacks a proposed portfolio before the Guardian can
approve it. It is deterministic in v0 so every objection is reproducible and testable.
No critic has transaction authority.
"""
from __future__ import annotations
from dataclasses import dataclass
from .models import Opportunity, RiskAssessment

@dataclass(frozen=True)
class Critique:
    agent: str
    severity: str
    passed: bool
    findings: tuple[str, ...]

@dataclass(frozen=True)
class AdversarialReview:
    passed: bool
    critiques: tuple[Critique, ...]
    required_actions: tuple[str, ...]

def _research_critic(o: Opportunity) -> Critique:
    findings = []
    if o.confidence < 0.60: findings.append("evidence confidence below 0.60")
    if not o.source or o.source == "unknown": findings.append("source provenance is missing")
    if o.base_apy is not None and o.reward_apy is not None and o.gross_apy > 0:
        if max(0.0, o.reward_apy) / o.gross_apy > 0.80:
            findings.append("yield is dominated by rewards/incentives")
    return Critique("research", "high" if findings else "info", not findings, tuple(findings))

def _liquidity_critic(o: Opportunity) -> Critique:
    findings = []
    if o.liquidity_usd <= 0: findings.append("no usable liquidity reported")
    elif o.tvl_usd > 0 and o.liquidity_ratio < 0.05: findings.append("liquidity is less than 5% of TVL")
    if o.lockup_days > 30: findings.append("exit is materially constrained by lockup")
    return Critique("liquidity", "high" if findings else "info", not findings, tuple(findings))

def _risk_critic(o: Opportunity, risk: RiskAssessment) -> Critique:
    findings = []
    if risk.blocked: findings.append("risk engine has already blocked the opportunity")
    if risk.score < 45.0: findings.append(f"risk score {risk.score:.3f} is below minimum quality")
    if o.leverage > 1.5: findings.append("leverage exceeds conservative review threshold")
    severity = "critical" if risk.blocked else ("high" if findings else "info")
    return Critique("risk", severity, not findings, tuple(findings))

def _concentration_critic(opportunities: list[Opportunity], weights: dict[str, float]) -> Critique:
    findings = []
    by_protocol: dict[str, float] = {}
    by_chain: dict[str, float] = {}
    for o in opportunities:
        w = max(0.0, weights.get(o.opportunity_id, 0.0))
        by_protocol[o.protocol] = by_protocol.get(o.protocol, 0.0) + w
        by_chain[o.chain] = by_chain.get(o.chain, 0.0) + w
    if max(by_protocol.values(), default=0.0) > 0.40: findings.append("protocol concentration exceeds 40%")
    if max(by_chain.values(), default=0.0) > 0.60: findings.append("chain concentration exceeds 60%")
    return Critique("concentration", "high" if findings else "info", not findings, tuple(findings))

def review(opportunities: list[Opportunity], risks: list[RiskAssessment], weights: dict[str, float]) -> AdversarialReview:
    """Run independent critics and fail closed on any finding."""
    risk_by_id = {r.opportunity_id: r for r in risks}
    critiques = []
    for o in opportunities:
        critiques.extend((_research_critic(o), _liquidity_critic(o), _risk_critic(o, risk_by_id[o.opportunity_id])))
    critiques.append(_concentration_critic(opportunities, weights))
    actions = tuple(f"{c.agent}: {finding}" for c in critiques if not c.passed for finding in c.findings)
    return AdversarialReview(not actions, tuple(critiques), actions)
