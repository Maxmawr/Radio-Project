from wsgiref.validate import validator
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, FileField, IntegerField
from wtforms.validators import DataRequired, NumberRange
from flask_wtf.file import FileAllowed, FileRequired
import app.models
from datetime import datetime


class Search(FlaskForm):
    partbrand = SelectField('Brand', coerce=int)
    search = TextAreaField('Name')
    tag = SelectField('Tag', coerce=int)


class Add_Part(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    brand = SelectField('brand', validators=[DataRequired()], coerce=int)
    tags = TextAreaField('tags')
    sizenum = IntegerField('sizenum', validators=[NumberRange(min=0, message="Number must be non-negative")])
    type = SelectField('type', validators=[DataRequired()], coerce=int)
    image = FileField('Image', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Images only!')
    ])


class Search_Brand(FlaskForm):
    brand = SelectField('brand', coerce=int)
