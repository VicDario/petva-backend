from flask import json, request, jsonify, Blueprint
from api.models import Reservation, Diagnostic, History, Surgery, Vaccine, db, Pet, Clinic, Doctor, Reservation_Status
from werkzeug.security import check_password_hash, generate_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from datetime import timedelta, datetime, timezone

doctor = Blueprint('api_doctor', __name__)

sessiontime = timedelta(hours=1)

@doctor.route('/login', methods=['POST']) #checked
def login_doctor():
    email = request.json.get("email", None)
    password = request.json.get("password", None)
    doctor = Doctor.query.filter_by(email=email).first()        
    if doctor is not None and check_password_hash(doctor.password, password):
        access_token = create_access_token(identity=email, expires_delta=sessiontime)
        return jsonify(access_token=access_token), 201
    else:
        return jsonify({"Error": "Bad username or password"}), 401

@doctor.route('/info', methods=['GET'])
@jwt_required()
def info_doctor():
    current_user = get_jwt_identity()
    doctor = Doctor.query.filter_by(email=current_user).first()

    return jsonify(doctor.serialize()), 200

@doctor.route('/reservations/add', methods=['POST'])
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

@doctor.route('/reservations', methods=['GET'])
@jwt_required()
def get_hours_doctor():
    current_user = get_jwt_identity()
    doctor = Doctor.query.filter_by(email=current_user).first()
    reservations = Reservation.query.filter_by(id_doctor=doctor.id).all()
    return jsonify([i.serialize() for i in reservations]), 200

@doctor.route('/reservations/<int:id_reservation>/change', methods=['PUT'])
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

@doctor.route('/attending/<int:pet_id>', methods=['GET'])
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

@doctor.route('/attending/<int:pet_id>/history/vaccine/add', methods=['POST'])
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


@doctor.route('/attending/<int:pet_id>/history/surgery/add', methods=['POST'])
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

@doctor.route('/attending/<int:pet_id>/history/diagnostic/add', methods=['POST'])
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