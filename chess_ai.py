import chess, chess.uci
import time
import sqlite3
from tpc import db
import tpc

from models import Games, Positions

ENGINE_URL = 'static/stockfish'
MOVETIME = 1000 # time in msec for engine to think
PAUSE = 1 # time in sec between each AI move

class ChessGame():
    def __init__(self):
        self.engine = chess.uci.popen_engine(ENGINE_URL)
        self.engine.uci()     
        
        self.game, self.pos = tpc.query_state()
        print "Initial state is", self.game, self.pos
        if self.game == None:
            self.new_game()
        self.board = chess.Board(self.pos)
        
        self.engine.position(self.board)

    def new_game(self):
        game = Games( int(time.time()) ) 
        db.session.add(game)
        db.session.commit()
        
        self.game, _ = tpc.query_state()
        self.board = chess.Board()
        self.engine.position(self.board)
        self.pos = self.board.fen()

        self.update_pos_db(self.game, self.pos)

    def update_pos_db(self, game, pos):
        newpos = Positions( game, pos )
        db.session.add(newpos)
        db.session.commit()
         
    def make_move(self, move):
        self.board.push(move[0])
        self.engine.position(self.board)
        self.pos = self.board.fen()

    def game_end_condition(self):
        b = self.board
        return (b.is_checkmate() or b.is_stalemate() or
    b.is_insufficient_material() or b.is_fivefold_repitition() or
    b.is_seventyfive_moves())

    def ai_game(self):
        while not self.game_end_condition():
            move = self.engine.go(movetime=MOVETIME)
            print move
            self.make_move(move)
            self.update_pos_db(self.game, self.pos)
            time.sleep(PAUSE)

    def ai_loop(self):
        while True:
            self.ai_game()
            self.new_game()

if __name__ == "__main__":
    game = ChessGame()
    game.ai_loop()
