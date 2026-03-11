select
  page_key,
  metadata ->> 'placement' as placement,
  metadata ->> 'label' as label,
  metadata ->> 'href' as href,
  count(*) as clicks,
  count(distinct session_id) as unique_sessions
from public.marketing_events
where event_name = 'cta_click'
group by 1, 2, 3, 4
order by clicks desc, unique_sessions desc;
