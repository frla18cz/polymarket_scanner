select
  coalesce(utm_source, '(none)') as utm_source,
  coalesce(utm_medium, '(none)') as utm_medium,
  coalesce(utm_campaign, '(none)') as utm_campaign,
  count(*) filter (where event_name = 'page_view') as page_views,
  count(*) filter (where event_name = 'cta_click') as cta_clicks,
  count(*) filter (where event_name = 'auth_signed_in') as auth_signed_ins,
  count(distinct session_id) as unique_sessions,
  round(
    (
      count(*) filter (where event_name = 'cta_click')::numeric
      / nullif(count(*) filter (where event_name = 'page_view'), 0)
    ) * 100,
    2
  ) as click_through_pct
from public.marketing_events
group by 1, 2, 3
order by page_views desc, auth_signed_ins desc, cta_clicks desc;
