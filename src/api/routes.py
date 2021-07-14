from flask import request, jsonify, url_for, Blueprint
from api.models import History, db, User, Pet, Clinic, Doctor, Fundation, Specie, Pet_state
from api.utils import generate_sitemap, APIException
from werkzeug.security import check_password_hash, generate_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from datetime import timedelta, datetime

api = Blueprint('api', __name__)

sessiontime = 1

@api.route('/', methods=['GET'])
def main():
    return jsonify(Test="Test"), 200


#User Routes

@api.route('/user/register', methods=['POST'])
def register_user():
    if User.query.filter_by(email=request.json.get('email')).first() is not None:
        return jsonify(Error='Email already registered'), 409
    user = User()
    user.email = request.json.get('email')
    user.name = request.json.get('name')
    user.lastname = request.json.get('lastname')
    user.password = generate_password_hash(request.json.get('password'))

    db.session.add(user)
    db.session.commit()

    return jsonify(Success='User created'), 201

@api.route('/user/login', methods=['POST'])
def login_user():
    email = request.json.get("email", None)
    password = request.json.get("password", None)
    user = User.query.filter_by(email=email).first()        
    if user is not None and check_password_hash(user.password, password):
        access_token = create_access_token(identity=email, expires_delta=timedelta(hours=sessiontime))
        return jsonify(access_token=access_token), 201
    else:
        return jsonify({"Error": "Bad username or password"}), 401


@api.route('/user/info', methods=['GET'])
@jwt_required()
def info_user():
    current_user = get_jwt_identity()
    user = User.query.filter_by(email=current_user).one_or_none()

    return jsonify(user.serialize())

@api.route('/user/pets', methods=['GET'])
@jwt_required()
def pets_user():
    current_user = get_jwt_identity()
    user = User.query.filter_by(email=current_user).one_or_none()
    return jsonify(user.serialize_pets())

@api.route('/user/pets/add', methods=['POST'])
@jwt_required()
def add_pet():
    current_user = get_jwt_identity()
    user = User.query.filter_by(email=current_user).one_or_none()
    fundation = Fundation.query.filter_by(name="Null").one_or_none()
    pet = Pet()
    pet.name = request.json.get("name")
    pet.id_owner = user.id
    pet.code_chip = request.json.get("code_chip", None)
    pet.breed = request.json.get("breed", None)
    pet.id_fundation = fundation.id
    pet.state = Pet_state.owned
    pet.picture = request.json.get("picture", None)
    birth = request.json.get("birth_date", None) # DD/MM/YYYY
    if birth is not None:
        birth = datetime.strptime(birth, "%d/%m/%Y") 
    pet.birth_date = birth
    if request.json.get("specie") == 'cat':
        pet.specie = Specie.cat
    if request.json.get("specie") == 'dog':
        pet.specie = Specie.dog

    history = History()
    pet.history = history

    db.session.add(pet)
    db.session.commit()
    
    return jsonify(Success='Pet added'), 201

#Clinic Routes

@api.route('/user/pet/<int:pet_id>/history', methods=['GET'])
@jwt_required()
def get_history_pet(pet_id):
    current_user = get_jwt_identity()
    user = User.query.filter_by(email=current_user).one_or_none()

    pet = Pet.query.filter_by(id_owner=user.id, id=pet_id).first()

    if pet is None:
        return jsonify(Error="Pet not found"), 404
    
    return jsonify(History=pet.serialize_history()), 200

@api.route('/clinic/register', methods=['POST'])
def register_clinic():
    clinic = Clinic()
    clinic.email = request.json.get('email')
    clinic.name = request.json.get('name')
    clinic.address = request.json.get('address')
    clinic.phone = request.json.get('phone')
    clinic.password = generate_password_hash(request.json.get('password'))

    db.session.add(clinic)
    db.session.commit()

    return jsonify(Success='Clinic created'), 201

@api.route('/clinic/login', methods=['POST'])
def login_clinic():
    email = request.json.get("email", None)
    password = request.json.get("password", None)
    clinic = Clinic.query.filter_by(email=email).first()        
    if clinic is not None and check_password_hash(clinic.password, password):
        access_token = create_access_token(identity=email, expires_delta=timedelta(hours=sessiontime))
        return jsonify(access_token=access_token), 201
    else:
        return jsonify({"Error": "Bad username or password"}), 401


#Doctor Routes

@api.route('/doctor/register', methods=['POST']) #Incomplete
def register_doctor():
    doctor = Doctor()
    doctor.email = request.json.get('email')
    doctor.name = request.json.get('name')
    doctor.lastname = request.json.get('lastname')
    doctor.specialty = request.json.get('specialty')
    doctor.password = generate_password_hash(request.json.get('password'))

    db.session.add(doctor)
    db.session.commit()

    return jsonify(Success='Doctor created'), 201

@api.route('/doctor/login', methods=['POST'])
def login_doctor():
    email = request.json.get("email", None)
    password = request.json.get("password", None)
    doctor = Doctor.query.filter_by(email=email).first()        
    if doctor is not None and check_password_hash(doctor.password, password):
        access_token = create_access_token(identity=email, expires_delta=timedelta(hours=sessiontime))
        return jsonify(access_token=access_token), 201
    else:
        return jsonify({"Error": "Bad username or password"}), 401

#Fundation Routes

@api.route('/fundation/register', methods=['POST'])
def register_fundation():
    fundation = Fundation()
    fundation.email = request.json.get('email')
    fundation.name = request.json.get('name')
    fundation.address = request.json.get('address')
    fundation.phone = request.json.get('phone')
    fundation.password = generate_password_hash(request.json.get('password'))

    db.session.add(fundation)
    db.session.commit()

    return jsonify(Success='Fundation created'), 201

@api.route('/fundation/login', methods=['POST'])
def login_fundation():
    email = request.json.get("email", None)
    password = request.json.get("password", None)
    fundation = Fundation.query.filter_by(email=email).first()        
    if fundation is not None and check_password_hash(fundation.password, password):
        access_token = create_access_token(identity=email, expires_delta=timedelta(hours=sessiontime))
        return jsonify(access_token=access_token), 201
    else:
        return jsonify({"Error": "Bad username or password"}), 401