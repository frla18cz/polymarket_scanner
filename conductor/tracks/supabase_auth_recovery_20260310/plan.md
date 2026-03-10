# Implementation Plan: Supabase Auth Recovery and Marketing Tracking

Restore the minimal Supabase public schema needed for PolyLab auth-side metadata and ad-tracking, then wire a lightweight shared tracker into the marketing pages and app.

## Phase 1: Contracts and Schema Definition
- [x] Task: Add failing tests for the Supabase recovery migration contract and shared tracking asset integration.
- [x] Task: Document the new Supabase public-schema role in the tech stack before implementation.

## Phase 2: Schema Recovery
- [x] Task: Add a checked-in SQL migration for `profiles`, `marketing_events`, RLS policies, and the auth trigger/backfill flow.
- [x] Task: Apply the migration to the live Supabase project and verify that existing `auth.users` are backfilled into `profiles`.

## Phase 3: Frontend Tracking Hooks
- [x] Task: Add a shared frontend tracking helper and mirror it between `frontend_deploy/assets` and `static/assets`.
- [x] Task: Wire page-view and CTA tracking into `/`, `/landing`, `/custom-data`, and `/app` without blocking the UI.
- [x] Task: Re-run targeted contract tests for the new migration asset, mirrored frontend assets, and page integration.
