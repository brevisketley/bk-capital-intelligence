"""Authoritative source map used by the ingestion layer.

The system keeps source roles explicit so a single vendor cannot silently become
both the data source and the risk authority.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class SourceSpec:
    name: str
    role: str
    endpoint: str
    historical: bool
    notes: str


SOURCES = (
    SourceSpec(
        name="DeFiLlama",
        role="cross-protocol discovery",
        endpoint="https://yields.llama.fi/pools",
        historical=True,
        notes="Broad discovery feed; requires protocol-level enrichment before capital decisions.",
    ),
    SourceSpec(
        name="Morpho",
        role="market and vault primary data",
        endpoint="https://api.morpho.org/graphql",
        historical=True,
        notes="Official API exposes markets, vaults, APYs, TVL, utilization, rewards and historical time series.",
    ),
    SourceSpec(
        name="Pendle",
        role="fixed-yield market primary data",
        endpoint="https://api-v2.pendle.finance/core/v2/markets/all",
        historical=False,
        notes="Official API exposes market data; APY methodology is documented by Pendle.",
    ),
)


def source_map() -> dict[str, SourceSpec]:
    return {source.name: source for source in SOURCES}
