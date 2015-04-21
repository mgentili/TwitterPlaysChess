from tpc import db
#from sqlalchemy.dialects.postgresql import JSON

class Games(db.Model):
    __tablename__ = 'games'

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.Integer)
    
    def __init__(self, start_time):
        self.start_time = start_time

    def __repr__(self):
        return '<id {}, start_time {}>'.format(self.id, self.start_time)


class Positions(db.Model):
    __tablename__ = 'positions'

    id = db.Column(db.Integer, primary_key=True)
    game = db.Column(db.Integer)
    pos = db.Column(db.String())

    def __init__(self, game, pos):
        self.game = game
        self.pos = pos

    def __repr__(self):
        return '<id {}, game {}, pos {}>'.format(self.id, self.game, self.pos)
