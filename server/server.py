"""server

Serves the following endpoints:

    GET /jobs
        Return an HTML page containing a table of all jobs, sorted by most
        recent first.

    POST /jobs
        Create a new job.  The request body must be a form containing the
        following fields:

        - "proxy" is the kind of proxy, i.e. either "nginx" or "envoy".
        - "proxy_commit" is the SHA1 hash of the git commit of the proxy
          project that the job will build and test.
        - "tracer_commit" is the SHA1 hash of the git commit of the tracing
          library project (i.e. dd-trace-cpp) that the job will use in the
          build of the proxy.

Requires the following environment variables:

    DATABASE_DIR
        Path to the directory containing the sqlite3 database and SQL statement
        files.
    
    LOGS_DIR
        Path to the directory containing log files.
"""

from flask import Flask, request
import json
import os
from pathlib import Path
import sqlite3
import sxml

db_dir = Path(os.environ['DATABASE_DIR'])
logs_dir = Path(os.environ['LOGS_DIR'])
db_path = db_dir / 'database.sqlite'
app = Flask(__name__, static_folder=logs_dir)


def link_to_log(file_name):
    if file_name is None:
        return ''
    return ['a', {'href': f'/logs/{file_name}'}, 'output']


def render_runtime(seconds: float):
    """Return a human-readable time duration of the specified number of
    `seconds`.
    """
    seconds = int(seconds)
    if seconds < 60:
        return f'{seconds}s'
    minutes = seconds // 60
    seconds = seconds % 60
    if minutes < 60:
        return f'{minutes}m {seconds}s'
    hours = minutes // 60
    minutes = minutes % 60
    return f'{hours}h {minutes}m {seconds}s'


def render_job_status(runtime_seconds, return_status):
    """Return a human-readable description of the run status of the job based
    on the specified `runtime_seconds` and `return_status`.
    """
    if return_status is None:
        return 'Queued'
    if runtime_seconds is None:
        return 'Running'
    runtime = render_runtime(runtime_seconds)
    if return_status == 0:
        return f'Complete ({runtime})'
    return f'Failed ({runtime})'


def jobs_rows(jobs_cursor):
    """Yield HTML table rows from the specified SQL query result set
    `jobs_cursor`.
    """
    for created, proxy, proxy_commit, proxy_commit_url_pattern, tracer_commit, begin, end, runtime, status, log in jobs_cursor:
        yield ['tr',
            # Created
            ['td', created.replace('T', ' ') + ' UTC'],
            # Proxy
            ['td', proxy],
            # Proxy Commit
            ['td',
                ['a', {'href': proxy_commit_url_pattern.format(commit=proxy_commit)},
                    proxy_commit[:7]]],
            # Tracer Commit
            ['td',
                ['a', {'href': f'https://github.com/Datadog/dd-trace-cpp/commit/{tracer_commit}'},
                    tracer_commit[:7]]],
            # Status
            ['td', render_job_status(runtime, status)],
            # Output (log)
            ['td', link_to_log(log)]] # yapf: disable


def render_jobs_page(jobs_cursor):
    """Return an HTML page containing a table of jobs based off of the specified SQL query result set `jobs_cursor`. 
    """
    return sxml.html_from_sexpr(
      ['html',
        ['head', ['title', 'Proxy Punisher: Jobs']],
        ['body',
          ['table', {'border': '1'},
            ['tr',
              ['th', 'Created'],
              ['th', 'Proxy'],
              ['th', 'Proxy Commit'],
              ['th', 'Tracer Commit'],
              ['th', 'Status'],
              ['th', 'Output']],
              *jobs_rows(jobs_cursor)]]]) # yapf: disable


@app.get('/jobs')
def get_jobs():
    sql = (db_dir / 'statements' / 'get-jobs.sql').read_text()
    with sqlite3.connect(f'file:{db_path}?mode=ro', uri=True) as db:
        db.execute('pragma foreign_keys = on;')
        return render_jobs_page(db.execute(sql))
    # TODO: `db.close()` without screwing up transactions.


@app.post('/jobs')
def post_jobs():
    proxy = request.form.get('proxy')
    if proxy is None:
        return f'Missing the "proxy" form field.\n', 400
    proxy_commit = request.form.get('proxy_commit')
    if proxy_commit is None:
        return f'Missing the "proxy_commit" form field.\n', 400
    tracer_commit = request.form.get('tracer_commit')
    if tracer_commit is None:
        return f'Missing the "tracer_commit" form field.\n', 400

    sql = (db_dir / 'statements' / 'create-job.sql').read_text()
    with sqlite3.connect(db_path) as db:
        db.execute('pragma foreign_keys = on;')
        try:
            db.execute(
                sql, {
                    'proxy': proxy,
                    'proxy_commit': proxy_commit,
                    'tracer_commit': tracer_commit
                })
        except sqlite3.IntegrityError as error:
            return f'{error}\n', 400
    db.close()
    return 'ok\n'


def server():
    """This is the entrypoint for `waitress`, the uWSGI runner."""
    return app
