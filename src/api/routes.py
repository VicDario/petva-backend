from flask import json, request, jsonify, url_for, Blueprint
from sqlalchemy.orm import query
from api.models import Diagnostic, History, Surgery, Vaccine, db, User, Pet, Clinic, Doctor, Foundation, Specie, Pet_state
from api.utils import generate_sitemap, APIException
from werkzeug.security import check_password_hash, generate_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from datetime import timedelta, datetime
import uuid

api = Blueprint('api', __name__)

sessiontime = timedelta(hours=1)

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
        access_token = create_access_token(identity=email, expires_delta=sessiontime)
        return jsonify(access_token=access_token), 201
    else:
        return jsonify({"Error": "Bad username or password"}), 401


@api.route('/user/info', methods=['GET'])
@jwt_required()
def info_user():
    current_user = get_jwt_identity()
    user = User.query.filter_by(email=current_user).first()

    return jsonify(user.serialize()), 200

@api.route('/user/pets', methods=['GET'])
@jwt_required()
def pets_user():
    current_user = get_jwt_identity()
    user = User.query.filter_by(email=current_user).first()
    if user is None:
        return jsonify(Error="User not found"), 404
    return jsonify(user.serialize_pets()), 200

@api.route('/user/pets/<int:pet_id>', methods=['GET'])
@jwt_required()
def pet_user(pet_id):
    current_user = get_jwt_identity()
    user = User.query.filter_by(email=current_user).first()
    if user is None:
        return jsonify(Error="User not found"), 404
    pet = Pet.query.filter_by(id_owner=user.id, id=pet_id).first()
    if pet is None:
        return jsonify(Error="Pet not found"), 404
    return jsonify(pet.serialize())

@api.route('/user/pets/add', methods=['POST'])
@jwt_required()
def add_pet_to_user():
    current_user = get_jwt_identity()
    user = User.query.filter_by(email=current_user).first()
    pet = Pet()
    pet.name = request.json.get("name")
    pet.id_owner = user.id
    pet.id_foundation = None
    pet.code_chip = request.json.get("code_chip", None)
    pet.breed = request.json.get("breed", None)
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

    pet.history = History()

    db.session.add(pet)
    db.session.commit()
    
    return jsonify(Success='Pet added'), 201

@api.route('/user/pets/<int:pet_id>/history', methods=['GET'])
@jwt_required()
def get_history_pet_user(pet_id):
    current_user = get_jwt_identity()
    user = User.query.filter_by(email=current_user).first()
    pet = Pet.query.filter_by(id_owner=user.id, id=pet_id).first()

    if pet is None:
        return jsonify(Error="Pet not found"), 404
    
    return jsonify(History=pet.serialize_history()), 200

@api.route('/user/pets/<int:pet_id>/history/vaccine/add', methods=['POST'])
@jwt_required()
def add_vaccine_user_to_pet(pet_id):
    current_user = get_jwt_identity()
    user = User.query.filter_by(email=current_user).first()
    pet = Pet.query.filter_by(id_owner=user.id, id=pet_id).first()

    if pet is None:
        return jsonify(Error="Pet not found"), 404

    history = History.query.filter_by(id_pet=pet.id).first()
    
    vaccine = Vaccine()
    date = request.json.get("date")
    vaccine.date = datetime.strptime(date, "%d/%m/%Y")
    vaccine.lot = request.json.get("lot")
    vaccine.name = request.json.get("name")
    vaccine.laboratory = request.json.get("laboratory")
    vaccine.id_history = history.id

    db.session.add(vaccine)
    db.session.commit()

    return jsonify(Success="Vaccine added in history pet id: {}".format(pet.id)), 201

