"""
Flask Application for Part Management and Image Handling

This script defines a Flask web application that provides several routes for
managing parts and brands, handling image uploads and transformations,
and user authentication.

Key Features:
- Upload and process images (displayed as thumbnails and cached to disk).
- Manage parts with various attributes, including tags and brands.
- Search for parts based on different criteria.
- User authentication (login, register, and logout).
- CSRF protection and password hashing.

Dependencies:
- Flask: Core web framework.
- Flask-Caching: Caching support for Flask.
- Flask-SQLAlchemy: SQLAlchemy integration with Flask for ORM.
- Flask-Login: User session management.
- Flask-Bcrypt: Password hashing for secure authentication.
- Flask-WTF: Intergration of Flask and WTForms
- SQLAlchemy: SQL toolkit and Object Relational Mapper.
- Werkzeug: Utilities for handling file uploads.
- Pillow: Imaging library for image processing.
- io: For handling in-memory file streams.
- csv: For CSV file operations.
- os: For file path operations.

Required `pip` packages:
- Flask
- Flask-Bcrypt
- Flask-Caching
- Flask-Login
- Flask-SQLAlchemy
- Flask-WTF
- SQLAlchemy
- Werkzeug
- Pillow
- Faker
"""

import io
import csv
from app import app
from flask import make_response, render_template, request, redirect, url_for
from flask_caching import Cache
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from sqlalchemy.orm import selectinload
from werkzeug.utils import secure_filename
import os
from PIL import Image as PIL_Image
from flask_login import LoginManager, login_user, logout_user, login_required
from flask_bcrypt import Bcrypt
from faker import Faker
import random


fake = Faker()

UPLOAD_FOLDER = 'app/static/images'
app.config['CACHE_TYPE'] = 'filesystem'
app.config['CACHE_DIR'] = 'cache-directory'
cache = Cache(config={'CACHE_TYPE': 'SimpleCache'})
cache.init_app(app)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


basedir = os.path.abspath(os.path.dirname(__file__))
db = SQLAlchemy()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(
    basedir, "radio.db")
app.secret_key = 'correcthorsebatterystaple'
WTF_CSRF_ENABLED = True
WTF_CSRF_SECRET_KEY = 'sup3r_secr3t_passw3rd'
db.init_app(app)

import app.models as models
from app.forms import Search, Add_Part, Search_Brand, Search_Tag, Edit

login_manager = LoginManager()
login_manager.init_app(app)

bcrypt = Bcrypt(app)

THUMB_SIZE = 160

MAX_URL_LENGTH = 2048

from app.models import Part, Brand, Type, Tag, Image


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.before_request
def limit_url_length():
    if len(request.url) > MAX_URL_LENGTH:
        return render_template('404.html'), 404


@app.route("/")
def home():
    return render_template("home.html")


def generate_random_image(image_path):
    width, height = 200, 200
    color = tuple(random.randint(0, 255) for _ in range(3))

    img = PIL_Image.new('RGB', (width, height), color)
    img.save(image_path)


@app.route('/add_test_data')
@login_required
def add_test_data(num_records=1000):
    with app.app_context():
        brands = Brand.query.all()
        types = Type.query.all()

        for _ in range(num_records):
            new_part = Part()
            new_part.name = fake.catch_phrase()
            new_part.width = random.randint(1, 100)

            selected_brand = random.choice(brands)
            new_part.brands.append(selected_brand)

            selected_type = random.choice(types)
            new_part.type_id = selected_type.id

            tag_names = [fake.word() for _ in range(random.randint(1, 5))]
            for tag_name in tag_names:
                tag = Tag.query.filter_by(name=tag_name).first()
                if tag is None:
                    new_tag = Tag(name=tag_name)
                    db.session.add(new_tag)
                    db.session.commit()
                    new_part.tags.append(new_tag)
                else:
                    if tag not in new_part.tags:
                        new_part.tags.append(tag)

            dummy_image_name = f"{fake.uuid4()}.jpg"
            image_path = os.path.join(UPLOAD_FOLDER, dummy_image_name)

            generate_random_image(image_path)

            new_image = Image(name=dummy_image_name)
            new_image.part_id = new_part.id

            db.session.add(new_part)
            db.session.commit()
            new_image.part_id = new_part.id
            db.session.add(new_image)
            db.session.commit()

        return f"{num_records} records added to the database."


