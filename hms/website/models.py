from time import timezone
from . import db
# from datetime import datetime
from sqlalchemy.sql import func

# class Note(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     data = db.Column(db.String(10000))
#     date = db.Column(db.DateTime(timezone=True), default=func.now())
#     para_id = db.Column(db.Integer, db.ForeignKey('para.id'))

class Predicted(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ph = db.Column(db.Float)
    wt = db.Column(db.Float)
    ec = db.Column(db.Float)
    nb = db.Column(db.Integer)
    svm = db.Column(db.Integer)
    date = db.Column(db.DateTime(), default=func.now())

class Status(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.Integer, unique=True)
    title = db.Column(db.String(255))
    recommend = db.Column(db.Text())
    source = db.Column(db.Text())


class Para(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ph = db.Column(db.Float)
    ph_s = db.Column(db.Integer)
    wt = db.Column(db.Float)
    wt_s = db.Column(db.Integer)
    ec = db.Column(db.Float)
    ec_s = db.Column(db.Integer)
    status = db.Column(db.Integer)

    # def __init__(self,ph, wt, ec):
    #     self.ph = ph
    #     self.wt = wt
    #     self.ec = ec