with funnel as (
  select
    session_id,
    min(created_at) filter (where event_name = 'page_view' and page_key in ('home', 'landing', 'custom-data')) as first_marketing_view_at,
    min(created_at) filter (where event_name = 'cta_click' and page_key in ('home', 'landing', 'custom-data')) as first_marketing_click_at,
    min(created_at) filter (where event_name = 'page_view' and page_key = 'app') as first_app_view_at,
    min(created_at) filter (where event_name = 'oauth_login_started') as first_oauth_start_at,
    min(created_at) filter (where event_name = 'signup_success') as first_signup_success_at,
    min(created_at) filter (where event_name = 'auth_signed_in') as first_signed_in_at
  from public.marketing_events
  group by session_id
)
select
  count(*) filter (where first_marketing_view_at is not null) as marketing_sessions,
  count(*) filter (where first_marketing_click_at is not null) as clicked_cta,
  count(*) filter (where first_app_view_at is not null) as reached_app,
  count(*) filter (where first_oauth_start_at is not null) as started_oauth,
  count(*) filter (where first_signup_success_at is not null) as signed_up_email,
  count(*) filter (where first_signed_in_at is not null) as signed_in,
  round(
    (
      count(*) filter (where first_signed_in_at is not null)::numeric
      / nullif(count(*) filter (where first_marketing_view_at is not null), 0)
    ) * 100,
    2
  ) as marketing_to_sign_in_pct
from funnel;
