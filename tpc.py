from flask import Flask, render_template, request, jsonify, url_for
import chess, chess.uci
import time
app = Flask(__name__)

engine = None
board = chess.Board()
MOVETIME = 2000 # 2 seconds for engine to think
PAUSE = 4 # 4 seconds between each AI move

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
    global engine, board
    engine_url = 'static/stockfish'
    print engine_url
    engine = chess.uci.popen_engine(engine_url)
    print "Engine uci is", engine.uci()
    print engine.name
    board = chess.Board()
    engine.position(board)

@app.route("/ai_game")
def ai_game():
    if not engine == None:
        return
    new_game()
    while not board.is_checkmate():
        move = engine.go(movetime=2000)
        print move
        board.push(move[0])
        engine.position(board)
        time.sleep(PAUSE)

@app.route("/get_position")
def get_position():
    return jsonify(position=board.fen())  

if __name__ == "__main__":
    #app.run(host='0.0.0.0')
    app.run(threaded=True,debug=True)
