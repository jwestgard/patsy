from flask import Flask
from flask import render_template
from flask import request
from flask_script import Manager
from flask_bootstrap import Bootstrap
import sqlite3
from flask import g

DATABASE = 'data/patsy.db'
app = Flask(__name__)
manager = Manager(app)
bootstrap = Bootstrap(app)

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db

def make_dicts(cursor, row):
    return dict((cursor.description[idx][0], value)
                for idx, value in enumerate(row))

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/')
def index():
    user_agent = request.headers.get('User-Agent')
    return render_template('index.html')

@app.route('/assets')
def assets():
    query = 'SELECT * FROM assets'
    rows = query_db(query)
    return render_template('assets.html', assets=rows)

@app.route('/batches')
def batches():
    query = 'SELECT * FROM batches'
    rows = query_db(query)
    return render_template('batches.html', batches=rows)

@app.route('/instances')
def instancescur():
    query = 'SELECT * FROM instances'
    rows = query_db(query)
    return render_template('instances.html', instances=rows)

if __name__ == '__main__':
    manager.run()
