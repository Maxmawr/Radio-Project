from app.routes import db

PartBrands = db.Table('PartBrands',
    db.Column('part_id', db.Integer, db.ForeignKey('Part.id')),
    db.Column('brand_id', db.Integer, db.ForeignKey('Brand.id')))

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

    manufacturer = db.relationship("Manufacturer", back_populates="brands")
    parts = db.relationship("Part", secondary="PartBrands", back_populates="brands")

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
    description = db.Column(db.Text())

    def __repr__(self):
        return self.name


class Part(db.Model):
    __tablename__ = "Part"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text())
    type_id = db.Column(db.Integer, db.ForeignKey('Type.id'))
    size = db.Column(db.Text())
    image = db.Column(db.Text())

    brands = db.relationship("Brand", secondary="PartBrands", back_populates="parts")
    tag = db.relationship("Tag", secondary="PartTag", backref="parts")
    type = db.relationship("Type", backref="tparts")

    def __repr__(self):
        return self.name


class Tag(db.Model):
    __tablename__ = "Tag"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text())

    def __repr__(self):
        return self.name
