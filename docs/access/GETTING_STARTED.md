# Getting Started with PolyLab

This guide is for someone opening PolyLab for the first time and trying to get useful results fast.

## What PolyLab Is Best At

PolyLab is strongest when you want to:

- scan many active markets faster than the native Polymarket UI
- narrow the list down with filters instead of browsing manually
- compare opportunities using spread, liquidity, APR, and Smart Money context
- move from broad discovery to a short list worth deeper review

It is less useful if you expect tick-level execution tools or automated trading.

## A Good First Workflow

1. Start with a broad category or theme you understand.
2. Narrow the expiration window so you are not comparing markets with completely different timelines.
3. Limit spread and set minimum liquidity so you avoid markets that are hard to enter or exit cleanly.
4. Use price range to focus on the type of position you actually want to study.
5. Sort by the field that matches your goal, usually `APR`, `Spread`, `Volume`, `Liquidity`, or `Expires`.
6. Open a handful of candidates and compare the full market details before deciding anything.

## What the Main Filters Are For

### Categories

Use included categories to focus the list. Use excluded categories to strip out entire areas you know you do not want to review.

This is usually the fastest way to cut noise.

### Expires Within / Not Sooner Than

These filters are useful when you want comparable market horizons.

- short windows are better for urgent, event-driven setups
- longer windows are better when you want time for a thesis to play out

### Price Range

This helps you focus on a probability band.

- lower prices usually mean lower implied odds of resolving in your favor
- higher prices usually mean the market already thinks the outcome is likely

The filter is most useful when combined with spread and liquidity.

### Max Spread

Use this to remove markets where entry cost is inflated by a wide bid-ask gap.

As a rule of thumb, lower spread means cleaner pricing and less friction.

### Min Volume / Min Liquidity

Use these together.

- volume tells you how active trading has been
- liquidity tells you more about market depth right now

High volume with weak liquidity can still be annoying to trade. Low spread with very low liquidity can also be misleading.

### APR

APR is useful for comparing potential annualized return, but it should never be read in isolation. A very high APR can still be attached to poor market quality, weak liquidity, or a thesis you do not trust.

### Smart Money Context

Treat Smart Money signals as context, not proof.

They can help you notice where historically stronger wallets are concentrated, but they do not guarantee the current market is mispriced.

## Three Practical Use Cases

### 1. Safe, Cleaner Markets

Try:

- tighter `Max Spread`
- higher `Min Liquidity`
- moderate to high price range
- shorter shortlist with manual review

### 2. Longer-Horizon Research

Try:

- broader expiration window
- stronger category filtering
- sort by liquidity or volume first
- use Smart Money fields as a secondary filter

### 3. Mispricing Hunt

Try:

- price range plus spread cap
- sort by APR
- check holders and market details before trusting the ranking

## Common Mistakes

- chasing APR without checking spread or liquidity
- comparing markets with very different timelines
- treating Smart Money labels as automatic conviction
- assuming scanner rank equals trade recommendation

## Next Step

Once you are comfortable scanning the list, read [Metrics Guide](./METRICS.md) so the numbers mean something consistent.
