import tweepy
import pprint
import json
import sys
import tpc
import chess
import helpers
file = open('test.txt', 'a')

consumerKey = "xJYD61CtdkrPBEfSv37cSAUXv"
consumerSecret = "3RHmmCwfe0Jqpl5GNlBmMyfim5GXu2QzPklPYUuVl1DXaafT0i"
accessKey = "956669833-AHtkEW0MDLbqjtkwQ3tVnkbXDRdd0iTAUHXMPA0j"
accessSecret = "OHit4o8twNUEXAGI8UyXuHkgyf0ohQ6OFZuCCH3H7Ae6c"
keyword = '#TwitterPlaysChess'

auth = tweepy.OAuthHandler(consumerKey, consumerSecret)
auth.set_access_token(accessKey, accessSecret)
api = tweepy.API(auth)

class MoveListener(tweepy.StreamListener):
    def on_status(self, status):
        print(status.text)

    def on_data(self, data):
        json_data = json.loads(data)
        move = json_data['text'].split(" ")[0]
        user = json_data['user']['screen_name']
        time = json_data['created_at'][11:18]

        game, pos = tpc.query_state()
        temp = chess.Board(pos)

        print move
        
        if user == 'plays_chess': #always allow our tweets
            tpc.add_move_db( game, move, user, time)
        elif helpers.move_ok(move[:4]): #move is four characters long
            tpc.add_move_db( game, move[:4], user, time)
            print "New move", move[:4]
        elif move[:7] == "newgame": #or move is to create a new game
            tpc.add_move_db( game, move[:7], user, time)
            print "New game move!", move[:7]
        else:
            print "Not valid :-("

    def on_error(self, status_code):
        print >> sys.stderr, 'Encountered error with status code:', status_code
        return True

    def on_timeout(self):
        print >> sys.stderr, 'Timeout...'
        return True

if __name__ == "__main__":
    print "Now listening for ", keyword
    sapi = tweepy.streaming.Stream(auth, MoveListener())
    sapi.filter(track=[keyword])
    print "hi"
