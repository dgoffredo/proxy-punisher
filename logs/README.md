For each job executed by the [runner](../runner), standard output and standard
error are written to a file in this directory.  Each file has the `.log.txt`
suffix and is exposed under the [server](../server)'s `/logs` endpoint.  They
are also linked from the server's `/jobs` page.
