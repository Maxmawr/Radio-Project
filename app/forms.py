from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Optional, ValidationError
import app.models
from datetime import datetime

class Filter_Brands(FlaskForm):
  partbrand = SelectField('partbrand', validators=[DataRequired()], coerce=int)