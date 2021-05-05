from flask import render_template, url_for, flash, redirect, request, session, jsonify
from book_review import app, db, bcrypt
from book_review.forms import RegistrationForm, LoginForm, Postform
from book_review.__init__ import db
from book_review.forms import RegistrationForm, LoginForm
from book_review.models import User, Review, Book
from flask_login import login_user, current_user, logout_user, login_required
import json
import requests
from flask import jsonify

posts = Book.query.all()

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', posts=posts)


@app.route("/about")
def about():
    return render_template('about.html', title='About')


# @app.route("/review", methods=['GET','POST'])
# def review():
#     if request.method == "POST":
#         searchQuery = request.form.get("searchQuery")
#         print(searchQuery)

#         # Avoid SQL Injection Using Bindings
#         sql = "SELECT isbn, author, title \
#                FROM Book \
#                WHERE isbn LIKE :x \
#                OR author LIKE :y \
#                OR title LIKE :z"

#         # I spent an hour wondering why I couldnt put the bindings inside the wildcard string...
#         # https://stackoverflow.com/questions/3105249/python-sqlite-parameter-substitution-with-wildcards-in-like
#         matchString = "%{}%".format(searchQuery)

#         stmt = db.text(sql).bindparams(x=matchString, y=matchString, z=matchString)

#         results = db.session.execute(stmt).fetchall()
#         print(results)

#         session["books"] = []

#         for row in results:
#             # A row is not JSON serializable so we pull out the pieces
#             book = dict()
#             book["isbn"] = row[0]
#             book["author"] = row[1]
#             book["title"] = row[2]
#             session["books"].append(book)
#         return render_template("review.html", searchedFor=searchQuery, books=session["books"])

#     return render_template("review.html", title='Review')


@app.route("/book/api/<string:isbn>")
def api(isbn): 
    data = "SELECT isbn, author, title \
               FROM Book \
               WHERE isbn LIKE :x \
               OR author LIKE :y \
               OR title LIKE :z"
    if data==None:
        return render_template('404.html')

    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "YegUTeGTeZBfvDwYok7xg", "isbns": isbn})
    average_rating=res.json()['Book'][0]['average_rating']
    work_ratings_count=res.json()['Book'][0]['work_ratings_count']
    x = {
    "title": data.title,
    "author": data.author,
    "year": data.year,
    "isbn": isbn,
    "review_count": work_ratings_count,
    "average_rating": average_rating
    }

    return jsonify(x)
    # api = json.dumps(x)
    # return render_template("api.json",api=api)


@app.route("/review/<isbn>" ,methods=["POST","GET"])
@login_required
def review(isbn):
    form = Postform()

    isbn = isbn

    apiCall = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "YegUTeGTeZBfvDwYok7xg", "isbns": isbn })
    apidata = apiCall.json()
    dbdata = db.execute(" SELECT * FROM Book WHERE isbn = :isbn", {"isbn": isbn}).fetchall()
    dbreviews = db.execute('SELECT * FROM Review WHERE book_id = :isbn', {'book_id': isbn}).fetchall()

    alreadyHasReview = db.execute('SELECT * FROM Review WHERE book_id = :isbn and user_id = :email ', {'book_id': isbn, 'user_id': email}).fetchall()
    if request.method == 'POST':
        if alreadyHasReview:  
            flash('You alreaddy submitted a review on this book')
        else: 
            rating = int(request.form['rating'])
            comment = request.form['comment']
            email = session['email']
            fisbn = isbn
            db.execute("INSERT into Review (user_id, rating, review, book_id) Values (:user_id, :rating, :review, :book_id)", {'user_id': email, 'rating': rating, 'review': comment, 'book_id': fisbn})
            db.commit()
            flash('Awesome, Your review added successfully ')
        
    if apiCall:
        return render_template('singlebook.html', apidata = apidata, dbdata = dbdata, dbreviews = dbreviews, isbn = isbn )
    else:
        flash('Data fetch failed')
        return render_template('singlebook.html')
        
    return render_template('singlebook.html', title='Review')


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))