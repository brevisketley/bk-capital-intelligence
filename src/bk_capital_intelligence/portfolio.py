from dataclasses import dataclass

from .models import Opportunity
from .risk_engine import assess


@dataclass(frozen=True)
class Allocation:
    opportunity_id: str
    weight: float


def _capped_pro_rata(values: list[tuple[str, float]], cap: float) -> list[Allocation]:
    """Allocate to weights summing to 1 while respecting a hard per-name cap."""
    if not values or cap <= 0:
        return []
    remaining = {key: max(0.0, value) for key, value in values}
    result: dict[str, float] = {}
    open_keys = set(remaining)
    while open_keys:
        total = sum(remaining[key] for key in open_keys)
        if total <= 0:
            break
        room = 1.0 - sum(result.values())
        changed = False
        for key in list(open_keys):
            proposed = room * remaining[key] / total
            if proposed >= cap:
                result[key] = cap
                open_keys.remove(key)
                changed = True
        if not changed:
            for key in open_keys:
                result[key] = room * remaining[key] / total
            break
    return [Allocation(opportunity_id=key, weight=round(weight, 8)) for key, weight in result.items() if weight > 0]


def construct_risk_adjusted_portfolio(
    opportunities: list[Opportunity],
    max_single_weight: float = 0.35,
    minimum_score: float = 55.0,
) -> list[Allocation]:
    """Research allocator; deterministic and never exceeds max_single_weight."""
    if not 0 < max_single_weight <= 1:
        raise ValueError("max_single_weight must be in (0, 1]")
    candidates = []
    for opportunity in opportunities:
        assessment = assess(opportunity)
        if not assessment.blocked and assessment.score >= minimum_score:
            value = max(0.0, opportunity.net_apy) * assessment.score / 100.0
            candidates.append((opportunity.opportunity_id, value))
    return _capped_pro_rata(candidates, max_single_weight)
