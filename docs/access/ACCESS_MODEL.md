# Product Access Model

This document defines the intended PolyLab access model so future UI, auth, and monetization work stays consistent.

## Core Principle

PolyLab should be easy to try without friction.

- Guests should reach the core product and understand its value quickly.
- Signed-in users should get persistence and continuity.
- Pricing, if introduced later, should apply to advanced workflow leverage, not basic access.

This means the product should be designed as:

- `Guest` = exploration and value discovery
- `Signed-in` = persistence and retention
- `Future premium` = advanced workflow acceleration

## Guest Experience

Guests should be able to use the product meaningfully without hitting an auth wall.

Guest access should include:

- entering `/app`
- browsing the market scanner
- using the core filter set
- opening market details
- viewing Smart Money context
- using the product long enough to understand why it is better than manual Polymarket browsing

The guest experience should not feel like a crippled demo.

## Signed-In Experience

Signing in should unlock continuity features, not basic product access.

Signed-in-only features should center on saved state and repeat usage, such as:

- saved presets
- saved filters
- watchlist or favorites
- recently viewed markets
- synced preferences across devices
- remembered layout or UI preferences
- saved market groups or research lists
- future email updates or notifications tied to the account

The user prompt should be tied to high-intent actions like:

- `Sign in to save this preset`
- `Sign in to save these filters`
- `Sign in to continue this workflow later`

Not:

- `Sign in to use PolyLab`

## Future Premium Candidates

If monetization is introduced later, it should focus on leverage features rather than first-use discovery.

Reasonable future premium candidates:

- deeper or more advanced filters
- more powerful preset workflows
- advanced Smart Money depth or overlays
- exports
- alerts or notifications with richer controls
- advanced market discovery tools
- workflow features that save heavy users time every day

These are intentionally separate from the signed-in baseline.

## UX Rules

- Do not put a login wall in front of the scanner.
- Do not force signup before the user sees real value.
- Use auth prompts at the moment of intent, not on first load.
- Keep pricing language separate from account language while PolyLab remains free during early access.

## Current Practical Direction

Today, PolyLab should be treated internally as:

- guest access for almost the entire scanner experience
- sign-in for persistence and retention features
- no public pricing wall yet

Any existing login gate on individual features should be treated as an implementation detail, not the long-term product model, unless intentionally reaffirmed later.
