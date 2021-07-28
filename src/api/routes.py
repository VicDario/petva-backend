from flask import json, request, jsonify, url_for, Blueprint
from sqlalchemy.orm import query
from api.models import Reservation, Diagnostic, History, Surgery, Vaccine, db, User, Pet, Clinic, Doctor, Foundation, Specie, Pet_state, Reservation_Status
from api.utils import generate_sitemap, APIException
from werkzeug.security import check_password_hash, generate_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from datetime import timedelta, datetime, timezone
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
    user.phone = request.json.get('phone')
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

@api.route('/user/info', methods=['PUT'])
@jwt_required()
def update_user():
    current_user = get_jwt_identity()
    user = User.query.filter_by(email=current_user).first()
    if user is None:
        return jsonify(Error="User not found"), 404
    user.name = request.json.get('name')
    user.lastname = request.json.get('lastname')
    user.phone = request.json.get('phone')
    user.email = request.json.get('email')
    if request.json.get('picture') is not None:
        user.picture = request.json.get('picture')
    db.session.commit()
    if request.json.get('password') is not None:
        user.password = generate_password_hash(request.json.get('password'))
    
    return jsonify(Success="User updated"), 202


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
    return jsonify(pet.serialize()), 200

@api.route('/user/pets/<int:pet_id>', methods=['DELETE'])
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

@api.route('/user/pets/<int:pet_id>', methods=['PUT'])
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


#User to clinic

@api.route('/user/clinics/list', methods=['GET'])
def get_clinics():
    clinics = Clinic.query.all()
    return jsonify([i.serialize() for i in clinics]), 200

@api.route('/user/clinics/<int:clinic_id>/doctors', methods=['GET'])
def get_doctors_clinic(clinic_id):
    clinic = Clinic.query.filter_by(id=clinic_id).first()
    if clinic is None:
        return jsonify(Error="Clinic not found"), 404
    doctors = Doctor.query.filter_by(id_clinic=clinic.id).all()
    return jsonify([i.serialize() for i in doctors]), 200

@api.route('/user/clinics/<int:clinic_id>/doctor/<int:doctor_id>/reservations', methods=['GET'])
def get_reservations_clinic(clinic_id, doctor_id):
    clinic = Clinic.query.filter_by(id=clinic_id).first()
    if clinic is None:
        return jsonify(Error="Clinic not found"), 404
    doctor = Doctor.query.filter_by(id=doctor_id).first()
    if doctor is None:
        return jsonify(Error="Doctor not found"), 404
    reservations = Reservation.query.filter_by(id_doctor=doctor.id, status=Reservation_Status.available).all()
    return jsonify([i.serialize() for i in reservations]), 200

@api.route('/user/clinics/<int:clinic_id>/doctor/<int:doctor_id>/reservation/add', methods=['POST'])
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

@api.route('/user/reservations', methods=['GET'])
@jwt_required()
def get_reservations_user():
    current_user = get_jwt_identity()
    user = User.query.filter_by(email=current_user).first()
    reservations = Reservation.query.filter_by(id_user=user.id, status=Reservation_Status.reserved).all()
    return jsonify([reservation.serialize() for reservation in reservations ]), 200

@api.route('/user/reservations/<int:id_reservation>/cancel', methods=['DELETE'])
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

#Clinic Routes

@api.route('/clinic/register', methods=['POST']) #checked
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

@api.route('/clinic/login', methods=['POST']) #checked
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

@api.route('/clinic/check/reservations', methods=['GET'])
@jwt_required()
def check_reserved_clinic():
    current_user = get_jwt_identity()
    clinic = Clinic.query.filter_by(email=current_user).first()
    if clinic is None:
        return jsonify(Error="Clinic not found"), 404
    print(clinic.name)
    reservations = Reservation.query.filter_by(id_clinic=clinic.id).all()
    return jsonify([i.serialize() for i in reservations]), 200


#Doctor Routes

