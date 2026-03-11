select
  date_trunc('day', created_at) as day,
  count(*) as total_events,
  count(*) filter (where event_name = 'page_view') as page_views,
  count(*) filter (where event_name = 'cta_click') as cta_clicks,
  count(*) filter (where event_name = 'auth_signed_in') as auth_signed_ins,
  count(distinct session_id) as unique_sessions,
  count(distinct user_id) filter (where user_id is not null) as known_users
from public.marketing_events
group by 1
order by 1 desc;
