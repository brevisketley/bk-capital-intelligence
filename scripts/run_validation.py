"""Run conditional historical replay and emit an honest validation report."""
from __future__ import annotations

import json
from pathlib import Path

from bk_capital_intelligence.replay import replay
from bk_capital_intelligence.validation import validate_period_returns

ROOT = Path(__file__).resolve().parents[1]
HISTORY = ROOT / "data" / "historical"
REPORTS = ROOT / "data" / "validation"


def latest_dataset() -> Path:
    files = sorted(HISTORY.glob("conditional-*.json"))
    if not files:
        raise FileNotFoundError("no conditional historical dataset exists")
    return files[-1]


def main() -> None:
    dataset = latest_dataset()
    document = json.loads(dataset.read_text(encoding="utf-8"))
    result = replay(document["series"])
    report = {
        "dataset": dataset.name,
        "dataset_type": document["dataset_type"],
        "survivorship_bias_warning": document["survivorship_bias_warning"],
        "observations": result.observations,
        "performance": {
            "bk_risk_adjusted": result.bk.__dict__,
            "highest_apy": result.highest_apy.__dict__,
            "equal_weight": result.equal_weight.__dict__,
        },
        "validation": "NOT_ELIGIBLE_CONDITIONAL_DATASET",
        "reason": "Current-universe backfill is useful for engine testing but is not a valid unbiased portfolio-performance claim.",
    }
    REPORTS.mkdir(parents=True, exist_ok=True)
    path = REPORTS / f"report-{dataset.stem}.json"
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(path)


if __name__ == "__main__":
    main()
