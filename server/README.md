This directory contains an HTTP server that allows jobs to be created and
listed.

The actual work of running a job is not triggered by the server.  Instead, a
separate [runner](../runner) component periodically executes any pending job.

This module has [dependencies](requirements.txt) that can be installed via
`pip3 install -r requirements.txt`.

Running the server requires certain environment variables.  See
[server.py](server.py) and [bin/server](../bin/server).
