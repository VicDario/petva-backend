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
    email = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(50), nullable=False)
    lastname= db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(12))
    picture = db.Column(db.Text)
    pets = db.relationship('Pet', cascade='all, delete', backref='User')

    def serialize(self):
        return {
            'name': self.name,
            'lastname': self.lastname,
            'email': self.email,
            'picture': self.picture
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
    picture = db.Column(db.Text)
    birth_date = db.Column(db.Date)
    history = db.Relationship('History', cascade='all, delete', backref='Pet')
    id_owner = db.Column(db.Integer, db.ForeignKey('user.id'), ondelete='CASCADE', nullable=True)
    id_fundation  = db.Column(db.Integer, db.ForeignKey('fundation.id'), ondelete='CASCADE', nullable=True)

    def serialize(self):
        return {
            'id': self.id,
            'id_owner': self.id_owner,
            'id_fundation': self.id_owner,
            'name': self.name,
            'code_chip': self.code_chip,
            'specie': self.specie,
            'date': self.birth_date,
            'picture': self.picture
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
    
    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

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
    
    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class Diagnostic(db.Model):
    __tablename__ = 'diagnostics'
    id = db.Column(db.Integer, primary_key=True)
    id_history = db.Column(db.Integer, db.ForeignKey('history.id'), ondelete='CASCADE')
    diagnostic = db.Column(db.Text, nullable=False)
    date = db.Column(db.Date, nullable=False)
    doctor_name = db.Column(db.String(100))

    def serialize(self):
        return {
            'id': self.id,
            'diagnostic': self.diagnostic,
            'doctor_name': self.doctor_name,
            'date': self.date
        }
    
    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

class Surgery(db.Model):
    __tablename__ = 'surgeries'
    id = db.Column(db.Integer, primary_key=True)
    id_history = db.Column(db.Integer, db.ForeignKey('history.id'), ondelete='CASCADE')
    description = db.Column(db.Text, nullable=False)
    doctor_name = db.Column(db.String(100))
    date = db.Column(db.Date)

    def serialize(self):
        return {
            'id': self.id,
            'description': self.description,
            'doctor_name': self.doctor_name,
            'date': self.date
        }

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
class Clinic(db.Model):
    __tablename__ = 'clinics'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.Text, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(100), nullable=False)
    doctors = db.Relationship('Doctor', cascade='all, delete', backref='Clinic')
    picture = db.Column(db.Text)
    
    def serialize(self):
        return {
            'id': self.id,
            'address': self.address,
            'email': self.email,
            'phone': self.phone,
            'picture': self.picture
        }
    
    def serialize_doctors(self):
        return list(map(lambda doctor: doctor.serialize(), self.doctors))
    
    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

class Doctor(db.Model):
    __tablename__ = 'doctors'
    id = db.Column(db.Integer, primary_key=True)
    id_clinic = db.Column(db.Integer, db.ForeignKey('clinic.id'), ondelete='CASCADE')
    name = db.Column(db.String(100), nullable=False)
    lastname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    specialty = db.Column(db.String(50), nullable=False)
    picture = db.Column(db.Text)

    def serialize(self):
        return {
            'id': self.id,
            'id_clinic': self.id_clinic,
            'name': self.name,
            'lastname': self.lastname,
            'specialty': self.specialty
        }
    
    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

class Fundation(db.Model):
    __tablename__ = 'fundations'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(100), nullable=False)
    picture = db.Column(db.Text)
    pets = db.relationship('Pet', backref='Fundation')

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'picture': self.picture
        }
    def serialize_pets(self):
        return list(map(lambda pet: pet.serialize, self.pets))
    
    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()