@api.route('/clinic/doctor/register', methods=['POST']) #checked
@jwt_required()
def register_doctor():
    current_user = get_jwt_identity()
    clinic = Clinic.query.filter_by(email=current_user).first()
    
    doctor = Doctor()
    doctor.id_clinic = clinic.id
    doctor.email = request.json.get('email')
    doctor.name = request.json.get('name')
    doctor.lastname = request.json.get('lastname')
    doctor.specialty = request.json.get('specialty')
    doctor.password = generate_password_hash(request.json.get('password'))

    db.session.add(doctor)
    db.session.commit()

    return jsonify(Success='Doctor created'), 201

@api.route('/clinic/doctor', methods=['GET']) #checked
@jwt_required()
def get_doctors():
    current_user = get_jwt_identity()
    clinic = Clinic.query.filter_by(email=current_user).first()
    doctors = Doctor.query.filter_by(id_clinic=clinic.id).all()
    return jsonify([i.serialize() for i in doctors]), 200

@api.route('/clinic/doctor/<int:id_doctor>', methods=['DELETE'])
@jwt_required()
def delete_doctor(id_doctor):
    current_user = get_jwt_identity()
    clinic = Clinic.query.filter_by(email=current_user).first()
    doctor = Doctor.query.filter_by(id_clinic=clinic.id, id=id_doctor).first()
    if doctor is None:
        return jsonify(Error="Doctor not found"), 404
    db.session.delete(doctor)
    db.session.commit()
    return jsonify(Success="Doctor deleted"), 203

@api.route('/clinic/reservations/<int:id_reservation>/change', methods=['PUT'])
@jwt_required()
def change_reservation(id_reservation):
    current_user = get_jwt_identity()
    clinic = Clinic.query.filter_by(email=current_user).first()
    reservation = Reservation.query.filter_by(id_clinic=clinic.id, id=id_reservation).first()
    if reservation is None:
        return jsonify(Error="Reservation not found"), 404
    status = request.json.get('status')
    if status is None:
        return jsonify(Error="Bad status"), 400
    if status == 'confirmed':
        reservation.status = Reservation_Status.confirmed
    elif status == 'canceled':
        reservation.status = Reservation_Status.canceled
    elif status == 'available':
        reservation.status = Reservation_Status.available
        reservation.id_pet = None
        reservation.id_user = None
    elif status == 'missed':
        reservation.status = Reservation_Status.missed
    
    db.session.commit()
    return jsonify(Success="Reservation status changed"), 200


@api.route('/doctor/login', methods=['POST']) #checked
def login_doctor():
    email = request.json.get("email", None)
    password = request.json.get("password", None)
    doctor = Doctor.query.filter_by(email=email).first()        
    if doctor is not None and check_password_hash(doctor.password, password):
        access_token = create_access_token(identity=email, expires_delta=sessiontime)
        return jsonify(access_token=access_token), 201
    else:
        return jsonify({"Error": "Bad username or password"}), 401

@api.route('/doctor/info', methods=['GET'])
@jwt_required()
def info_doctor():
    current_user = get_jwt_identity()
    doctor = Doctor.query.filter_by(email=current_user).first()

    return jsonify(doctor.serialize()), 200

@api.route('/doctor/reservations/add', methods=['POST'])
@jwt_required()
def add_reservation_doctor():
    current_user = get_jwt_identity()
    doctor = Doctor.query.filter_by(email=current_user).first()

    reservation = Reservation()
    reservation.id_doctor = doctor.id
    reservation.id_clinic = doctor.clinic.id
    reservation.status = Reservation_Status.available
    hour_start = request.json.get('hour_start')
    hour_end = request.json.get('hour_end')
    reservation.date_start = datetime.strptime(hour_start, "%d/%m/%Y %H:%M:%S")
    reservation.date_end = datetime.strptime(hour_end,  "%d/%m/%Y %H:%M:%S")

    db.session.add(reservation)
    db.session.commit()
    
    print(reservation.serialize())
    return jsonify(Success="Reservation added"), 201

@api.route('/doctor/reservations', methods=['GET'])
@jwt_required()
def get_hours_doctor():
    current_user = get_jwt_identity()
    doctor = Doctor.query.filter_by(email=current_user).first()
    reservations = Reservation.query.filter_by(id_doctor=doctor.id).all()
    return jsonify([i.serialize() for i in reservations]), 200

