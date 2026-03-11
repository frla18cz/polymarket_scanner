# Marketing Tracking

This folder holds the practical operating docs for PolyLab marketing telemetry.

## Why this lives here

- The tracking is product-specific and tied directly to the live Supabase schema.
- It is useful for day-to-day campaign work, but it should not bloat the root `README.md`.
- A short pointer from the main README is enough. The detailed queries and event taxonomy belong here.

## Current data model

Tracking events are stored in `public.marketing_events`.

Important fields:

- `created_at`
- `user_id`
- `session_id`
- `event_name`
- `page_path`
- `page_key`
- `landing_variant`
- `referrer`
- `utm_source`
- `utm_medium`
- `utm_campaign`
- `utm_term`
- `utm_content`
- `metadata`

User profiles are mirrored into `public.profiles` from `auth.users`.

## Current event names

Page and CTA events:

- `page_view`
- `cta_click`

Auth funnel events from `/app`:

- `signup_success`
- `oauth_login_started`
- `auth_signed_in`
- `auth_signed_out`

## Current page keys

- `home`
- `landing`
- `custom-data`
- `app`

## Where events are emitted

- `/` homepage
- `/landing`
- `/custom-data`
- `/app`

## Recommended workflow

1. Use `overview.sql` for a top-level daily read.
2. Use `utm_breakdown.sql` to check campaign/source quality.
3. Use `cta_performance.sql` to compare CTA placements.
4. Use `auth_funnel.sql` to inspect sign-in conversion after landing/app entry.

## Recommendation on documentation structure

Use one local folder like `docs/marketing/` for project-specific marketing ops.

Do not try to interconnect READMEs across multiple repos yet unless:

- the same schema is shared across projects
- the same dashboard queries are reused unchanged
- one repo is clearly the source of truth for growth ops

If you later want a cross-project layer, keep it lightweight:

- one central growth notes repo or Notion
- each product repo links to its own tracking docs
- avoid duplicating SQL in multiple repos
