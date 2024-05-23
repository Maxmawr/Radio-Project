from app import app
from flask import render_template
from flask_sqlalchemy import SQLAlchemy
import os

basedir = os.path.abspath(os.path.dirname(__file__))
db = SQLAlchemy()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, "radio.db")
db.init_app(app)

import app.models as models

# import sqlite3


# @app.errorhandler(404)
# def page_not_found(e):
#    return render_template('404.html'), 404


# Route for the home page
@app.route("/")
def home():
    return render_template("home.html")


@app.route("/brands")
def brands():
    brands = models.Brand.query.all()
    return render_template("brands.html", brands=brands)


@app.route("/manufacturers")
def manufacturers():
    manufacturers = models.Manufacturer.query.all()
    return render_template("manufacturers.html", manufacturers=manufacturers)


@app.route("/all_parts")
def all_parts():
    all_parts = models.Part.query.all()
    return render_template("all_parts.html", all_parts=all_parts)


if __name__ == "__main__":
    app.run(debug=True)
