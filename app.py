import os
from flask import Flask, render_template
if os.path.exists("env.py"):
    import env

app = Flask(__name__)

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


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)