# Route for brands page
@app.route("/brands", methods=['GET', 'POST'])
def brands():
    form = Search_Brand()
    brands = models.Brand.query.order_by(func.lower(models.Brand.name)).all()
    form.brand.choices = [(0, 'None')]
    form.brand.choices.extend((b.id, b.name) for b in brands)

    form_submitted = False

    if request.method == 'POST':
        form_submitted = True
        if form.validate_on_submit():
            brand = form.brand.data
            return redirect(url_for('search', brand=brand))

    results = []
    return render_template("brands.html", results=results, form=form,
                           brands=brands, form_submitted=form_submitted)


@app.route("/manufacturers")
def manufacturers():
    manufacturers = models.Manufacturer.query.all()
    return render_template("manufacturers.html", manufacturers=manufacturers)


@app.route("/all_parts", methods=['GET', 'POST'])
@cache.cached(timeout=50)
def all_parts():
    all_parts = (
                models.Part.query.options(
                    selectinload(models.Part.brands),
                    selectinload(models.Part.tags),
                    selectinload(models.Part.type)
                )
                .all()
                )
    form = Search_Tag()
    tags = models.Tag.query.all()
    form.tag.choices = [(0, 'None')]
    form.tag.choices.extend((t.id, t.name) for t in tags)

    if request.method == 'POST' and form.validate_on_submit():
        tag = form.tag.data
        return (redirect(url_for('search', tag=tag)))
    else:
        results = []
    return render_template("all_parts.html", all_parts=all_parts,
                           results=results, form=form, tags=tags)


@app.route("/search", methods=['GET', 'POST'])
def search():
    """This route allows the user to search by filling out a selection
    of entries on the form.
    As of now, they can search by name, size, and brand.
    Any of the fields can be left blank, and they are not
    considered by the search."""
    form = Search()
    brands = models.Brand.query.order_by(func.lower(models.Brand.name)).all()
    tags = models.Tag.query.order_by(func.lower(models.Tag.name)).all()
    types = models.Type.query.order_by(func.lower(models.Type.name)).all()

    tag_choices = [(0, 'None')]
    tag_choices.extend((t.id, t.name) for t in tags)
    form.tag.choices = tag_choices

    brand_choices = [(0, 'None')]
    brand_choices.extend((b.id, b.name) for b in brands)
    form.partbrand.choices = brand_choices

    type_choices = [(0, 'None')]
    type_choices.extend((t.id, t.name) for t in types)
    form.type.choices = type_choices

    brand = request.args.get('brand', type=int)
    tag = request.args.get('tag', type=int)

    results = []
    form_submitted = False

    if request.method == 'POST':
        form_submitted = True
        if form.validate_on_submit():
            search_term = '%' + form.search.data.strip().lower() + '%'
            partbrand_id = form.partbrand.data
            tag_id = form.tag.data
            type_id = form.type.data
            width = form.width.data
            height = form.height.data

            query = models.Part.query

            if search_term:
                query = query.filter(func.lower(models.Part.name).like(
                    search_term))

            if partbrand_id:
                query = query.filter(models.Part.brands.any(id=partbrand_id))

            if tag_id:
                query = query.filter(models.Part.tags.any(id=tag_id))

            if type_id:
                query = query.filter(models.Part.type.has(id=type_id))

            if width is not None:
                min_width = width * 0.9
                max_width = width * 1.1
                query = query.filter(models.Part.width.between(
                    min_width, max_width))

            if height is not None:
                min_height = height * 0.9
                max_height = height * 1.1
                query = query.filter(models.Part.height.between(
                    min_height, max_height))

            results = query.all()

    elif brand is not None:
        form.partbrand.data = brand
        results = models.Part.query.filter(models.Part.brands.any(
            id=brand)).all()

    elif tag is not None:
        form.tag.data = tag
        results = models.Part.query.filter(models.Part.tags.any(id=tag)).all()

    return render_template("search.html", form=form, results=results,
                           form_submitted=form_submitted)


@app.route("/part/<int:id>")
def part(id):
    part = models.Part.query.filter_by(id=id).first_or_404()
    images = models.Image.query.filter_by(part_id=part.id).first()
    return render_template("part.html", part=part, images=images)


