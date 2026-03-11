select
  page_key,
  landing_variant,
  count(*) filter (where event_name = 'page_view') as page_views,
  count(*) filter (where event_name = 'cta_click') as cta_clicks,
  count(distinct session_id) as unique_sessions,
  round(
    (
      count(*) filter (where event_name = 'cta_click')::numeric
      / nullif(count(*) filter (where event_name = 'page_view'), 0)
    ) * 100,
    2
  ) as cta_click_rate_pct
from public.marketing_events
group by 1, 2
order by page_views desc, cta_click_rate_pct desc nulls last;