@api.route('/doctor/reservations/<int:id_reservation>/change', methods=['PUT'])
@jwt_required()
def change_reservation_doctor(id_reservation):
    current_user = get_jwt_identity()
    doctor = Doctor.query.filter_by(email=current_user).first()
    reservation = Reservation.query.filter_by(id_doctor=doctor.id, id=id_reservation).first()
    if reservation is None:
        return jsonify(Error="Reservation not found"), 404
    status = request.json.get('status')
    if status is None:
        return jsonify(Error="Bad status"), 400
    if status == 'finished':
        reservation.status = Reservation_Status.finished
    elif status == 'missed':
        reservation.status = Reservation_Status.missed
    
    db.session.commit()
    return jsonify(Success="Reservation status changed"), 200

@api.route('/doctor/attending/<int:pet_id>', methods=['GET'])
@jwt_required()
def get_pet_info_doctor(pet_id):
    current_user = get_jwt_identity()
    doctor = Doctor.query.filter_by(email=current_user).first()
    if doctor is None:
        return jsonify(Error="Doctor not found"), 404
    pet = Pet.query.filter_by(id=pet_id).first()
    if pet is None:
        return jsonify(Error="Pet not found"), 404
    return jsonify(Pet=pet.serialize(), History=pet.serialize_history()), 200

@api.route('/doctor/attending/<int:pet_id>/history/vaccine/add', methods=['POST'])
@jwt_required()
def add_vaccine_user_to_pet(pet_id):
    current_user = get_jwt_identity()
    doctor = Doctor.query.filter_by(email=current_user).first()
    if doctor is None:
        return jsonify(Error="Doctor not found"), 404
    pet = Pet.query.filter_by(id=pet_id).first()
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


@api.route('/doctor/attending/<int:pet_id>/history/surgery/add', methods=['POST'])
@jwt_required()
def add_surgery_user_to_pet(pet_id):
    current_user = get_jwt_identity()
    doctor = Doctor.query.filter_by(email=current_user).first()
    if doctor is None:
        return jsonify(Error="Doctor not found"), 404

    pet = Pet.query.filter_by(id=pet_id).first()
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

@api.route('/doctor/attending/<int:pet_id>/history/diagnostic/add', methods=['POST'])
@jwt_required()
def add_diagnostic_user_to_pet(pet_id):
    current_user = get_jwt_identity()
    doctor = Doctor.query.filter_by(email=current_user).first()
    if doctor is None:
        return jsonify(Error="Doctor not found"), 404

    pet = Pet.query.filter_by(id=pet_id).first()
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

    return jsonify(foundation.serialize()), 200

@api.route('/foundation/info', methods=['PUT'])
@jwt_required()
def update_foundation():
    current_user = get_jwt_identity()
    foundation = Foundation.query.filter_by(email=current_user).first()
    foundation.name = request.json.get('name')
    foundation.address = request.json.get('address')
    foundation.phone = request.json.get('phone')
    foundation.email = request.json.get('email')
    if request.json.get('picture') is not None:
        foundation.picture = request.json.get('picture')
    if request.json.get('password') is not None:
        foundation.password = generate_password_hash(request.json.get('password'))
    db.session.commit()
    return jsonify(Success="Foundation updated"), 202

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

@api.route('/foundation/pets/<int:pet_id>', methods=['PUT'])
@jwt_required()
def update_foundation_pet(pet_id):
    current_user = get_jwt_identity()
    foundation = Foundation.query.filter_by(email=current_user).first()
    if foundation is None:
        return jsonify(Error="Foundation not found"), 404
    pet = Pet.query.filter_by(id_foundation=foundation.id, id=pet_id).first()
    if pet is None:
        return jsonify(Error="Pet not found"), 404
    pet.name = request.json.get('name')
    pet.code_chip = request.json.get('code_chip')
    pet.breed = request.json.get('breed')
    if request.json.get('picture') is not None:
        pet.picture = request.json.get('picture')
    
    db.session.commit()
    return jsonify(Success="Pet updated"), 202

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
    
    return jsonify(pet.serialize_history()), 200


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
