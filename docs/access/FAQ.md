# FAQ and Data Limits

## Is PolyLab financial advice?

No. PolyLab is a research and scanning tool. It helps you discover and compare markets faster, but it does not tell you what you should buy, sell, or hold.

## Where does the data come from?

PolyLab is built on top of Polymarket-related data sources used by the project, including market data from Gamma and additional holder analysis inputs described in the project documentation.

For users, the important point is simple: PolyLab aggregates and reshapes source data so the scanner is faster to use than raw browsing.

## How often is the data updated?

The product is designed around periodic refreshes rather than tick-level live execution. In the current product documentation, the scanner is described as running on an hourly update cycle.

If timing matters to your decision, always confirm critical details in the live market.

## Why can numbers differ from what I see directly on Polymarket?

A few common reasons:

- PolyLab may be showing a recent snapshot rather than the latest tick
- derived metrics can be calculated differently from what you infer manually
- source APIs, market metadata, and holder data can update on different cadences
- temporary data gaps or anomalies can distort individual rows

This is normal for an analytics layer. Use the scanner to prioritize attention, then verify specifics before acting.

## Why does a market with high APR still look bad?

Because APR is not a complete quality signal.

A market can show strong annualized return while still having:

- wide spread
- weak liquidity
- short-duration annualization effects
- poor underlying thesis quality

High APR is a prompt to investigate, not a reason to trust the setup automatically.

## Should I trust Smart Money signals?

Treat them as informative but imperfect.

They can help surface patterns that are hard to see manually, but they are still a layer of interpretation over incomplete and changing market data. They are best used to prioritize review, not to outsource judgment.

## What should I check before acting on a market?

At minimum:

1. Confirm the current live price.
2. Check spread and liquidity.
3. Re-read the market wording and resolution criteria.
4. Make sure the time horizon matches your thesis.
5. Treat scanner metrics as support, not as proof.

## Do I need an account to understand whether PolyLab is useful?

No. The intended product model is guest-first for discovery. You should be able to browse the scanner, inspect markets, and understand the product's value before any sign-in requirement for persistence features.

More detail is in [Access Model](./ACCESS_MODEL.md).

## What is the main limitation to keep in mind?

PolyLab is strongest as a discovery and prioritization layer.

It is not a substitute for:

- reading the live market carefully
- understanding resolution rules
- checking execution quality
- making your own risk decisions