@api.route('/user/pets/<int:pet_id>/history/diagnostic/add', methods=['POST'])
@jwt_required()
def add_diagnostic_user_to_pet(pet_id):
    current_user = get_jwt_identity()
    user = User.query.filter_by(email=current_user).first()
    pet = Pet.query.filter_by(id_owner=user.id, id=pet_id).first()

    if pet is None:
        return jsonify(Error="Pet not found"), 404

    history = History.query.filter_by(id_pet=pet.id).first()
    
    diagnostic = Diagnostic()
    date = request.json.get("date")
    diagnostic.date = datetime.strptime(date, "%d/%m/%Y")
    diagnostic.diagnostic = request.json.get("diagnostic")
    diagnostic.doctor_name = request.json.get("doctor_name")
    diagnostic.id_history = history.id

    db.session.add(diagnostic)
    db.session.commit()

    return jsonify(Success="Diagnostic added in history pet id: {}".format(pet.id)), 201

@api.route('/user/pets/<int:pet_id>/history/surgery/add', methods=['POST'])
@jwt_required()
def add_surgery_user_to_pet(pet_id):
    current_user = get_jwt_identity()
    user = User.query.filter_by(email=current_user).first()
    pet = Pet.query.filter_by(id_owner=user.id, id=pet_id).first()

    if pet is None:
        return jsonify(Error="Pet not found"), 404

    history = History.query.filter_by(id_pet=pet.id).first()
    
    surgery = Surgery()
    date = request.json.get("date")
    surgery.date = datetime.strptime(date, "%d/%m/%Y")
    surgery.description = request.json.get("description")
    surgery.doctor_name = request.json.get("doctor_name")
    surgery.id_history = history.id

    db.session.add(surgery)
    db.session.commit()

    return jsonify(Success="Surgery added in history pet id: {}".format(pet.id)), 201

@api.route('/user/pets/<int:pet_id>/report/lost', methods=['POST'])
@jwt_required()
def get_report_pet_user(pet_id):
    current_user = get_jwt_identity()
    user = User.query.filter_by(email=current_user).first()
    pet = Pet.query.filter_by(id_owner=user.id, id=pet_id).first()
    if pet is None:
        return jsonify(Error="Pet not found"), 404
    pet.last_location = request.json.get("last_location")
    pet.state = Pet_state.lost
    db.session.commit()
    return jsonify(Success="Pet {} {} reported".format(pet.id, pet.name)), 200

@api.route('/user/pets/<int:pet_id>/report/founded', methods=['GET'])
@jwt_required()
def get_report_pet_user_lost(pet_id):
    current_user = get_jwt_identity()
    user = User.query.filter_by(email=current_user).first()
    pet = Pet.query.filter_by(id_owner=user.id, id=pet_id).first()
    if pet is None:
        return jsonify(Error="Pet not found"), 404
    pet.last_location = None
    pet.state = Pet_state.owned
    db.session.commit()
    return jsonify(Success="Pet {} {} reported".format(pet.id, pet.name)), 200

#Clinic Routes

@api.route('/clinic/register', methods=['POST'])
def register_clinic():
    if Clinic.query.filter_by(email=request.json.get("email")).first() is not None:
        return jsonify(Error="Clinic already registered"), 409
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
        access_token = create_access_token(identity=email, expires_delta=sessiontime)
        return jsonify(access_token=access_token), 201
    else:
        return jsonify({"Error": "Bad username or password"}), 401

@api.route('/clinic/info', methods=['GET'])
@jwt_required()
def info_clinic():
    current_user = get_jwt_identity()
    clinic = Clinic.query.filter_by(email=current_user).first()

    return jsonify(clinic.serialize()), 200

#Doctor Routes

@api.route('/doctor/register', methods=['POST']) #Incomplete
def register_doctor():
    if Doctor.query.filter_by(email=request.json.get('email')).first() is not None:
        return jsonify(Error="Doctor already exists"), 400
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
        access_token = create_access_token(identity=email, expires_delta=sessiontime)
        return jsonify(access_token=access_token), 201
    else:
        return jsonify({"Error": "Bad username or password"}), 401

#Foundation Routes

@api.route('/foundation/register', methods=['POST'])
def register_foundation():
    if Foundation.query.filter_by(email=request.json.get('email')).first() is not None:
        return jsonify(Error="Email already registered"), 409
    foundation = Foundation()
    foundation.email = request.json.get('email')
    foundation.name = request.json.get('name')
    foundation.address = request.json.get('address')
    foundation.phone = request.json.get('phone')
    foundation.password = generate_password_hash(request.json.get('password'))

    db.session.add(foundation)
    db.session.commit()

    return jsonify(Success='Foundation created'), 201

