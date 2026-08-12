# BK Capital Intelligence

AI-native, risk-adjusted digital-capital intelligence platform.

## Mission
Discover, evaluate, simulate and monitor capital-allocation opportunities using evidence, deterministic risk controls and multi-agent analysis.

## Live research MVP
- Render: https://bk-capital-intelligence.onrender.com
- Health: https://bk-capital-intelligence.onrender.com/health
- Live scan API: https://bk-capital-intelligence.onrender.com/api/scan?limit=25
- Source registry: https://bk-capital-intelligence.onrender.com/api/sources

## Build boundary
This repository and its dedicated Render service are the only resources for this project. Existing GitHub repositories and Render services are outside scope and must not be modified.

## Safety gates
- No user funds in MVP
- No custody
- No token in MVP
- No profit guarantees
- No autonomous execution before security, legal and risk gates pass

## Core loop
Discover → Normalize → Score → Rank → Simulate → Benchmark → Learn → Monitor

## Current working components
- DeFiLlama discovery ingestion
- APY/base/reward decomposition and provenance
- Provisional deterministic risk engine
- Hard exposure-cap portfolio allocator
- Out-of-sample performance metric engine
- Morpho and Pendle read-only enrichment clients
- Deterministic Guardian policy layer
- Research → Risk → Portfolio → Guardian swarm contract
- Dependency-free web dashboard and JSON API
- GitHub Actions test suite

## First proof point
Compare BK risk-adjusted allocation against highest-APY and equal-weight baselines using net return, volatility, drawdown, liquidity/exit events and protocol-risk events.

## Next build sequence
1. Historical observation storage
2. Protocol-level enrichment and confidence scoring
3. Point-in-time replay dataset
4. Benchmark engine with walk-forward validation
5. Critic/adversarial agent layer
6. Monitoring and audit trail
7. Commercial analytics layer
8. Controlled non-custodial transaction proposals only after legal/security gates
