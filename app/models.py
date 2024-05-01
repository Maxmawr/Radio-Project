from app.routes import db

class Manufacturer(db.Model):
    __tablename__ = "Manufacturer"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text())
    brand = db.relationship("Brand", backref="manufacturer")

class Brand(db.Model):
    __tablename__ = "Brand"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text())
    notes = db.Column(db.Text())
    manufacturer_id = db.Column(id.Integer, db.ForeignKey('manufacturer.id'))
    
    def __repr__(self):
        return self.name


