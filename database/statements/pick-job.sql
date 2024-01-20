select
  proxy,
  Proxy.git_remote_url as proxy_git_remote_url,
  proxy_commit,
  tracer_commit
from Job
inner join Proxy on Job.proxy = Proxy.name
where begin_iso_utc is null
order by create_iso_utc
limit 1;
