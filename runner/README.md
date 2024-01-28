[runner.py](runner.py) is a script that pops an unstarted job from the
database, runs it, and then updates the database with the result of the job
run.

The actual work of the job is done by one of the shell scripts in [bin/](bin).
The runner executes one of the scripts as a subprocess. Output is written
to a job specific file in the [logs directory](../logs).

The path to the logs directory, the database directory, and the bin directory
are all configured via mandatory environment variables.  See
[runner.py](runner.py).
