"""Progressive specialist-agent feedback loop for Capital Intelligence.

The agents are intentionally deterministic in the MVP. Each specialist receives the
same opportunity/risk/portfolio context, produces an independent finding, and may
veto or request revision. The orchestrator repeats the review until consensus or a
hard stop is reached. This makes the swarm auditable before introducing external
LLM providers.
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
    passed: bool
    vetoed: bool


@dataclass(frozen=True)
class ProgressiveReview:
    iterations: tuple[SwarmIteration, ...]
    final_decision: str


Agent = Callable[[list[Opportunity], list[RiskAssessment], dict[str, float]], AgentFinding]


def _research(opps: list[Opportunity], risks: list[RiskAssessment], weights: dict[str, float]) -> AgentFinding:
    weak = [o.opportunity_id for o in opps if o.confidence < 0.60]
    if weak:
        return AgentFinding("research", "REVISE", "WARNING", (f"low source confidence: {','.join(weak[:5])}",))
    return AgentFinding("research", "PASS", "INFO", ("source confidence acceptable",))


def _risk(opps: list[Opportunity], risks: list[RiskAssessment], weights: dict[str, float]) -> AgentFinding:
    hard = [r.opportunity_id for r in risks if r.overall_risk >= 80]
    if hard:
        return AgentFinding("risk", "VETO", "CRITICAL", (f"high-risk opportunities present: {','.join(hard[:5])}",))
    return AgentFinding("risk", "PASS", "INFO", ("no critical risk score breach",))


def _liquidity(opps: list[Opportunity], risks: list[RiskAssessment], weights: dict[str, float]) -> AgentFinding:
    concentrated = [k for k, w in weights.items() if w > 0.40]
    if concentrated:
        return AgentFinding("liquidity", "REVISE", "WARNING", (f"position concentration requires review: {','.join(concentrated[:5])}",))
    return AgentFinding("liquidity", "PASS", "INFO", ("allocation concentration within review threshold",))


def _sustainability(opps: list[Opportunity], risks: list[RiskAssessment], weights: dict[str, float]) -> AgentFinding:
    suspicious = [o.opportunity_id for o in opps if o.gross_apy > 100 and o.apy_reward > o.apy_base]
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


def progressive_review(
    opportunities: list[Opportunity],
    risks: list[RiskAssessment],
    weights: dict[str, float],
    *,
    agents: Iterable[Agent] = DEFAULT_AGENTS,
    max_iterations: int = 3,
) -> ProgressiveReview:
    """Run specialist feedback repeatedly until PASS or a hard VETO.

    REVISE findings are retained as feedback for the next iteration. The MVP does
    not silently change capital allocations inside the critic: the caller must
    explicitly recompute the portfolio between iterations. This prevents an agent
    from both proposing and approving its own remediation.
    """
    history: list[SwarmIteration] = []
    current = list(agents)
    for iteration in range(1, max_iterations + 1):
        findings = tuple(agent(opportunities, risks, weights) for agent in current)
        vetoed = any(f.decision == "VETO" for f in findings)
        passed = not vetoed and all(f.decision == "PASS" for f in findings)
        history.append(SwarmIteration(iteration, findings, passed, vetoed))
        if passed or vetoed:
            break
    final = "VETO" if history[-1].vetoed else "PASS" if history[-1].passed else "REVISE"
    return ProgressiveReview(tuple(history), final)