@api.route('/foundation/login', methods=['POST'])
def login_foundation():
    email = request.json.get("email", None)
    password = request.json.get("password", None)
    foundation = Foundation.query.filter_by(email=email).first()        
    if foundation is not None and check_password_hash(foundation.password, password):
        access_token = create_access_token(identity=email, expires_delta=sessiontime)
        return jsonify(access_token=access_token), 201
    else:
        return jsonify({"Error": "Bad username or password"}), 401

@api.route('/foundation/info', methods=['GET'])
@jwt_required()
def info_foundation():
    current_user = get_jwt_identity()
    foundation = Foundation.query.filter_by(email=current_user).first()

    return jsonify(foundation.serialize())

@api.route('/foundation/pets/add', methods=['POST'])
@jwt_required()
def add_pet_to_foundation():
    current_user = get_jwt_identity()
    foundation = Foundation.query.filter_by(email=current_user).first()
    if foundation is None:
        return jsonify(Error="Foundation not found"), 404
    pet = Pet()
    pet.name = request.json.get("name")
    pet.id_owner = None
    pet.code_chip = request.json.get("code_chip", None)
    pet.breed = request.json.get("breed", None)
    pet.id_foundation = foundation.id
    pet.state = Pet_state.adoption
    pet.picture = request.json.get("picture", None)
    birth = request.json.get("birth_date", None) # DD/MM/YYYY
    if birth is not None:
        birth = datetime.strptime(birth, "%d/%m/%Y") 
    pet.birth_date = birth
    if request.json.get("specie") == 'cat':
        pet.specie = Specie.cat
    if request.json.get("specie") == 'dog':
        pet.specie = Specie.dog

    pet.history = History()

    db.session.add(pet)
    db.session.commit()
    
    return jsonify(Success='Pet added'), 201

@api.route('/foundation/pets/in_adoption', methods=['GET'])
@jwt_required()
def foundation_pets_in_adoption():
    current_user = get_jwt_identity()
    foundation = Foundation.query.filter_by(email=current_user).first()
    pets = Pet.query.filter_by(id_foundation=foundation.id, state=Pet_state.adoption).all()

    return jsonify(list(map(lambda pet: pet.serialize(), pets))), 200


@api.route('/foundation/pets/owned', methods=['GET'])
@jwt_required()
def foundation_pets_owned():
    current_user = get_jwt_identity()
    foundation = Foundation.query.filter_by(email=current_user).first()
    pets = Pet.query.filter_by(id_foundation=foundation.id, state=Pet_state.owned).all()

    return jsonify(list(map(lambda pet: pet.serialize(), pets)))

@api.route('/foundation/pets/<int:pet_id>', methods=['GET'])
@jwt_required()
def foundation_pet(pet_id):
    current_user = get_jwt_identity()
    foundation = Foundation.query.filter_by(email=current_user).first()
    if foundation is None:
        return jsonify(Error="Foundation not found"), 404   
    pet = Pet.query.filter_by(id_foundation=foundation.id, id=pet_id).first()
    if pet is None:
        return jsonify(Error="Pet not found"), 404

    return jsonify(pet.serialize()), 200

@api.route('/foundation/transfer', methods=['POST'])
@jwt_required()
def foundation_transfer_pet_to_user():
    current_user = get_jwt_identity()
    foundation = Foundation.query.filter_by(email=current_user).first()
    if foundation is None:
        return jsonify(Error="Foundation not found"), 404
    user = User.query.filter_by(email=request.json.get("email_user")).first()
    if user is None:
        return jsonify(Error="User not found"), 404
    id_pet = int(request.json.get("id_pet"))
    pet = Pet.query.filter_by(id=id_pet, id_foundation=foundation.id).first()
    if pet is None:
        return jsonify(Error="Pet not found"), 404
    pet.id_owner = user.id
    pet.state = Pet_state.owned
    db.session.commit()
    return jsonify(Success="Pet {} {} transferred to user {} {}".format(pet.id, pet.name, user.id, user.email)), 201

