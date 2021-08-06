from flask import json, request, jsonify, Blueprint
from api.models import Reservation, History, db, User, Pet, Clinic, Doctor, Specie, Pet_state, Reservation_Status
from werkzeug.security import check_password_hash, generate_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from datetime import timedelta, datetime

user = Blueprint('api_user', __name__)

sessiontime = timedelta(hours=1)

@user.route('/register', methods=['POST'])
def register_user():
    if User.query.filter_by(email=request.json.get('email')).first() is not None:
        return jsonify(Error='Email already registered'), 409
    user = User()
    user.email = request.json.get('email')
    user.name = request.json.get('name')
    user.lastname = request.json.get('lastname')
    user.phone = request.json.get('phone')
    user.password = generate_password_hash(request.json.get('password'))

    db.session.add(user)
    db.session.commit()

    return jsonify(Success='User created'), 201

@user.route('/login', methods=['POST'])
def login_user():
    email = request.json.get("email", None)
    password = request.json.get("password", None)
    user = User.query.filter_by(email=email).first()        
    if user is not None and check_password_hash(user.password, password):
        access_token = create_access_token(identity=email, expires_delta=sessiontime)
        return jsonify(access_token=access_token), 201
    else:
        return jsonify({"Error": "Bad username or password"}), 401


@user.route('/info', methods=['GET'])
@jwt_required()
def info_user():
    current_user = get_jwt_identity()
    user = User.query.filter_by(email=current_user).first()

    return jsonify(user.serialize()), 200

@user.route('/info', methods=['PUT'])
@jwt_required()
def update_user():
    current_user = get_jwt_identity()
    user = User.query.filter_by(email=current_user).first()
    if user is None:
        return jsonify(Error="User not found"), 404
    if request.json.get('name') is not None:
        user.name = request.json.get('name')
    if request.json.get('lastname') is not None:
        user.lastname = request.json.get('lastname')
    if request.json.get('phone') is not None:
        user.phone = request.json.get('phone')
    if request.json.get('email') is not None:
        user.email = request.json.get('email')
    if request.json.get('picture') is not None:
        user.picture = request.json.get('picture')
    db.session.commit()
    if request.json.get('password') is not None:
        user.password = generate_password_hash(request.json.get('password'))
    
    return jsonify(Success="User updated"), 202


@user.route('/pets', methods=['GET'])
@jwt_required()
def pets_user():
    current_user = get_jwt_identity()
    user = User.query.filter_by(email=current_user).first()
    if user is None:
        return jsonify(Error="User not found"), 404
    return jsonify(user.serialize_pets()), 200

@user.route('/pets/<int:pet_id>', methods=['GET'])
@jwt_required()
def pet_user(pet_id):
    current_user = get_jwt_identity()
    user = User.query.filter_by(email=current_user).first()
    if user is None:
        return jsonify(Error="User not found"), 404
    pet = Pet.query.filter_by(id_owner=user.id, id=pet_id).first()
    if pet is None:
        return jsonify(Error="Pet not found"), 404
    return jsonify(pet.serialize()), 200

@user.route('/pets/<int:pet_id>', methods=['DELETE'])
@jwt_required()
def delete_pet_user(pet_id):
    current_user = get_jwt_identity()
    user = User.query.filter_by(email=current_user).first()
    if user is None:
        return jsonify(Error="User not found"), 404
    pet = Pet.query.filter_by(id_owner=user.id, id=pet_id).first()
    if pet is None:
        return jsonify(Error="Pet not found"), 404
    if pet.id_foundation is not None:
        return jsonify(Error="Cannot delete a pet that is part of a Foundation"), 409
    db.session.delete(pet)
    db.session.commit()
    return jsonify(Success="Pet deleted"), 203

@user.route('/pets/<int:pet_id>', methods=['PUT'])
@jwt_required()
def update_pet_user(pet_id):
    current_user = get_jwt_identity()
    user = User.query.filter_by(email=current_user).first()
    if user is None:
        return jsonify(Error="User not found"), 404
    pet = Pet.query.filter_by(id_owner=user.id, id=pet_id).first()
    if pet is None:
        return jsonify(Error="Pet not found"), 404
    if request.json.get('name') is not None:
        pet.name = request.json.get('name')
    if request.json.get('code_chip') is not None:
        pet.code_chip = request.json.get('code_chip')
    if request.json.get('breed') is not None:
        pet.breed = request.json.get('breed')
    if request.json.get('picture') is not None:
        pet.picture = request.json.get('picture')
    db.session.commit()
    return jsonify(Success="Success changes"), 202

