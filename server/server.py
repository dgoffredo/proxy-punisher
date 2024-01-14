from flask import Flask #, request

app = Flask(__name__)

@app.get('/jobs')
def get_jobs():
    # name = request.args.get("name", "World")
    return 'Hello!\n'

@app.post('/jobs')
def post_jobs():
    return 'Not yet!\n'

def server():
    return app
