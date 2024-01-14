insert into Job(
  create_iso_utc,
  proxy,
  proxy_commit,
  tracer_commit)
values(
  replace(datetime('now'), ' ', 'T'),
  @proxy,
  @proxy_commit,
  @tracer_commit);
