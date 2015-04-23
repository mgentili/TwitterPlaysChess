from flask import Flask, g, render_template, request, jsonify, url_for
import chess, chess.uci
import time
from contextlib import closing
from werkzeug.contrib.cache import SimpleCache
import os
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import desc

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
db = SQLAlchemy(app)
app.cache = SimpleCache()

import models

def init_db():
    db.create_all()

def query_state():
    g = db.session.query(models.Games.id).order_by(desc(models.Games.id)).first()
    if g == None:
        print "No game state"
        return {'game' : None, 'pos' : None}
    pos = db.session.query(models.Positions.pos).order_by(desc(models.Positions.id)).filter_by(game=g[0]).first()
    if pos == None:
        print "No position state"
        return {'game' : g[0], 'pos' : None}
    return { 'game' : g[0], 'pos' : pos[0] }

@app.route("/")
def index():
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
    return jsonify(position=rv)  

if __name__ == "__main__":
    app.run(threaded=True)
