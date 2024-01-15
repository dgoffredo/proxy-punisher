"""runner

TODO:
- Pick a job from the database.
- None? Done.
- If nginx:
  - fetch, checkout commit
  - cd dd-trace-cpp, fetch, checkout commit
  - make test TEST_ARGS='--verbose'
- If envoy
  - fetch, checkout commit
  - cd ../dd-trace-cpp, fetch, checkout commit
  - bazelisk test --override_repository=blahblah=../dd-trace-cpp --verbose_failures //test/blah/blah
- Loop back to the top.
"""

