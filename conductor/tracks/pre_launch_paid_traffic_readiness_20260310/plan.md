# Implementation Plan: Pre-Launch Paid Traffic Readiness

Prepare the paid-traffic web path by tightening copy, attribution, activation measurement, indexing behavior, and landing-page media loading before any ad spend.

## Phase 1: Contract and Track Setup
- [x] Task: Add failing contract tests for app auth copy, attribution persistence tokens, activation event names, canonical/robots meta, and lazy-loaded marketing proof media.
- [x] Task: Register this work as a dedicated Conductor track and keep the plan/spec updated through implementation.

## Phase 2: Copy and Tracking Foundation
- [x] Task: Replace misleading app `Pro`/`premium` auth wording with neutral account copy while keeping current auth gating behavior.
- [x] Task: Extend the shared tracking helper to persist first-touch attribution and reuse it on later events.
- [x] Task: Add app activation tracking for first market load, first filter use, Smart Money entry, outbound market opens, and password-login lifecycle events.

## Phase 3: Indexing and Media Hygiene
- [x] Task: Add canonical tags and `noindex,follow` where appropriate across marketing pages and `/app`.
- [x] Task: Lazy-load non-active proof/gallery media and reduce landing hero video eagerness on mobile/reduced-motion.
- [x] Task: Re-run the targeted frontend contract suite for home, landing, custom-data, app, shared tracking, and meta surfaces.
