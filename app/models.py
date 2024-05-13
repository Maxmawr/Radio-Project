from app.routes import db


class Brand(db.Model):
    __tablename__ = "Brand"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text())
    alias = db.Column(db.Text())
    motto = db.Column(db.Text())
    manufacturer_id = db.Column(db.Integer, db.ForeignKey('Manufacturer.id'))

    manufacturer = db.relationship("Manufacturer", back_populates="brands")
    parts = db.relationship("Parts", back_populates="brands")


    def __repr__(self):
        return self.name


class Manufacturer(db.Model):
    __tablename__ = "Manufacturer"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text())
    
    brands = db.relationship("Brand", back_populates="manufacturer")

class Parts(db.Model):
    __tablename__ = "Parts"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text())
    brand_id = db.Column(db.Integer, db.ForeignKey('brand.id'))
    type_id = db.Column(db.Integer, db.ForeignKey('type.id'))
    size = db.Column(db.Text())
    image = db.Column(db.Text())

    brands = db.relationship("Brand", back_populates="parts")
    type = db.relationship("Type", back_populates="parts")

    def __repr__(self):
        return self.name

class Type(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text())
    description = db.Column(db.Text())

    parts = db.relationship("Parts", back_populates="type")

    def __repr__(self):
        return self.name
