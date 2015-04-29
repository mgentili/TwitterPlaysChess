from flask import Flask, g, render_template, request, jsonify, url_for, Response
import chess, chess.uci
import time
from contextlib import closing
from werkzeug.contrib.cache import SimpleCache
import os
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import desc, func
import json

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
db = SQLAlchemy(app)
app.cache = SimpleCache()

import models

#DATABASE FUNCTIONS
def init_db():
    db.create_all()

def create_new_game():
    print "Creating new game!"
    game = models.Games( int(time.time()) )
    db.session.add(game)
    db.session.commit()
    g = get_last_game()
    start_pos = chess.STARTING_FEN
    update_pos_db( g, start_pos, 'None')
    return g, start_pos

def get_last_game():
    g = db.session.query(models.Games.id).order_by(desc(models.Games.id)).first()
    if g == None:
        return None
    return g[0]

def get_last_move(g):
    pos = db.session.query(models.Positions.pos).order_by(desc(models.Positions.id)).filter_by(game=g).first()
    if pos == None:
        return None
    return pos[0]

def query_state():
    g = get_last_game()
    if g == None:
        print "No game state"
        return (None, None)
    pos = get_last_move(g)
    if pos == None:
        print "No position state"
        return (g, None)
    return (g, pos)

def get_twitter_moves(last):
    new_last = db.session.query(models.TwitterMoves.id).order_by(desc(models.TwitterMoves.id)).first()
    print "Last was", last, "new last is", new_last
    if new_last == None:
        return None, None
    else:
        new_last = new_last[0]
    print "New last", new_last 
    moves = db.session.query(models.TwitterMoves.move,
            func.count(models.TwitterMoves.id).label('total')).filter(models.TwitterMoves.id
                    > last).filter(models.TwitterMoves.id <= new_last).group_by(models.TwitterMoves.move).order_by(desc('total')).all()
    return moves, new_last

def update_pos_db( game, pos, last_move):
    newpos = models.Positions( game, pos, last_move )
    db.session.add(newpos)
    db.session.commit()

def add_move_db(game, move, user, time):
    valid = models.TwitterMoves( game, move, user, time)
    db.session.add(valid)
    db.session.commit()

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
    create_new_game() 

@app.route("/get_position")
def get_position():
    rv = app.cache.get('position')
    if rv is None:
        _ , rv = query_state()
        app.cache.set('position', rv, timeout= 1)
    return jsonify(position=rv)  

@app.route("/get_counts")
def get_counts():
    moves = app.cache.get('counts')
    last = app.cache.get('last')
    last_move = -1
    if last is None:
        app.cache.set('last', -1, 1000)

    if moves is None:
        moves, new_last = get_twitter_moves(app.cache.get('last'))
        app.cache.set('counts', moves, timeout= 1)
        #app.cache.set('last', new_last, timeout=1000)

    print "moves are", moves
    print "jsonified", jsonify(moves)
    #return Response(json.dumps(moves), mimetype = 'application/json')
    return jsonify(aaData=moves)

if __name__ == "__main__":
    app.run(threaded=True)
