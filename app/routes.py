"""
Flask Application for Part Management and Image Handling

This script defines a Flask web application that provides several routes for managing parts and brands, handling image uploads and transformations, and user authentication.

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
"""

import io
import csv
from app import app
from flask import make_response, render_template, request, redirect, url_for
from flask_caching import Cache
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from werkzeug.utils import secure_filename
import os
from PIL import Image as PIL_Image, ImageOps as PIL_ImageOps
from flask_login import LoginManager, login_user, logout_user, login_required
from flask_bcrypt import Bcrypt


# Configuration for file uploads and caching
UPLOAD_FOLDER = 'app/static/images'
app.config['CACHE_TYPE'] = 'filesystem'
app.config['CACHE_DIR'] = 'cache-directory'
cache = Cache(config={'CACHE_TYPE': 'SimpleCache'})
cache.init_app(app)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Setup SQLAlchemy
basedir = os.path.abspath(os.path.dirname(__file__))
db = SQLAlchemy()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, "radio.db")
app.secret_key = 'correcthorsebatterystaple'
WTF_CSRF_ENABLED = True
WTF_CSRF_SECRET_KEY = 'sup3r_secr3t_passw3rd'
db.init_app(app)

import app.models as models
from app.forms import Search, Add_Part, Search_Brand, Search_Tag

login_manager = LoginManager()
login_manager.init_app(app)

bcrypt = Bcrypt(app)

THUMB_SIZE = 160

MAX_URL_LENGTH = 2048

from app.models import Part, Brand, Type, Tag, Image
from faker import Faker
import random

fake = Faker()

# Error handler with 404 route
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.before_request
def limit_url_length():
    if len(request.url) > MAX_URL_LENGTH:
        return render_template('404.html'), 404


# Route for the home page
@app.route("/")
def home():
    return render_template("home.html")

@app.route('/add_test_data')
def add_test_data(num_records=1):
    with app.app_context():  # Ensure you have the app context
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
                    new_part.tags.append(tag)

            # Dummy image handling
            dummy_image_name = f"{fake.uuid4()}.jpg"
            new_image = Image(name=dummy_image_name)

            db.session.add(new_part)
            db.session.commit()
            db.session.add(new_image)
            db.session.commit()

        return f"{num_records} records added to the database."

# Route for brands page
@app.route("/brands", methods=['GET', 'POST'])
def brands():
    form = Search_Brand()
    brands = models.Brand.query.all()
    form.brand.choices = [(0, 'None')]
    form.brand.choices.extend((b.id, b.name) for b in brands)

    form_submitted = False

    if request.method == 'POST':
        form_submitted = True
        if form.validate_on_submit():
            brand = form.brand.data
            return redirect(url_for('search', brand=brand))
    
    results = []
    return render_template("brands.html", results=results, form=form, brands=brands, form_submitted=form_submitted)


# Route for showing all manufacturers
@app.route("/manufacturers")
def manufacturers():
    manufacturers = models.Manufacturer.query.all()
    return render_template("manufacturers.html", manufacturers=manufacturers)


# Route for showing all parts
@app.route("/all_parts", methods=['GET', 'POST'])
def all_parts():
    all_parts = models.Part.query.all()
    form = Search_Tag()
    tags = models.Tag.query.all()
    form.tag.choices = [(0, 'None')]
    form.tag.choices.extend((t.id, t.name) for t in tags)

    if request.method == 'POST' and form.validate_on_submit():
        tag = form.tag.data
        print(tag)
        return (redirect(url_for('search', tag=tag)))
    else:
        results = []
    return render_template("all_parts.html", all_parts=all_parts, results=results, form=form, tags=tags)


# Route for searching parts
@app.route("/search", methods=['GET', 'POST'])
def search():
    form = Search()
    brands = models.Brand.query.all()
    tags = models.Tag.query.all()
    tag_choices = [(0, 'None')]
    tag_choices.extend((t.id, t.name) for t in tags)
    form.tag.choices = tag_choices
    brand_choices = [(0, 'None')]
    brand_choices.extend((b.id, b.name) for b in brands)
    form.partbrand.choices = brand_choices

    # Get the 'brand' query parameter
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

            # Start with a base query
            query = models.Part.query

            # Add name search condition
            if search_term:
                query = query.filter(func.lower(models.Part.name).like(search_term))

            # Add brand search condition if partbrand_id is provided
            if partbrand_id:
                query = query.filter(models.Part.brands.any(id=partbrand_id))

            # Add tag search condition if tags are provided
            if tag_id:
                query = query.filter(models.Part.tags.any(id=tag_id))

            # Execute the query
            results = query.all()

    elif brand is not None:
        form.partbrand.data = brand
        results = models.Part.query.filter(models.Part.brands.any(id=brand)).all()

    elif tag is not None:
        form.tag.data = tag
        results = models.Part.query.filter(models.Part.tags.any(id=tag)).all()

    return render_template("search.html", form=form, results=results, form_submitted=form_submitted)


# Route for specific part page
@app.route("/part/<int:id>")
def part(id):
    part = models.Part.query.filter_by(id=id).first_or_404()
    images = models.Image.query.filter_by(part_id=part.id).first()
    return render_template("part.html", part=part, images=images)


# Route for the adding parts function
@app.route('/add_part', methods=['GET', 'POST'])
@login_required
def add_part():
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

            # Handle image upload
            if 'image' in request.files:
                image_file = request.files['image']
                if image_file.filename != '':
                    filename = secure_filename(image_file.filename)
                    image_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    new_image.name = filename  # Save filename to the database

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

            new_part.width = form.sizenum.data
            new_part.brands.append(brand)
            new_part.type_id = form.type.data

            db.session.add(new_part)
            db.session.commit()
            new_image.part_id = new_part.id
            db.session.add(new_image)
            db.session.commit()
            return redirect(url_for('part', id=new_part.id))

    return render_template('add_part.html', form=form, title="Add A Part", form_submitted=form_submitted)


# Route for thumbnail generation and caching
@app.route("/thumbnail/<int:id>")
@cache.cached(timeout=50)
def thumbnail(id):
    print(cache.get(f'thumbnail:{id}'))
    """This route delivers a scaled down thumbnail as a jpeg file"""
    image = models.Image.query.filter_by(part_id=id).first()
    filename = os.path.join(UPLOAD_FOLDER, image.name)
    # TODO: Deal with missing images

    full = PIL_Image.open(filename)
    thumb = PIL_ImageOps.fit(full, (THUMB_SIZE, THUMB_SIZE), PIL_Image.LANCZOS)

    buf = io.BytesIO()
    thumb.save(buf, format='JPEG')

    response = make_response(buf.getvalue())
    response.headers.set('Content-Type', 'image/jpeg')
    return response


# Route for exporting as a csv
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


# Route for logging in
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = models.Users.query.filter_by(
            username=request.form.get("username")).first()
        # Check if the password entered is the same as the user's password
        password = request.form.get("password")
        if bcrypt.check_password_hash(user.hashed_password, password):
            # Use the login_user method to log in the user
            login_user(user)
            return redirect(url_for("home"))
    return render_template("login.html")


# Route for registering a new account
@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = models.Users(username=username, password=password, hashed_password=hashed_password)

        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for("login"))

    return render_template("sign_up.html")


@login_manager.user_loader
def loader_user(user_id):
    return models.Users.query.get(user_id)


# Route for logging out
@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))
