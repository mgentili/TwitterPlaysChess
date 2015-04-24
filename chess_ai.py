import chess, chess.uci
import time
import sqlite3
import tpc

ENGINE_URL = 'static/stockfish'
THINKTIME = 2000 # time in msec for engine to think
TWITTERTIME = 3 # time in sec between each twitter aggregated move

class ChessGame():
    def __init__(self):
        self.engine = chess.uci.popen_engine(ENGINE_URL)
        self.engine.uci()     
        print self.engine.name 
        self.game, self.pos = tpc.query_state()
        print "Initial state is", self.game, self.pos
        if self.game == None:
            self.new_game()
        self.board = chess.Board(self.pos)
        self.last = -1
        self.engine.position(self.board)
        print "Finished init"

    def new_game(self):
        self.game, self.pos = tpc.create_new_game()
        self.board = chess.Board(self.pos)
        self.engine.position(self.board)

    def make_move(self, move):
        print "Making move", move
        self.board.push(move)
        self.engine.position(self.board)
        self.pos = self.board.fen()
        tpc.update_pos_db(self.game, self.pos, str(move))

    def game_end_condition(self):
        b = self.board
        return (b.is_checkmate() or b.is_stalemate() or
    b.is_insufficient_material() or b.is_fivefold_repitition() or
    b.is_seventyfive_moves())

    def is_twitter_move(self):
        return (self.board.turn is chess.WHITE)
    
    def get_first_valid_move(self, moves):
        if moves == None or moves == []:
            return None
        else:
            i = 0
            while i < len(moves) and (chess.Move.from_uci(moves[i][0]) not in
                    self.board.legal_moves):
                i += 1
            if i == len(moves):
                print "No valid move inputted yet!"
                return None
            else:
                return chess.Move.from_uci(moves[i][0])

    def ai_game(self):
        while not self.game_end_condition():
            move = None
            if not self.is_twitter_move():
                print "Ai move start"
                move = self.engine.go(movetime=THINKTIME)[0]
                print "Ai move", move
                self.make_move(move)
            else:
                print "Twitter move start"
                time.sleep(TWITTERTIME)
                moves, last_move = tpc.get_twitter_moves(self.last)
                self.last = last_move
                print "Twitter moves are", moves
                move = self.get_first_valid_move(moves)
                print "Twitter chosen move is", move
                if move == None: # get ai move
                    move = self.engine.go(movetime=THINKTIME)[0]
                    print "No move, so generating random one", move
                self.make_move(move)

    def ai_loop(self):
        while True:
            self.ai_game()
            self.new_game()

if __name__ == "__main__":
    game = ChessGame()
    game.ai_loop()
