update Job set
  end_iso_utc = replace(datetime('now'), ' ', 'T'),
  status_code = @status_code
where proxy=@proxy
  and proxy_commit=@proxy_commit
  and tracer_commit=@tracer_commit;
