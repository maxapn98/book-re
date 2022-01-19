import os
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env


app = Flask(__name__)



app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")



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


@app.route('/library')
def librarypage():
    """
    Returns library page
    """
    return render_template("library.html")


@app.route('/login')
def loginpage():
    """
    Returns login page
    """
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def registerpage():
    return render_template("register.html")


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)

