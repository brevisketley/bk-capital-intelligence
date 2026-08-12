"""Progressive specialist-agent feedback loop for Capital Intelligence.

The MVP agents are deterministic and auditable. Each specialist independently
reviews the same decision context. REVISE findings trigger a deterministic
remediation, then the swarm reviews the remediated portfolio again. VETO findings
fail closed and cannot be overridden by another agent.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable

from .models import Opportunity, RiskAssessment


@dataclass(frozen=True)
class AgentFinding:
    agent: str
    decision: str  # PASS / REVISE / VETO
    severity: str  # INFO / WARNING / CRITICAL
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class SwarmIteration:
    iteration: int
    findings: tuple[AgentFinding, ...]
    effective_weights: tuple[tuple[str, float], ...]
    passed: bool
    vetoed: bool


@dataclass(frozen=True)
class ProgressiveReview:
    iterations: tuple[SwarmIteration, ...]
    final_decision: str
    final_weights: tuple[tuple[str, float], ...]


Agent = Callable[[list[Opportunity], list[RiskAssessment], dict[str, float]], AgentFinding]


def _research(opps: list[Opportunity], risks: list[RiskAssessment], weights: dict[str, float]) -> AgentFinding:
    weak = [o.opportunity_id for o in opps if o.confidence < 0.60 and weights.get(o.opportunity_id, 0) > 0]
    if weak:
        return AgentFinding("research", "REVISE", "WARNING", (f"low source confidence: {','.join(weak[:5])}",))
    return AgentFinding("research", "PASS", "INFO", ("source confidence acceptable",))


def _risk(opps: list[Opportunity], risks: list[RiskAssessment], weights: dict[str, float]) -> AgentFinding:
    hard = [r.opportunity_id for r in risks if r.score >= 80 and weights.get(r.opportunity_id, 0) > 0]
    if hard:
        return AgentFinding("risk", "VETO", "CRITICAL", (f"high-risk allocated opportunities: {','.join(hard[:5])}",))
    return AgentFinding("risk", "PASS", "INFO", ("no critical risk score breach",))


def _liquidity(opps: list[Opportunity], risks: list[RiskAssessment], weights: dict[str, float]) -> AgentFinding:
    concentrated = [k for k, w in weights.items() if w > 0.40]
    if concentrated:
        return AgentFinding("liquidity", "REVISE", "WARNING", (f"position concentration requires review: {','.join(concentrated[:5])}",))
    return AgentFinding("liquidity", "PASS", "INFO", ("allocation concentration within review threshold",))


def _sustainability(opps: list[Opportunity], risks: list[RiskAssessment], weights: dict[str, float]) -> AgentFinding:
    suspicious = [o.opportunity_id for o in opps if o.gross_apy > 100 and (o.reward_apy or 0) > (o.base_apy or 0) and weights.get(o.opportunity_id, 0) > 0]
    if suspicious:
        return AgentFinding("sustainability", "REVISE", "WARNING", (f"incentive-dominant headline yield: {','.join(suspicious[:5])}",))
    return AgentFinding("sustainability", "PASS", "INFO", ("no extreme incentive-dominant yield detected",))


def _red_team(opps: list[Opportunity], risks: list[RiskAssessment], weights: dict[str, float]) -> AgentFinding:
    if not opps:
        return AgentFinding("red_team", "VETO", "CRITICAL", ("empty opportunity universe",))
    if sum(weights.values()) <= 0:
        return AgentFinding("red_team", "VETO", "CRITICAL", ("portfolio has no investable allocation",))
    return AgentFinding("red_team", "PASS", "INFO", ("no structural portfolio failure detected",))


DEFAULT_AGENTS: tuple[Agent, ...] = (_research, _risk, _liquidity, _sustainability, _red_team)


def _renormalize(weights: dict[str, float]) -> dict[str, float]:
    total = sum(max(0.0, w) for w in weights.values())
    if total <= 0:
        return {k: 0.0 for k in weights}
    return {k: max(0.0, w) / total for k, w in weights.items()}


def _remediate(findings: tuple[AgentFinding, ...], opportunities: list[Opportunity], weights: dict[str, float]) -> dict[str, float]:
    updated = dict(weights)
    for finding in findings:
        if finding.decision != "REVISE":
            continue
        if finding.agent == "research":
            for o in opportunities:
                if o.confidence < 0.60:
                    updated[o.opportunity_id] = 0.0
        elif finding.agent == "sustainability":
            for o in opportunities:
                if o.gross_apy > 100 and (o.reward_apy or 0) > (o.base_apy or 0):
                    updated[o.opportunity_id] = 0.0
        elif finding.agent == "liquidity":
            for key, weight in list(updated.items()):
                if weight > 0.40:
                    updated[key] = 0.40
    return _renormalize(updated)


def progressive_review(
    opportunities: list[Opportunity],
    risks: list[RiskAssessment],
    weights: dict[str, float],
    *,
    agents: Iterable[Agent] = DEFAULT_AGENTS,
    max_iterations: int = 3,
) -> ProgressiveReview:
    """Run specialist feedback, remediation and re-review until PASS/VETO.

    VETO is fail-closed. REVISE is actionable feedback: the orchestrator applies a
    deterministic remediation and runs the swarm again. The final weight set is
    returned for the caller to feed into the Guardian, creating an auditable
    progressive decision loop rather than a one-shot critic.
    """
    if max_iterations < 1:
        raise ValueError("max_iterations must be >= 1")
    history: list[SwarmIteration] = []
    current_weights = _renormalize(dict(weights))
    agent_list = tuple(agents)
    for iteration in range(1, max_iterations + 1):
        findings = tuple(agent(opportunities, risks, current_weights) for agent in agent_list)
        vetoed = any(f.decision == "VETO" for f in findings)
        passed = not vetoed and all(f.decision == "PASS" for f in findings)
        history.append(SwarmIteration(iteration, findings, tuple(sorted(current_weights.items())), passed, vetoed))
        if passed or vetoed:
            break
        current_weights = _remediate(findings, opportunities, current_weights)
    final = "VETO" if history[-1].vetoed else "PASS" if history[-1].passed else "REVISE"
    return ProgressiveReview(tuple(history), final, tuple(sorted(current_weights.items())))
