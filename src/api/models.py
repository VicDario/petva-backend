from flask_sqlalchemy import SQLAlchemy
from enum import Enum

db = SQLAlchemy()

Specie = Enum('Specie', 'cat dog')
Pet_state = Enum('Pet_State', 'adoption owned lost')
Reservation_Status = Enum('Reservation_Status', 'available reserved')

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(50), nullable=False)
    lastname= db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(12))
    picture = db.Column(db.Text)
    pets = db.relationship('Pet', cascade='all, delete', backref='user')

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'lastname': self.lastname,
            'email': self.email,
            'phone': self.phone,
            'picture': self.picture
        }

    def serialize_pets(self):
        return list(map(lambda pet: pet.serialize(), self.pets))


class Pet(db.Model):
    __tablename__ = 'pets'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    code_chip = db.Column(db.String(50))
    specie = db.Column(db.Enum(Specie), nullable=False)
    picture = db.Column(db.Text)
    birth_date = db.Column(db.Date)
    breed = db.Column(db.String(30))
    state = db.Column(db.Enum(Pet_state), nullable=False)
    last_location = db.Column(db.Text)
    id_owner = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=True)
    id_foundation  = db.Column(db.Integer, db.ForeignKey('foundations.id', ondelete='CASCADE'), nullable=True)
    history = db.relationship('History', cascade='all, delete', backref='pet', uselist=False)

    def serialize(self):
        if self.specie == Specie.cat:
            specie = 'cat'
        if self.specie == Specie.dog:
            specie = 'dog'

        if self.state == Pet_state.adoption:
            state = 'adoption'
        if self.state == Pet_state.owned:
            state = 'owned'
        if self.state == Pet_state.lost:
            state = 'lost'
        return {
            'id': self.id,
            'id_owner': self.id_owner,
            'id_foundation': self.id_foundation,
            'name': self.name,
            'code_chip': self.code_chip,
            'birth_date': self.birth_date,
            'breed': self.breed,
            'specie': specie,
            'state': state,
            'picture': self.picture
        }
    def serialize_info_for_adoption(self):
        if self.specie == Specie.cat:
            specie = 'cat'
        if self.specie == Specie.dog:
            specie = 'dog'
        return {
            'name': self.name,
            'specie': specie,
            'birth_date': self.birth_date,
            'picture': self.picture,
            'name_foundation': self.foundation.name,
            'email_foundation': self.foundation.email,
            'phone_foundation': self.foundation.phone,
            'address_foundation': self.foundation.address,
            'picture_foundation': self.foundation.picture
        }
    
    def serialize_info_for_lost(self):
        if self.specie == Specie.cat:
            specie = 'cat'
        if self.specie == Specie.dog:
            specie = 'dog'
        return {
            'name': self.name,
            'code_chip': self.code_chip,
            'birth_date': self.birth_date,
            'last_location': self.last_location,
            'breed': self.breed,
            'specie': specie,
            'picture': self.picture,
            'email_owner': self.user.email,
            'phone_owner': self.user.phone,
            'name_owner': self.user.name + ' ' + self.user.lastname,
        }

    def serialize_history(self):
        return {
            'id': self.history.id,
            'id_pet': self.history.id_pet,
            'vaccines': self.history.serialize_vaccines(),
            'diagnostics': self.history.serialize_diagnostics(),
            'surgeries': self.history.serialize_surgeries()
        }

class History(db.Model):
    __tablename__ = 'histories'
    id = db.Column(db.Integer, primary_key=True)
    id_pet = db.Column(db.Integer, db.ForeignKey('pets.id', ondelete='CASCADE'))
    vaccines = db.relationship('Vaccine', cascade='all, delete', backref='history')
    diagnostics = db.relationship('Diagnostic', cascade='all, delete', backref='history')
    surgeries = db.relationship('Surgery', cascade='all, delete', backref='history')

    def serialize_vaccines(self):
        return list(map(lambda vaccine: vaccine.serialize(), self.vaccines))
    def serialize_diagnostics(self):
        return list(map(lambda diagnostic: diagnostic.serialize(), self.diagnostics))
    def serialize_surgeries(self):
        return list(map(lambda surgery: surgery.serialize(), self.surgeries))

