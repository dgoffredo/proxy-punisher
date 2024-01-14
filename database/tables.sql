create table Proxy(
  name text not null primary key,
  description text not null,
  git_remote_url text not null,
  -- Python format style pattern, where {commit_sha} is the SHA1 of the git
  -- commit.
  commit_url_pattern text not null);

insert into Proxy(name, description, git_remote_url, commit_url_pattern) values
  ('envoy',
   'Envoy with the Datadog extension',
   'https://github.com/envoyproxy/envoyproxy/envoy',
   'https://github.com/envoyproxy/envoy/commit/{commit_sha}'),
  ('nginx',
   'NGINX with the nginx-datadog module',
   'https://github.com/Datadog/nginx-datadog',
   'https://github.com/Datadog/nginx-datadog/commit/{commit_sha}');

create table Job(
  create_iso_utc text not null,
  proxy text not null,
  proxy_commit text not null,
  tracer_commit text not null,
  begin_iso_utc text,
  end_iso_utc text,
  runtime_seconds real as
    (case 
       when begin_iso_utc is null or end_iso_utc is null then
         null
       else
         24*60*60*(julianday(end_iso_utc) - julianday(begin_iso_utc))
     end),
  status_code integer,
  log_file_name text,

  foreign key(proxy) references Proxy(name),
  unique (proxy, proxy_commit, tracer_commit));
