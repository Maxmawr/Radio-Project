from app import app
from flask import render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import os

basedir = os.path.abspath(os.path.dirname(__file__))
db = SQLAlchemy()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, "radio.db")
app.secret_key = 'correcthorsebatterystaple'
WTF_CSRF_ENABLED = True
WTF_CSRF_SECRET_KEY = 'sup3r_secr3t_passw3rd'
db.init_app(app)

import app.models as models
from app.forms import Filter_Brands, Add_Part

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


@app.route("/search", methods=['GET', 'POST'])
def search():
    results = []
    form = Filter_Brands()
    brands = models.Brand.query.all()
    form.partbrand.choices = [(b.id, b.name) for b in brands]
    if request.method=='POST':
        if form.validate_on_submit():
            selected_brand_id = form.partbrand.data
            results = models.Part.query.filter(models.Part.brand.any(id=selected_brand_id)).all()
    return render_template("search.html", form=form, results=results)


@app.route("/part/<int:id>")
def part(id):
    part = models.Part.query.filter_by(id=id).first_or_404()
    return render_template("part.html", part=part)


@app.route('/add_part', methods=['GET', 'POST'])
def add_part():
  form = Add_Part()
  if request.method=='GET':
    return render_template('add_part.html', form=form, title="Add A Part")
  else:
    if form.validate_on_submit():
      new_part = models.Part()
      new_part.name = form.name.data
      db.session.add(new_part)
      db.session.commit()
      return redirect(url_for('details', ref=new_part.id))
    else:
      # note the terrible logic, this has already been called once in this function - could the logic be tidied up?   
      return render_template('add_part.html', form=form, title="Add A Part")


if __name__ == "__main__":
    app.run(debug=True)
