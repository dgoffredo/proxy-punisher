This directory contains a sqlite database of jobs.

- [tables.sql](tables.sql) defines the `Job` table.
- [statements/](statements) contains SQL statements used by the server and the
  runner to list jobs, create new jobs, pick jobs for execution, and update job
  properties.
- [\_\_init\_\_.py](__init__.py) contains utilities for accessing the database.
  These are used by the server and the runner. 

The database file itself (`database.sqlite`) is excluded from this repository
by [../.gitignore](../.gitignore).