@api.route('/foundation/pets/<int:pet_id>/history', methods=['GET'])
@jwt_required()
def get_history_pet_foundation(pet_id):
    current_user = get_jwt_identity()
    foundation = Foundation.query.filter_by(email=current_user).first()
    pet = Pet.query.filter_by(id_foundation=foundation.id, id=pet_id).first()

    if pet is None:
        return jsonify(Error="Pet not found"), 404
    
    return jsonify(History=pet.serialize_history()), 200


@api.route('/foundation/pets/<int:pet_id>/history/vaccine/add', methods=['POST'])
@jwt_required()
def add_vaccine_foundation_to_pet(pet_id):
    current_user = get_jwt_identity()
    foundation = Foundation.query.filter_by(email=current_user).first()

    pet = Pet.query.filter_by(id=pet_id, id_foundation=foundation.id).first()
    if pet is None:
        return jsonify(Error="Pet not found"), 404

    history = History.query.filter_by(id_pet=pet.id).first()
    
    vaccine = Vaccine()
    date = request.json.get("date")
    vaccine.date = datetime.strptime(date, "%d/%m/%Y")
    vaccine.lot = request.json.get("lot")
    vaccine.name = request.json.get("name")
    vaccine.laboratory = request.json.get("laboratory")
    vaccine.id_history = history.id

    db.session.add(vaccine)
    db.session.commit()

    return jsonify(Success="Vaccine added in history pet id: {}".format(pet.id)), 201

@api.route('/foundation/pets/<int:pet_id>/history/diagnostic/add', methods=['POST'])
@jwt_required()
def add_diagnostic_foundation_to_pet(pet_id):
    current_user = get_jwt_identity()
    foundation = Foundation.query.filter_by(email=current_user).first()
    pet = Pet.query.filter_by(id_foundation=foundation.id, id=pet_id).first()

    if pet is None:
        return jsonify(Error="Pet not found"), 404

    history = History.query.filter_by(id_pet=pet.id).first()
    
    diagnostic = Diagnostic()
    date = request.json.get("date")
    diagnostic.date = datetime.strptime(date, "%d/%m/%Y")
    diagnostic.diagnostic = request.json.get("diagnostic")
    diagnostic.doctor_name = request.json.get("doctor_name")
    diagnostic.id_history = history.id

    db.session.add(diagnostic)
    db.session.commit()

    return jsonify(Success="Diagnostic added in history pet id: {}".format(pet.id)), 201

@api.route('/foundation/pets/<int:pet_id>/history/surgery/add', methods=['POST'])
@jwt_required()
def add_surgery_foundation_to_pet(pet_id):
    current_user = get_jwt_identity()
    foundation = Foundation.query.filter_by(email=current_user).first()
    pet = Pet.query.filter_by(id_foundation=foundation.id, id=pet_id).first()

    if pet is None:
        return jsonify(Error="Pet not found"), 404

    history = History.query.filter_by(id_pet=pet.id).first()
    
    surgery = Surgery()
    date = request.json.get("date")
    surgery.date = datetime.strptime(date, "%d/%m/%Y")
    surgery.description = request.json.get("description")
    surgery.doctor_name = request.json.get("doctor_name")
    surgery.id_history = history.id

    db.session.add(surgery)
    db.session.commit()

    return jsonify(Success="Surgery added in history pet id: {}".format(pet.id)), 201

@api.route('pets/in_adoption/<int:page>', methods=['GET'])
def get_pets_in_adoption(page=1):
    pets = Pet.query.filter_by(state=Pet_state.adoption).paginate(page=page, per_page=10)
    return jsonify([pet.serialize_info_for_adoption() for pet in pets.items], pets.pages, pets.has_next, pets.has_prev), 200

@api.route('pets/lost/<int:page>', methods=['GET'])
def get_pets_lost(page=1):
    pets = Pet.query.filter_by(state=Pet_state.lost).paginate(page=page, per_page=10)
    return jsonify([pet.serialize_info_for_lost() for pet in pets.items], pets.pages, pets.has_next, pets.has_prev), 200