from flask_migrate import history
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    lastname= db.column(db.String(50), nullable=False)
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
    code_chip = db.column(db.String(50))
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
