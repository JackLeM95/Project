from app import db
from flask_login import UserMixin


class User(UserMixin, db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    pwd = db.Column(db.String(300), nullable=False, unique=True)
    information = db.Column(db.String(400), unique=True, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username
        return '<User %r>' % self.information

if __name__ == '__main__':
    db.create_all()
