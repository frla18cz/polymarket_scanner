select
  date_trunc('day', created_at) as day,
  count(*) filter (
    where event_name = 'page_view'
      and page_key = 'custom-data'
  ) as custom_data_views,
  count(*) filter (
    where event_name = 'cta_click'
      and page_key = 'custom-data'
      and coalesce(metadata ->> 'target_page_key', '') = 'email'
  ) as email_cta_clicks,
  count(distinct session_id) filter (
    where page_key = 'custom-data'
  ) as custom_data_sessions
from public.marketing_events
group by 1
order by 1 desc;
