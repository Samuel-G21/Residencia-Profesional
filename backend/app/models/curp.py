from . import db

class Curp(db.Model):
    __tablename__ = 'curps'
    ficha = db.Column(db.String(50), primary_key=True)
    curp = db.Column(db.String(18), nullable=False)
