# PolyLab Metrics Guide

This guide explains the main market metrics in plain language.

The exact implementation can evolve, but the practical meaning of each field should stay stable.

## Price

Price is the current market price of the selected outcome.

In prediction-market terms, it behaves like an implied probability on a `0` to `1` scale. A price near `0.70` roughly means the market is pricing that outcome around `70%`.

Practical use:

- compare how confident the market already is
- define the probability band you want to study
- combine with spread before reading too much into a single number

## Spread

Spread is the gap between the buy and sell side of the market.

A lower spread is generally better. It usually means:

- less friction to enter or exit
- cleaner price discovery
- better comparability between similar markets

A wide spread is a warning sign. It often means the market is harder to trade efficiently, even if the headline price looks attractive.

## Liquidity

Liquidity tells you how much depth the market has.

Higher liquidity usually means larger orders can be handled with less slippage. For scanner users, it is one of the best quick filters for removing fragile markets.

Liquidity matters because a market can look interesting on paper but still be difficult to trade at a fair price.

## Volume

Volume tells you how much trading activity has already happened over the measured period.

Higher volume can indicate stronger attention and participation, but volume alone does not guarantee tight pricing or good current depth.

Use volume as a sign of activity, not as a standalone quality score.

## APR

APR is an annualized return estimate based on the current market setup.

Why it is useful:

- it gives you a common frame for comparing opportunities with different time horizons
- it can highlight markets where the payoff profile looks unusually strong

Why it can mislead:

- annualization can make short-duration setups look extreme
- it says nothing by itself about execution quality
- it does not validate the underlying thesis

Best practice:

- use APR as a ranking aid
- confirm spread, liquidity, price, and market context before acting

## Expiration

Expiration tells you when the market resolves or becomes due.

This matters because return potential, uncertainty, and comparability all change with time horizon. Many scanner mistakes come from comparing a near-term market with a long-duration market as if they were equivalent.

## Smart Money Win Rate

Smart Money Win Rate is intended to summarize how successful relevant tracked holders have been historically.

Use it as:

- a directional indicator
- a prioritization hint
- one more piece of context when deciding what to inspect manually

Do not use it as:

- a guarantee that the current side is right
- a replacement for reading the market itself
- proof that a market is safe

## Profitable / Losing Holder Counts

These counts help show how tracked holders are distributed around the market.

They are useful when you want to see whether stronger historical participants are clustering on one side or whether conviction looks mixed.

The counts are more meaningful in combination than alone. A single count without market context can exaggerate weak indicators.

## Freshness / Last Updated

Freshness tells you how recent the underlying scanner data is.

This matters because PolyLab is designed around snapshot-based analysis, not tick-by-tick execution. If the last update is old, treat the scanner as a research starting point and confirm important details directly in the live market.

## A Good Interpretation Pattern

When you evaluate a candidate market, read metrics in this order:

1. Price and expiration to understand the basic setup.
2. Spread and liquidity to judge whether the market is practically tradable.
3. Volume to understand participation.
4. APR to compare attractiveness across candidates.
5. Smart Money fields to add context, not certainty.

That order prevents the most common mistake: overvaluing a single flashy metric.