class Vaccine(db.Model):
    __tablename__ = 'vaccines'
    id = db.Column(db.Integer, primary_key=True)
    id_history = db.Column(db.Integer, db.ForeignKey('histories.id', ondelete='CASCADE'))
    lot = db.Column(db.Text, nullable=False)
    date = db.Column(db.Date)
    laboratory = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(50), nullable=False)

    def serialize(self):
        return {
            'id': self.id,
            'id_history': self.id_history,
            'name': self.name,
            'lot': self.lot,
            'laboratory': self.laboratory,
            'date': self.date
        }

class Diagnostic(db.Model):
    __tablename__ = 'diagnostics'
    id = db.Column(db.Integer, primary_key=True)
    id_history = db.Column(db.Integer, db.ForeignKey('histories.id', ondelete='CASCADE'))
    diagnostic = db.Column(db.Text, nullable=False)
    date = db.Column(db.Date, nullable=False)
    doctor_name = db.Column(db.String(100))

    def serialize(self):
        return {
            'id': self.id,
            'id_history': self.id_history,
            'diagnostic': self.diagnostic,
            'doctor_name': self.doctor_name,
            'date': self.date
        }

class Surgery(db.Model):
    __tablename__ = 'surgeries'
    id = db.Column(db.Integer, primary_key=True)
    id_history = db.Column(db.Integer, db.ForeignKey('histories.id', ondelete='CASCADE'))
    description = db.Column(db.Text, nullable=False)
    doctor_name = db.Column(db.String(100))
    date = db.Column(db.Date)

    def serialize(self):
        return {
            'id': self.id,
            'id_history': self.id_history,
            'description': self.description,
            'doctor_name': self.doctor_name,
            'date': self.date
        }

class Clinic(db.Model):
    __tablename__ = 'clinics'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.Text, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    doctors = db.relationship('Doctor', cascade='all, delete', backref='clinic')
    picture = db.Column(db.Text)
    
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'address': self.address,
            'email': self.email,
            'phone': self.phone,
            'picture': self.picture
        }
    
    def serialize_doctors(self):
        return list(map(lambda doctor: doctor.serialize(), self.doctors))

class Doctor(db.Model):
    __tablename__ = 'doctors'
    id = db.Column(db.Integer, primary_key=True)
    id_clinic = db.Column(db.Integer, db.ForeignKey('clinics.id', ondelete='CASCADE'))
    name = db.Column(db.String(100), nullable=False)
    lastname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    specialty = db.Column(db.String(50), nullable=False)
    picture = db.Column(db.Text)

    def serialize(self):
        return {
            'id': self.id,
            'id_clinic': self.id_clinic,
            'name': self.name,
            'lastname': self.lastname,
            'specialty': self.specialty,
            'picture' : self.picture
        }

class Reservation(db.Model):
    __tablename__ = 'reservation'
    id = db.Column(db.Integer, primary_key=True)
    id_clinic = db.Column(db.Integer, db.ForeignKey('clinics.id', ondelete='CASCADE'))
    id_pet = db.Column(db.Integer, db.ForeignKey('pets.id', ondelete='CASCADE'), nullable=True)
    date_start = db.Column(db.DateTime, nullable=False)
    date_end = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.Enum(Reservation_Status), nullable=False)
    id_user = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=True)
    id_doctor = db.Column(db.Integer, db.ForeignKey('doctors.id', ondelete='CASCADE'))
    
    def serialize(self):
        return {
            'id': self.id,
            'id_clinic': self.id_clinic,
            'id_pet': self.id_pet,
            'date_start': self.date_start,
            'date_end': self.date_end,
            'id_user': self.id_user,
            'id_doctor': self.id_doctor
        }

class Foundation(db.Model):
    __tablename__ = 'foundations'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    address = db.Column(db.Text, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    picture = db.Column(db.Text)
    pets = db.relationship('Pet', backref='foundation')

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'picture': self.picture
        }

    def serialize_pets(self):
        return list(map(lambda pet: pet.serialize(), self.pets))