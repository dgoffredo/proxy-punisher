update Job set
  begin_iso_utc = replace(datetime('now'), ' ', 'T'),
  log_file_name = @log_file_name
where proxy=@proxy
  and proxy_commit=@proxy_commit
  and tracer_commit=@tracer_commit;
