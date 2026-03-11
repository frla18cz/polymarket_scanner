# Specification: Supabase Auth Recovery and Marketing Tracking (Mar 2026)

## 1. Overview
PolyLab's Supabase project currently has its default `auth`, `storage`, and `realtime` system tables, but the application-owned `public` schema is empty. The product should restore only the minimum schema needed for auth-adjacent user metadata and future paid-traffic measurement without making the backend depend on Supabase.

## 2. Functional Requirements

### 2.1 Minimal Public Schema
- Create a `public.profiles` table keyed by `auth.users.id`.
- Automatically create or update `public.profiles` rows from `auth.users`.
- Create a `public.marketing_events` table for paid-traffic and product event logging.

### 2.2 Security and Access
- Enable RLS on both public tables.
- `profiles` rows must only be readable and writable by their owning authenticated user.
- `marketing_events` must allow inserts from anonymous and authenticated visitors.
- Public reads of `marketing_events` must not be exposed.

### 2.3 Frontend Tracking
- Marketing homepage, paid landing page, custom-data page, and app should load one shared lightweight tracking helper.
- The helper should capture page views and explicit CTA clicks with UTM/referrer/session context.
- Authenticated inserts should attach the current Supabase user id when available.

## 3. Non-Functional Requirements
- Do not change backend market-data architecture; SQLite remains the only backend read datastore.
- Keep tracking best-effort and non-blocking for the UI.
- Keep `frontend_deploy` and `static` mirrored for any new asset or HTML changes.

## 4. Acceptance Criteria
- [ ] Supabase contains `public.profiles` and `public.marketing_events` with RLS enabled.
- [ ] Existing `auth.users` rows are backfilled into `public.profiles`.
- [ ] Marketing pages and `/app` load a shared tracking helper.
- [ ] CTA clicks and page views can be inserted anonymously or as an authenticated user.
- [ ] The frontend contract tests for mirrored assets and route-specific HTML continue to pass.

## 5. Out of Scope
- Public self-serve analytics dashboards.
- Backend-side dependency on Supabase for market reads.
- Full CRM, billing, or public pricing flows.
