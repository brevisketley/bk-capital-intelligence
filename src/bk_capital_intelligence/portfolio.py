from dataclasses import dataclass

from .models import Opportunity
from .risk_engine import assess


@dataclass(frozen=True)
class Allocation:
    opportunity_id: str
    weight: float


def construct_risk_adjusted_portfolio(
    opportunities: list[Opportunity],
    max_single_weight: float = 0.35,
    minimum_score: float = 55.0,
) -> list[Allocation]:
    candidates = []
    for opportunity in opportunities:
        assessment = assess(opportunity)
        if not assessment.blocked and assessment.score >= minimum_score:
            value = max(0.0, opportunity.net_apy) * assessment.score / 100.0
            candidates.append((opportunity, value))

    if not candidates:
        return []

    total = sum(value for _, value in candidates)
    raw = [(opportunity, value / total) for opportunity, value in candidates]

    capped = [(opportunity, min(weight, max_single_weight)) for opportunity, weight in raw]
    allocated = sum(weight for _, weight in capped)
    if allocated == 0:
        return []

    # Normalize only after the individual cap. This is a research allocator, not an execution policy.
    return [Allocation(opportunity_id=o.opportunity_id, weight=round(w / allocated, 8)) for o, w in capped]
