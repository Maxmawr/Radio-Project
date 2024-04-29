from flask import Flask, render_template
# import sqlite3

database = "Music.db"

app = Flask(__name__)


# @app.errorhandler(404)
# def page_not_found(e):
#    return render_template('404.html'), 404


# Route for the home page
@app.route("/")
def home():
    return render_template("home.html")


if __name__ == "__main__":
    app.run(debug=True)
