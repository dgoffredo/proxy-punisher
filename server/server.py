from flask import Flask, request
import json
import os
from pathlib import Path
import sqlite3
import sxml

db_dir = Path(os.environ['DATABASE_DIR'])
db_path = db_dir / 'database.sqlite'
app = Flask(__name__)


def link_to_log(file_name):
    if file_name is None:
        return ''
    return ['a', {'href': f'/logs/{file_name}'}, 'output']


def render_runtime(seconds):
    """TODO
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
    """TODO
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
    """TODO
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
    """TODO
    """
    return sxml.html_from_sexpr(['html',
        ['body',
            ['table',
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
    return 'ok\n'


def server():
    """This is the entrypoint for `waitress`, the uWSGI runner."""
    return app
