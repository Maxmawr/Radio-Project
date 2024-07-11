from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, FileField
from wtforms.validators import DataRequired, Optional, ValidationError
from flask_wtf.file import FileAllowed, FileRequired
import app.models
from datetime import datetime

class Search(FlaskForm):
    partbrand = SelectField('Brand', coerce=int)
    search = TextAreaField('Name')

class Add_Part(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    brand = SelectField('brand', validators=[DataRequired()], coerce=int)
    tags = TextAreaField('tags')
    type = SelectField('type', validators=[DataRequired()], coerce=int)
    image = FileField('Image', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Images only!')
    ])