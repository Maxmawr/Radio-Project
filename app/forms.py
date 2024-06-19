from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Optional, ValidationError
import app.models
from datetime import datetime

class Search(FlaskForm):
    partbrand = SelectField('partbrand', validators=[DataRequired()], coerce=int)
    search = TextAreaField('search')

class Add_Part(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    brand = SelectField('brand', validators=[DataRequired()], coerce=int)
    tags = TextAreaField('tags')
