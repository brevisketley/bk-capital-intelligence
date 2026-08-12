from bk_capital_intelligence.replay import replay


def test_replay_is_walk_forward_and_produces_all_baselines():
    series = {
        "a": [
            {"timestamp": 1, "apy": 10, "tvlUsd": 2_000_000, "apyReward": 0},
            {"timestamp": 2, "apy": 5, "tvlUsd": 2_000_000, "apyReward": 0},
            {"timestamp": 3, "apy": 5, "tvlUsd": 2_000_000, "apyReward": 0},
        ],
        "b": [
            {"timestamp": 1, "apy": 8, "tvlUsd": 2_000_000, "apyReward": 0},
            {"timestamp": 2, "apy": 12, "tvlUsd": 2_000_000, "apyReward": 0},
            {"timestamp": 3, "apy": 12, "tvlUsd": 2_000_000, "apyReward": 0},
        ],
    }
    result = replay(series, top_k=1)
    assert result.observations == 2
    assert result.bk.ending_value > 1
    assert result.highest_apy.ending_value > 1
    assert result.equal_weight.ending_value > 1