@user.route('/pets/add', methods=['POST'])
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

@user.route('/pets/<int:pet_id>/history', methods=['GET'])
@jwt_required()
def get_history_pet_user(pet_id):
    current_user = get_jwt_identity()
    user = User.query.filter_by(email=current_user).first()
    pet = Pet.query.filter_by(id_owner=user.id, id=pet_id).first()

    if pet is None:
        return jsonify(Error="Pet not found"), 404
    
    return jsonify(History=pet.serialize_history()), 200

@user.route('/pets/<int:pet_id>/report/lost', methods=['POST'])
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

@user.route('/pets/<int:pet_id>/report/founded', methods=['GET'])
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


#User to clinic

@user.route('/clinics/list', methods=['GET'])
def get_clinics():
    clinics = Clinic.query.all()
    return jsonify([i.serialize() for i in clinics]), 200

@user.route('/clinics/<int:clinic_id>/doctors', methods=['GET'])
def get_doctors_clinic(clinic_id):
    clinic = Clinic.query.filter_by(id=clinic_id).first()
    if clinic is None:
        return jsonify(Error="Clinic not found"), 404
    doctors = Doctor.query.filter_by(id_clinic=clinic.id).all()
    return jsonify([i.serialize() for i in doctors]), 200

@user.route('/clinics/<int:clinic_id>/doctor/<int:doctor_id>/reservations', methods=['GET'])
def get_reservations_clinic(clinic_id, doctor_id):
    clinic = Clinic.query.filter_by(id=clinic_id).first()
    if clinic is None:
        return jsonify(Error="Clinic not found"), 404
    doctor = Doctor.query.filter_by(id=doctor_id).first()
    if doctor is None:
        return jsonify(Error="Doctor not found"), 404
    reservations = Reservation.query.filter_by(id_doctor=doctor.id, status=Reservation_Status.available).all()
    return jsonify([i.serialize() for i in reservations]), 200

@user.route('/clinics/<int:clinic_id>/doctor/<int:doctor_id>/reservation/add', methods=['POST'])
@jwt_required()
def add_reservation_clinic(clinic_id, doctor_id):
    current_user = get_jwt_identity()
    user = User.query.filter_by(email=current_user).first()
    clinic = Clinic.query.filter_by(id=clinic_id).first()
    if clinic is None:
        return jsonify(Error="Clinic not found"), 404
    doctor = Doctor.query.filter_by(id=doctor_id).first()
    if doctor is None:
        return jsonify(Error="Doctor not found"), 404
    id_reservation = request.json.get("id_reservation")
    reservation = Reservation.query.filter_by(id_doctor=doctor.id, id_clinic=clinic.id, id=id_reservation).first()
    if reservation is None:
        return jsonify(Error="Reservation not found"), 404
    reservation.id_user = user.id
    reservation.status = Reservation_Status.reserved
    reservation.id_pet = request.json.get("id_pet")
    
    db.session.commit()
    return jsonify(Success="Reservation added in clinic id: {}".format(clinic.id)), 201

@user.route('/reservations', methods=['GET'])
@jwt_required()
def get_reservations_user():
    current_user = get_jwt_identity()
    user = User.query.filter_by(email=current_user).first()
    reservations = Reservation.query.filter_by(id_user=user.id, status=Reservation_Status.reserved).all()
    return jsonify([reservation.serialize() for reservation in reservations ]), 200

@user.route('/reservations/<int:id_reservation>/cancel', methods=['DELETE'])
@jwt_required()
def cancel_reservation(id_reservation):
    current_user = get_jwt_identity()
    user = User.query.filter_by(email=current_user).first()
    reservation = Reservation.query.filter_by(id=id_reservation).first()
    if reservation is None:
        return jsonify(Error="Reservation not found"), 404
    if reservation.id_user != user.id:
        return jsonify(Error="Not authorized"), 401
    reservation.status = Reservation_Status.canceled
    db.session.commit()
    return jsonify(Success="Reservation canceled"), 200