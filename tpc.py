from flask import Flask, g, render_template, request, jsonify, url_for
import chess, chess.uci
import time
import sqlite3
from contextlib import closing
from werkzeug.contrib.cache import SimpleCache
import os
from flask.ext.sqlalchemy import SQLAlchemy

print os.environ['APP_SETTINGS']
app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
db = SQLAlchemy(app)

app.cache = SimpleCache()

def connect_db():
    """Connects to a specific database"""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

def with_context(fun):
        with app.app_context():
            return fun()

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

def insert_db(query, args):
    db = get_db()
    cur = db.cursor()
    cur.execute(query, args)
    db.commit()
    id = cur.lastrowid
    cur.close()
    return id

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def query_state():
    game_query = "select id from games order by id desc limit 1"
    game = query_db(game_query, one=True)
    if game == None:
        print "No game state"
        return {'game' : None, 'pos' : None}
    else:
        print "game", game
    game = game[0]
    pos_query = """select pos from moves where game=? order by id desc limit
    1"""
    pos = query_db(pos_query, args=(game,), one=True)
    print "pos", pos
    if pos == None:
        print "No position state"
        return {'game' : game, 'pos' : None}
    pos = pos[0]
    return { 'game' : game, 'pos' : pos }

@app.teardown_appcontext
def close_connection(exception):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

@app.route("/")
def index():
    print url_for('index')
    print request.url
    return render_template("index.html")

@app.route("/send_move")
def send_move():
    a = request.args.get('a', 0, type=int)
    b = request.args.get('b', 0, type=int)
    return jsonify(result = a + b)

@app.route("/new_game")
def new_game():
    print "Hi"

@app.route("/get_position")
def get_position():
    rv = app.cache.get('position')
    if rv is None:
        rv = query_state()['pos']
        app.cache.set('position', rv, timeout= 1)
    print rv
    return jsonify(position=rv)  

if __name__ == "__main__":
    #app.run(host='0.0.0.0')
    app.run(threaded=True,debug=True)
