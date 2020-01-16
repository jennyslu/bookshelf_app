from sqlalchemy import Column, Integer, String

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def setup_db(app):
    '''
    binds a flask application and a SQLAlchemy service
    '''
    # ensure it is the same db being used by models
    db.app = app
    db.init_app(app)
    db.create_all()


class Book(db.Model):
    __tablename__ = 'books'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    author = Column(String)
    rating = Column(Integer)

    def __init__(self, id, title, author, rating):
        self.id = id
        self.title = title
        self.author = author
        self.rating = rating

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'rating': self.rating,
        }
