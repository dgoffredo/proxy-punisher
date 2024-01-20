"""runner

Picks an unstarted job from the database and runs it.

Requires the following environment variables:

    DATABASE_DIR
        Path to the directory containing the sqlite3 database and SQL statement
        files.

    LOGS_DIR
        Path to the directory into which the runner will write job logs.
    
    BIN_DIR
        Path to the directory containing the proxy-specific scripts, i.e. the
        "bin/" subdirectory. 
"""

import os
from pathlib import Path
import sqlite3
import subprocess
import sys

db_dir = Path(os.environ['DATABASE_DIR'])
db_path = db_dir / 'database.sqlite'
logs_dir = Path(os.environ['LOGS_DIR'])
bin_dir = Path(os.environ['BIN_DIR'])

with sqlite3.connect(db_path) as db:
    rows = list(
        db.execute((db_dir / 'statements' / 'pick-job.sql').read_text()))
    if len(rows) == 0:
        sys.exit(0)
    assert len(rows) == 1

    (proxy, proxy_git_remote_url, proxy_commit, tracer_commit), = rows
    log_file_name = f'{proxy}-{proxy_commit}-{tracer_commit}.log.txt'
    db.execute(
        (db_dir / 'statements' / 'begin-job.sql').read_text(), {
            'proxy': proxy,
            'proxy_commit': proxy_commit,
            'tracer_commit': tracer_commit,
            'log_file_name': log_file_name
        })

db.close()

with open(logs_dir / log_file_name, 'w') as log:
    if proxy == 'nginx':
        script_path = bin_dir / 'test-nginx'
    else:
        assert proxy == 'envoy'
        script_path = bin_dir / 'test-envoy'

    child_env = dict(os.environ)
    child_env['PROXY_REMOTE'] = proxy_git_remote_url
    child_env['PROXY_COMMIT'] = proxy_commit
    child_env['TRACER_COMMIT'] = tracer_commit
    result = subprocess.run([str(script_path)],
                            stdout=log,
                            stderr=log,
                            env=child_env)

with sqlite3.connect(db_path) as db:
    db.execute(
        (db_dir / 'statements' / 'end-job.sql').read_text(), {
            'status_code': result.returncode,
            'proxy': proxy,
            'proxy_commit': proxy_commit,
            'tracer_commit': tracer_commit
        })
