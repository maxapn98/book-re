import os
from functools import wraps
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from bson.json_util import dumps, loads
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env


app = Flask(__name__)


app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")


mongo = PyMongo(app)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('user') is None:
            return redirect('/login',code=302)
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
def homepage():
    """
    Returns home page
    """
    return render_template("home.html")


@app.route('/contact')
def contactpage():
    """
    Returns contact page
    """
    return render_template("contact.html")


@app.route('/search_book', methods=["GET", "POST"])
def search_book():
    """
    Search mongo.books by using query
    """
    if request.method == "POST":
        search_query = request.form.get("searchQuery")
        if not search_query:
            return redirect(url_for("librarypage"))
        
        queried = mongo.db.books.aggregate([{
            "$search": {
                'index': 'searchBooks',
                'text': {
                    'path': ["bookName", "bookDesc"],
                    'query': search_query,
                },
                'highlight': {"path": "bookName"},
            }
        }])

        return render_template("library.html", books=queried, query_word=search_query)

    return redirect(url_for("librarypage"))


@app.route('/library')
def librarypage():
    """
    Returns library page
    """
    print(mongo.db.books.find())
    return render_template("library.html", books=mongo.db.books.find())


@app.route("/add_book", methods=["GET", "POST"])
@login_required
def add_book():
    """
    Returns add_book page
    """

    if request.method == "POST":
        new_book = {
            "bookName": request.form.get("bookName").lower(),
            "bookImgUrl": request.form.get("bookImgUrl"),
            "bookDesc": request.form.get("bookDesc"),
            }
        mongo.db.books.insert_one(new_book)
        return redirect(url_for("librarypage"))

    return render_template("add-book.html")


@app.route("/delete_book/<book_id>", methods=["GET","POST"])
@login_required
def delete_book(book_id):
    """
    Delete book from mongoDB
    """
    mongo.db.books.delete_one({"_id": ObjectId(book_id)})
    return redirect(url_for("librarypage"))


@app.route("/update_book/<book_id>", methods=["GET", "POST"])
@login_required
def update_book(book_id):
    """
    Update book information
    """
    if request.method == "POST":
        updated_book = {
            "bookName": request.form.get("bookName").lower(),
            "bookImgUrl": request.form.get("bookImgUrl"),
            "bookDesc": request.form.get("bookDesc"),
            }

        mongo.db.books.update_one({"_id": ObjectId(book_id)}, {"$set": updated_book})
        return redirect(url_for("librarypage"))

    book = mongo.db.books.find_one({"_id": ObjectId(book_id)})
    return render_template("update-book.html", book=book)


@app.route("/book/<book_id>")
def book_page(book_id):
    """
    Returns book page
    """
    book_reviews = mongo.db.reviews.find({"_book_id": ObjectId(book_id)})
    book = mongo.db.books.find_one({"_id": ObjectId(book_id)})
    if session.get('user'):
        user = mongo.db.users.find_one({"_id": ObjectId(session['user']["_id"])})
        del user["password"]
    else:
        user = None
    return render_template('book-page.html', book=book, reviews=book_reviews, user=user)


@app.route("/add_book_review/<book_id>", methods=["POST", "GET"])
@login_required
def add_book_review(book_id):
    if request.method == "POST":
        user = session['user']

        book_review = {
            "username": user["username"],
            "_user_id": ObjectId(user["_id"]),
            "_book_id": ObjectId(book_id),
            "context": request.form.get("reviewComment"),
        }

        mongo.db.reviews.insert_one(book_review)
        return redirect(url_for("book_page", book_id=book_id))
    
    return redirect(url_for("book_page", book_id=book_id))


@app.route("/delete_book_review/<review_id>", methods=["POST", "GET"])
@login_required
def delete_book_review(review_id):
    """
    Delete book review
    """
    user_id = ObjectId(session['user']['_id'])
    review = mongo.db.reviews.find_one({'_id': ObjectId(review_id)})
    if user_id == review["_user_id"]:
        mongo.db.reviews.delete_one(review)

    return redirect(url_for('book_page', book_id=review["_book_id"]))


@app.route("/update_book_review/<review_id>", methods=["GET", "POST"])
@login_required
def update_book_review(review_id):
    """
    Update book review
    """
    user_id = ObjectId(session['user']['_id'])
    review = mongo.db.reviews.find_one({'_id': ObjectId(review_id)})
    if user_id == review["_user_id"] and request.method == "GET":
        return render_template("update-review.html", review=review)

    if user_id == review["_user_id"] and request.method == "POST":
        review["context"] = request.form.get("reviewText")
        mongo.db.reviews.update_one({"_id": ObjectId(review_id)}, {"$set": review})
        return redirect(url_for("book_page", book_id=review["_book_id"]))

    return redirect(url_for("book_page", book_id=review["_book_id"]))
    


@app.route('/profile/<username>', methods=["GET", "POST"])
@login_required
def profilepage(username):
    """
    Profile page functionality
    """
    user = mongo.db.users.find_one({"_id": ObjectId(session["user"]["_id"])})
    del user['password']

    if session['user']:
        return render_template("profile.html",user=user)

    return redirect(url_for('login'))


@app.route('/logout')
@login_required
def logout():
    """
    Logout functionality
    """
    flash("You have been logged out")
    session.pop('user')
    return redirect(url_for("loginpage"))


@app.route('/login', methods=["GET", "POST"])
def loginpage():
    """
    Login page and login functionality
    """
    if request.method == "POST":
        # check if username exists in db
        existing_user = mongo.db.users.find_one({"username": request.form.get("username").lower()})

        if existing_user:
            # ensure hashed password matches user input
            if check_password_hash(existing_user["password"], request.form.get("password")):
                    del existing_user["password"]
                    existing_user["_id"] = str(existing_user["_id"])
                    session["user"] = loads(dumps(existing_user))
                    flash("Welcome, {}".format(request.form.get("username")))
                    return redirect(url_for('profilepage', username=session["user"]))
            else:
                # invalid password match
                flash("Incorrect Username and/or Password")
                return redirect(url_for("loginpage"))

        else:
            # username doesn't exist
            flash("Incorrect Username and/or Password")
            return redirect(url_for("loginpage"))

    return render_template("login.html")



@app.route("/register", methods=["GET", "POST"])
def registerpage():
    """
    Register page functionality
    """
    if request.method == "POST":
        # check if username already exists in db
        existing_user = mongo.db.users.find_one({"username": request.form.get("username").lower()})

        if existing_user:
            flash("Username already exists")
            return redirect(url_for("registerpage"))

        register = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }

        mongo.db.users.insert_one(register)
        new_user = mongo.db.users.find_one({"username": register["username"]})
        del new_user["password"]
        new_user['_id'] = str(new_user['_id'])

        # put the new user into 'session' cookie
        session["user"] = loads(dumps(new_user))
        flash("Registration Successful!")
        return redirect(url_for('profilepage', username=session["user"]))
    return render_template("register.html")


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)