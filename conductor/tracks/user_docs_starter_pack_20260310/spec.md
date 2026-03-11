# Specification: User Documentation Starter Pack (Mar 2026)

## 1. Overview

PolyLab has strong internal and engineering documentation, but it lacks a compact set of user-facing docs that explain what the product does, how to use the scanner effectively, and how to interpret the main metrics. The first documentation pack should make the product easier to understand without requiring users to read internal product notes or reverse-engineer metric behavior.

## 2. Functional Requirements

### 2.1 Docs Hub

- Add a clear user-docs entry point under `docs/access/README.md`.
- The hub must link to the first core user-facing documents.

### 2.2 Getting Started Guide

- Add a short guide for first-time users that explains how to get value from the scanner quickly.
- The guide must explain the practical role of the main filter groups and common mistakes.

### 2.3 Metrics Guide

- Add a plain-language guide for the main scanner metrics.
- The guide must explain what each metric is useful for and where it can mislead users.

### 2.4 FAQ and Limits

- Add a user-facing FAQ that explains update cadence, data-source expectations, common discrepancies, and core limitations.

### 2.5 Access Model

- Preserve the existing access-model explanation as a linked companion document rather than burying it inside engineering docs.

### 2.6 Public Docs Surface

- Expose the user documentation on the public website under a dedicated docs route.
- The docs page must be reachable from public navigation, not only from the repository.
- Local/backend frontend mode and Vercel routing must both serve the public docs page.
- The public docs page should be indexable and present in the sitemap.

## 3. Non-Functional Requirements

- Keep the language direct and understandable for non-developers.
- Avoid implying financial advice or guaranteed signal quality.
- Keep the docs scoped to product use, not local development or deployment.

## 4. Acceptance Criteria

- [ ] `docs/access/README.md` acts as a user-docs hub.
- [ ] A new getting-started guide exists and is linked from the hub.
- [ ] A new metrics guide exists and is linked from the hub.
- [ ] A new FAQ/limitations guide exists and is linked from the hub.
- [ ] The access-model document remains available as a separate linked document.
- [ ] A public `/docs` page exists and is reachable from the public website.
- [ ] Local frontend mode and Vercel rewrites serve the docs page.
- [ ] The sitemap includes the docs page.
