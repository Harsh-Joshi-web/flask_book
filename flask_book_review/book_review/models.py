from book_review import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    
    reviews = db.relationship('Review', backref='user', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

class Review(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False, primary_key=True)
    review = db.Column(db.String, nullable=False)
    rating = db.Column(db.Integer, nullable=False) 

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    isbn = db.Column(db.String(20), unique=True, nullable=False)
    title = db.Column(db.String(20), nullable=False)
    author = db.Column(db.String(20), nullable=False)
    year = db.Column(db.CHAR(4), nullable=False)

    reviews = db.relationship('Review', backref='book', lazy=True)