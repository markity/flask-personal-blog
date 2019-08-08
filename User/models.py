from flask_sqlalchemy import SQLAlchemy
from config import con

db = SQLAlchemy(con.app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False, unique=True)
    username = db.Column(db.String(32), nullable=False, unique=False)
    email = db.Column(db.String(128), nullable=True, unique=True)

    def add_with_save(self):
        db.session.add(self)
        db.session.commit()
