import chess, chess.uci
import time
import sqlite3
import tpc

ENGINE_URL = 'static/stockfish'
MOVETIME = 2000 # 2 seconds for engine to think
PAUSE = 4 # 4 seconds between each AI move

class ChessGame():
    def __init__(self):
        self.engine = chess.uci.popen_engine(ENGINE_URL)
        self.engine.uci()
        self.board = chess.Board()
        self.engine.position(self.board)
        currstate = tpc.with_context(lambda: tpc.query_state())
        print currstate
        self.game = currstate['game']
        self.pos = currstate['pos']
    
    def ai_game(self):
        while not self.board.is_checkmate():
            move = self.engine.go(movetime=MOVETIME)
            print move
            self.board.push(move[0])
            self.engine.position(self.board)
            newpos = self.board.fen()
            create_move_query = """insert into moves (game, pos) values
            (?,?)"""
            tpc.with_context(lambda: tpc.insert_db(create_move_query,
                args=(self.game,newpos,)))
            self.pos = newpos 
            time.sleep(PAUSE)

    def ai_loop(self):
        while True:
            if self.game == None:
                create_game_query = """insert into games (starttime) values
                (?)"""
                tpc.with_context(lambda:
                    tpc.insert_db(create_game_query,args=(int(time.time()),)))
                self.game = tpc.with_context(lambda: tpc.query_state())['game']
            self.ai_game()

if __name__ == "__main__":
    game = ChessGame()
    game.ai_loop()
