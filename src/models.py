from flask_migrate import history
from flask_sqlalchemy import SQLAlchemy
import enum
db = SQLAlchemy()

class Specie(enum.Enum): #We can add more species, I'm testing this it´s not definitive
    cat = 'Cat'
    dog = 'Dog'
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    lastname= db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    pets = db.relationship('Pet', cascade='all, delete', backref='User')

    def serialize(self):
        return {
            'name': self.name,
            'lastname': self.lastname,
            'email': self.email
        }

    def serialize_pets(self):
        return list(map(lambda pet: pet.serialize(), self.pets))

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class Pet(db.Model):
    __tablename__ = 'pets'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    code_chip = db.Column(db.String(50))
    specie = db.Column(db.Enum(Specie), nullable=False)
    history = db.Relationship('History', cascade='all, delete', backref='Pet')
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), ondelete='CASCADE')

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'code_chip': self.code_chip
        }
        
    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

class History(db.Model):
    __tablename__ = 'Histories'
    id = db.Column(db.Integer, primary_key=True)
    id_pet = db.Column(db.Integer, db.ForeignKey('pet.id'), ondelete='CASCADE')
    vaccines = db.relationship('Vaccine', cascade='all, delete', backref='History')
    diagnostics = db.relationship('Diagnostic', cascade='all, delete', backref='History')
    surgeries = db.relationship('Surgery', cascade='all, delete', backref='History')

    def serialize_vaccines(self):
        return list(map(lambda vaccine: vaccine.serialize(), self.vaccines))
    def serialize_diagnostics(self):
        return list(map(lambda diagnostic: diagnostic.serialize(), self.diagnostics))
    def serialize_vaccines(self):
        return list(map(lambda surgery: surgery.serialize(), self.surgeries))

class Vaccine(db.Model):
    __tablename__ = 'Vaccines'
    id = db.Column(db.Integer, primary_key=True)
    id_history = db.Column(db.Integer, db.ForeignKey('history.id'), ondelete='CASCADE')
    lot = db.Column(db.text, nullable=False)
    date = db.Column(db.Date)
    laboratory = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(50), nullable=False)

    def serialize(self):
        return {
            'name': self.name,
            'lot': self.lot,
            'laboratory': self.laboratory,
            'date': self.date
        }

class Diagnostic(db.Model):
    __tablename__ = 'diagnostics'
    id = db.Column(db.Integer, primary_key=True)
    id_history = db.Column(db.Integer, db.ForeignKey('history.id'), ondelete='CASCADE')
    diagnostic = db.Column(db.Text, nullable=False)
    date = db.Column(db.Date, nullable=False)
    doctor_name = db.Column(db.String(100))

    def serialize(self):
        return {
            'diagnostic': self.diagnostic,
            'doctor_name': self.doctor_name,
            'date': self.date
        }

class Surgery(db.Model):
    __tablename__ = 'surgeries'
    id = db.Column(db.Integer, primary_key=True)
    id_history = db.Column(db.Integer, db.ForeignKey('history.id'), ondelete='CASCADE')
    description = db.Column(db.Text, nullable=False)
    doctor_name = db.Column(db.String(100))
    date = db.Column(db.Date)

    def serialize(self):
        return {
            'description': self.description,
            'doctor_name': self.doctor_name,
            'date': self.date
        }