@app.route('/add_part', methods=['GET', 'POST'])
@login_required
def add_part():
    """This route is for adding new parts to the database.
    It takes each entry from the form and puts them together
    into a part that gets comitted.
    Two commits are used because otherwise the image is not
    assigned to the part."""

    form = Add_Part()

    brands = models.Brand.query.all()
    form.brand.choices = [(b.id, b.name) for b in brands]

    types = models.Type.query.all()
    form.type.choices = [(t.id, t.name) for t in types]

    form_submitted = False

    if request.method == 'POST':
        form_submitted = True
        if form.validate_on_submit():
            selected_brand_id = form.brand.data
            brand = models.Brand.query.filter_by(id=selected_brand_id).first()

            new_part = models.Part()
            new_image = models.Image()

            new_part.name = form.name.data

            if 'image' in request.files:
                image_file = request.files['image']
                if image_file.filename != '':
                    filename = secure_filename(image_file.filename)
                    image_file.save(os.path.join(app.config['UPLOAD_FOLDER'],
                                                 filename))
                    new_image.name = filename

            taglist = form.tags.data.split(",")
            for t in taglist:
                tag = models.Tag.query.filter_by(name=t).first()
                if tag is None:
                    new_tag = models.Tag()
                    new_tag.name = t.strip()
                    db.session.add(new_tag)
                    db.session.commit()
                    tag = models.Tag.query.filter_by(name=t).first()
                new_part.tags.append(tag)

            new_part.width = form.width.data
            new_part.height = form.height.data
            new_part.brands.append(brand)
            new_part.type_id = form.type.data

            db.session.add(new_part)
            db.session.commit()
            new_image.part_id = new_part.id
            db.session.add(new_image)
            db.session.commit()
            return redirect(url_for('part', id=new_part.id))

    return render_template('add_part.html', form=form, title="Add A Part",
                           form_submitted=form_submitted)


@app.route("/thumbnail/<int:id>")
@cache.cached(timeout=50)
def thumbnail(id):
    """This route delivers a scaled down thumbnail as a jpeg file.
    It checks if the thumnail has been generated, if not it creates the
    thumbnail and caches it to disk."""
    image = models.Image.query.filter_by(part_id=id).first()

    filename = os.path.join(UPLOAD_FOLDER, image.name)

    full = PIL_Image.open(filename)

    thumb = full.copy()
    thumb.thumbnail((THUMB_SIZE, THUMB_SIZE), PIL_Image.LANCZOS)

    buf = io.BytesIO()
    thumb.save(buf, format='JPEG')
    buf.seek(0)

    response = make_response(buf.getvalue())
    response.headers.set('Content-Type', 'image/jpeg')
    return response


@app.route("/export")
@login_required
def export():
    # TODO: Export all fields
    all_parts = models.Part.query.all()

    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["name"])
    for part in all_parts:
        row = [part.name]
        w.writerow(row)
    response = make_response(buf.getvalue())
    response.headers.set('Content-Type', 'text/csv')
    response.headers.set(
        'Content-Disposition', 'attachment', filename="all_parts.csv")
    return response


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = models.Users.query.filter_by(
            username=request.form.get("username")).first()
        password = request.form.get("password")
        if bcrypt.check_password_hash(user.hashed_password, password):
            login_user(user)
            return redirect(url_for("home"))
    return render_template("login.html")


@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        hashed_password = bcrypt.generate_password_hash(
            password).decode('utf-8')
        new_user = models.Users(username=username,
                                hashed_password=hashed_password)

        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for("login"))

    return render_template("sign_up.html")


@app.route("/delete/<int:id>")
def delete(id):
    part = models.Part.query.filter_by(id=id).first_or_404()
    return render_template("delete.html", part=part)


@app.route("/delete_confirm/<int:id>", methods=['GET', 'POST'])
def delete_confirm(id):
    part = models.Part.query.filter_by(id=id).first_or_404()
    db.session.delete(part)
    db.session.commit()
    print("deleted", part)
    return redirect(url_for("all_parts"))


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_part(id):
    part = models.Part.query.filter_by(id=id).first_or_404()
    form = Edit(request.form, obj=part)

    brands = models.Brand.query.all()
    form.brand.choices = [(b.id, b.name) for b in brands]

    types = models.Type.query.all()
    form.type.choices = [(t.id, t.name) for t in types]

    if form.validate_on_submit():
        form.populate_obj(part)
        db.session.commit()
        return redirect(url_for('part', id=id))
    return render_template('edit.html', **locals())


@login_manager.user_loader
def loader_user(user_id):
    return models.Users.query.get(user_id)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))
