from datetime import datetime, timezone

import pytest

from bk_capital_intelligence.ingestion import IngestionError, normalize_pool, normalize_pools


SAMPLE = {
    "pool": "abc-123",
    "project": "Example Protocol",
    "chain": "Ethereum",
    "symbol": "USDC",
    "apy": 8.5,
    "apyBase": 6.5,
    "apyReward": 2.0,
    "tvlUsd": 2_500_000,
    "poolMeta": "stablecoin lending",
}


def test_normalize_pool_preserves_source_identity_and_net_apy():
    item = normalize_pool(SAMPLE, datetime(2026, 8, 12, tzinfo=timezone.utc))
    assert item.opportunity_id == "defillama:abc-123"
    assert item.protocol == "Example Protocol"
    assert item.asset == "USDC"
    assert item.gross_apy == pytest.approx(0.085)
    assert item.net_apy == pytest.approx(0.085)
    assert item.tvl_usd == pytest.approx(2_500_000)
    assert item.liquidity_risk == pytest.approx(0.20)


def test_legacy_tvl_field_is_still_supported():
    row = {**SAMPLE, "tvlUsd": None, "tvl": 500_000}
    item = normalize_pool(row)
    assert item.tvl_usd == pytest.approx(500_000)
    assert item.liquidity_risk == pytest.approx(0.45)


def test_reward_only_yield_is_marked_high_sustainability_risk():
    row = {**SAMPLE, "apy": 12.0, "apyBase": 0.0, "apyReward": 12.0}
    item = normalize_pool(row)
    assert item.sustainability_risk >= 0.90


def test_missing_identity_is_rejected():
    with pytest.raises(IngestionError):
        normalize_pool({"project": "Example Protocol"})


def test_invalid_rows_are_skipped_without_poisoning_batch():
    payload = {"data": [SAMPLE, {"project": "missing fields"}, "bad row"]}
    items = normalize_pools(payload)
    assert len(items) == 1
    assert items[0].opportunity_id == "defillama:abc-123"
