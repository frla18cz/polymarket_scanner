# Implementation Plan: User Documentation Starter Pack

Create a compact first-pass user documentation set under `docs/access/` so people can understand how to use PolyLab and how to read the main scanner metrics.

## Phase 1: Docs Structure
- [x] Task: Create a dedicated Conductor track for the user-documentation work.
- [x] Task: Turn `docs/access/README.md` into a user-docs hub that links the first documentation set.

## Phase 2: Core User Docs
- [x] Task: Add a getting-started guide focused on first-use scanner workflows and common mistakes.
- [x] Task: Add a plain-language metrics guide for price, spread, liquidity, volume, APR, and Smart Money context.
- [x] Task: Add a FAQ/limitations guide covering cadence, discrepancies, and non-advisory positioning.
- [x] Task: Preserve the access-model writeup as a separate companion document linked from the hub.

## Phase 3: Public Web Docs
- [x] Task: Add a public `/docs` page that exposes the user documentation on the website.
- [x] Task: Link the docs page from the public marketing surfaces.
- [x] Task: Serve `/docs` in local/backend frontend mode and Vercel routing, and add it to the sitemap.
- [x] Task: Add targeted contract tests for docs content, route serving, and indexing coverage.

## Phase 4: Multipage Docs Rebuild
- [x] Task: Replace the one-page docs landing with a classic multipage docs IA and sidebar shell.
- [x] Task: Make markdown the source of truth for public docs content and add a generator for published HTML.
- [x] Task: Add detailed trader-facing pages for workflows, filters, metrics, APR methodology, Smart Money methodology, and data limitations.
- [x] Task: Update routing, rewrites, and sitemap coverage for nested docs pages.
- [x] Task: Add regression tests for markdown source, generated docs pages, nested routing, and docs SEO metadata.

## Phase 5: Full Public Methodology Expansion
- [x] Task: Mark the entire public docs surface as `In Progress` with both a global banner and page-level status.
- [x] Task: Add public docs pages for project overview, upstream data sources, refresh/storage pipeline, and reference contracts.
- [x] Task: Document exact current upstream endpoints, field mapping, snapshot cadence, holder sampling limits, and derived metrics.
- [x] Task: Align the internal UI contract with the current public app contract where outdated Smart Money win-rate references remained.
- [x] Task: Expand generator and tests to cover the wider docs IA and exact implementation-level content.
