import io, csv
from app import app
from flask import make_response, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, and_
from werkzeug.utils import secure_filename
import os
from PIL import Image, ImageOps

UPLOAD_FOLDER = 'app/static/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

basedir = os.path.abspath(os.path.dirname(__file__))
db = SQLAlchemy()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, "radio.db")
app.secret_key = 'correcthorsebatterystaple'
WTF_CSRF_ENABLED = True
WTF_CSRF_SECRET_KEY = 'sup3r_secr3t_passw3rd'
db.init_app(app)

import app.models as models
from app.forms import Search, Add_Part

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
    form = Search()
    brands = models.Brand.query.all()
    results = []
    brand_choices = [(0, 'N/A')]
    brand_choices.extend((b.id, b.name) for b in brands)
    form.partbrand.choices = brand_choices

    if request.method == 'POST' and form.validate_on_submit():
        search_term = '%' + form.search.data.lower() + '%'
        partbrand_id = form.partbrand.data

        if partbrand_id == 0:
            results = models.Part.query.filter(
                func.lower(models.Part.name).like(search_term)
            ).all()
        else:
            results = models.Part.query.filter(
                and_(
                    func.lower(models.Part.name).like(search_term),  # Case insensitive search
                    models.Part.brands.any(id=partbrand_id)
                )
            ).all()
    return render_template("search.html", form=form, results=results)


@app.route("/part/<int:id>")
def part(id):
    part = models.Part.query.filter_by(id=id).first_or_404()
    images = models.Image.query.filter_by(part_id=part.id).all()
    return render_template("part.html", part=part, images=images)


@app.route('/add_part', methods=['GET', 'POST'])
def add_part():
    form = Add_Part()

    brands = models.Brand.query.all()
    form.brand.choices = [(b.id, b.name) for b in brands]

    types = models.Type.query.all()
    form.type.choices = [(t.id, t.name) for t in types]

    if request.method == 'GET':
        return render_template('add_part.html', form=form, title="Add A Part")
    else:
        if form.validate_on_submit():
            selected_brand_id = form.brand.data
            # Might cause crashes, check for valid data
            brand = models.Brand.query.filter_by(id=selected_brand_id).first()
            # print(type(selected_brand_id))

            new_part = models.Part()

            # assigning new part's name
            new_part.name = form.name.data

        # Handle image upload
        if 'image' in request.files:
            image_file = request.files['image']
            if image_file.filename != '':
                filename = secure_filename(image_file.filename)
                image_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                new_part.image = filename  # Save filename to the database

            # Adding tags
            taglist = form.tags.data.split(",")
            for t in taglist:
                tag = models.Tag.query.filter_by(name=t).first()
                if tag is None:
                    new_tag = models.Tag()
                    new_tag.name = t
                    db.session.add(new_tag)
                    db.session.commit()
                    tag = models.Tag.query.filter_by(name=t).first()
                new_part.tags.append(tag)

            # Assigning new part's brand
            new_part.brands.append(brand)

            # new_part.type = form.type.data

            db.session.add(new_part)
            db.session.commit()
            return redirect(url_for('part', id=new_part.id))
        else:
            # note the terrible logic, this has already been called once in this function - could the logic be tidied up?
            return render_template('add_part.html', form=form, title="Add A Part")


@app.route("/thumbnail/<int:id>")
def thumbnail(id):
    """This route delivers a scaled down thumbnail as a jpeg file"""
    image = models.Image.query.filter_by(part_id=id).first()
    filename = os.path.join(UPLOAD_FOLDER, image.name)
    # TODO: Cache thumbnails to disc
    # TODO: Deal with missing images

    # response.headers.set(
    #     'Content-Disposition', 'attachment', filename=image.name)
    full = Image.open(filename)
    thumb = ImageOps.fit(full, (100, 100), Image.LANCZOS)

    buf = io.BytesIO()
    thumb.save(buf, format='JPEG')

    response = make_response(buf.getvalue())
    response.headers.set('Content-Type', 'image/jpeg')
    return response

@app.route("/export")
def export():
    """Exports all the parts as a csv file"""
    # TODO: This should only be admin
    # TODO: Export all fields
    allparts = models.Part.query.all()

    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["name"])
    for part in allparts:
        row = [part.name]
        w.writerow(row)
    response = make_response(buf.getvalue())
    response.headers.set('Content-Type', 'text/csv')
    response.headers.set(
    'Content-Disposition', 'attachment', filename="all_parts.csv")
    return response

if __name__ == "__main__":
    app.run(debug=True)
