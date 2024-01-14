select
  create_iso_utc,
  proxy,
  proxy_commit,
  Proxy.commit_url_pattern as proxy_commit_url_pattern,
  tracer_commit,
  begin_iso_utc,
  end_iso_utc,
  runtime_seconds,
  status_code,
  log_file_name
from Job
inner join Proxy on Job.proxy = Proxy.name
order by create_iso_utc desc;
