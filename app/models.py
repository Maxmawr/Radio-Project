from app.routes import db
from flask_login import UserMixin

PartBrands = db.Table('PartBrands',
                      db.Column('part_id', db.Integer,
                                db.ForeignKey('Part.id')),
                      db.Column('brand_id', db.Integer,
                                db.ForeignKey('Brand.id')))

PartTag = db.Table('PartTag',
                   db.Column('part_id', db.Integer, db.ForeignKey('Part.id')),
                   db.Column('tag_id', db.Integer, db.ForeignKey('Tag.id')))


class Brand(db.Model):
    __tablename__ = "Brand"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text())
    alias = db.Column(db.Text())
    motto = db.Column(db.Text())
    manufacturer_id = db.Column(db.Integer, db.ForeignKey('Manufacturer.id'))
    logo = db.Column(db.Integer())

    manufacturer = db.relationship("Manufacturer", back_populates="brands")
    parts = db.relationship("Part", secondary="PartBrands",
                            back_populates="brands")

    def __repr__(self):
        return self.name


class Manufacturer(db.Model):
    __tablename__ = "Manufacturer"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text())

    brands = db.relationship("Brand", back_populates="manufacturer")

    def __repr__(self):
        return self.name


class Type(db.Model):
    __tablename__ = "Type"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text())

    def __repr__(self):
        return self.name


class Part(db.Model):
    __tablename__ = "Part"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text())
    type_id = db.Column(db.Integer, db.ForeignKey('Type.id'))
    width = db.Column(db.Integer())
    height = db.Column(db.Integer())
    notes = db.Column(db.Text())
    vrp_link = db.Column(db.Text())
    box_number = db.Column(db.Integer())

    brands = db.relationship("Brand", secondary="PartBrands",
                             back_populates="parts")
    tags = db.relationship("Tag", secondary="PartTag", back_populates="parts")
    type = db.relationship("Type", backref="parts")

    images = db.relationship("Image", back_populates="part")

    def __repr__(self):
        return self.name


class Image(db.Model):
    __tablename__ = "Image"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text())
    part_id = db.Column(db.Integer, db.ForeignKey(Part.id))

    part = db.relationship("Part", back_populates="images")

    def __repr__(self):
        return self.name


class Tag(db.Model):
    __tablename__ = "Tag"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text())

    parts = db.relationship("Part", secondary="PartTag", back_populates="tags")

    def __repr__(self):
        return self.name


class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(250), unique=True,
                         nullable=False)
    hashed_password = db.Column(db.String())

    def __repr__(self):
        return self.name
