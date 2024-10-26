from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, FileField, IntegerField
from wtforms.validators import DataRequired, NumberRange, Length, Optional
from flask_wtf.file import FileAllowed, FileRequired


class Search(FlaskForm):
    partbrand = SelectField('Brand', coerce=int)
    search = TextAreaField('Name', validators=[Length(max=100)])
    tag = SelectField('Tag', coerce=int)
    width = IntegerField('Width', validators=[Optional(), NumberRange(
        min=1, max=1000, message="Number must be between 1 and 1000")])
    height = IntegerField('Height', validators=[Optional(), NumberRange(
        min=1, max=1000, message="Number must be between 1 and 1000")])
    type = SelectField('Type', coerce=int)


class Add_Part(FlaskForm):
    name = StringField('name', validators=[DataRequired(), Length(max=100)])
    brand = SelectField('brand', validators=[DataRequired()], coerce=int)
    tags = TextAreaField('tags', validators=[Length(max=100)])
    width = IntegerField(
        'width', validators=[NumberRange(
            min=0, max=400, message="Number must be less than or equal to 400")])
    height = IntegerField(
        'height', validators=[NumberRange(
            min=0, max=400, message="Number must be less than or equal to 400")])
    type = SelectField('type', validators=[DataRequired()], coerce=int)
    image = FileField('Image', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Images only!')
    ])


class Search_Brand(FlaskForm):
    brand = SelectField('brand', coerce=int)


class Search_Tag(FlaskForm):
    tag = SelectField('tag', coerce=int)


class Edit(FlaskForm):
    name = StringField('name', validators=[DataRequired(), Length(max=100)])
    brand = SelectField('brand', validators=[DataRequired()], coerce=int)
    tags = TextAreaField('tags', validators=[Length(max=100)])
    width = IntegerField(
        'width', validators=[NumberRange(
            min=0, max=400, message="Number must be less than or equal to 400")])
    height = IntegerField(
        'height', validators=[NumberRange(
            min=0, max=400, message="Number must be less than or equal to 400")])
    type = SelectField('type', validators=[DataRequired()], coerce=int)
    image = FileField('Image', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Images only!')
    ])