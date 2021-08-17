from flask import json, request, jsonify, Blueprint, render_template
from api.models import Reservation, db, Clinic, Doctor, Reservation_Status
from werkzeug.security import check_password_hash, generate_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, decode_token
from datetime import timedelta
from services.mail_service import send_email
from services.token import generate_confirmation_token, confirm_token
from app import app

clinic = Blueprint('api_clinic', __name__)

sessiontime = timedelta(hours=1)

@clinic.route('/register', methods=['POST']) #checked
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

    url = app.config['URL_FRONTEND'] + '/clinic/confirm'
    token = generate_confirmation_token(clinic.email)
    send_email('Reset Your Password',
                sender=app.config['MAIL_USERNAME'],
                recipients=[clinic.email],
                text_body=render_template('confirm_email_organization.txt', url=url + token),
                html_body=render_template('confirm_email_organization.html', url=url + token))

    return jsonify(Success='Clinic created'), 201

@clinic.route('/confirm')
def confirm_clinic():
    token = request.json.get('token')
    email = confirm_token(token, 172800)
    if email is False:
        return jsonify(Error='Invalid token'), 409
    clinic = Clinic.query.filter_by(email=email).first()
    if clinic is None:
        return jsonify(Error='Clinic not found'), 409

    clinic.confirmed = True
    db.session.commit()

    send_email('Primer paso completado',
                sender=app.config['MAIL_USERNAME'],
                recipients=[clinic.email],
                text_body=render_template('new_clinic_first_step.txt'),
                html_body=render_template('new_clinic_first_step.html'))

    return jsonify(Success='Clinic confirmed'), 200


@clinic.route('/login', methods=['POST']) #checked
def login_clinic():
    email = request.json.get("email", None)
    password = request.json.get("password", None)
    clinic = Clinic.query.filter_by(email=email).first()        
    if clinic is not None and check_password_hash(clinic.password, password):
        access_token = create_access_token(identity=email, expires_delta=sessiontime)
        return jsonify(access_token=access_token), 201
    else:
        return jsonify({"Error": "Bad username or password"}), 401

@clinic.route('/info', methods=['GET'])
@jwt_required()
def info_clinic():
    current_user = get_jwt_identity()
    clinic = Clinic.query.filter_by(email=current_user).first()

    return jsonify(clinic.serialize()), 200

@clinic.route('/forgot', methods=['POST'])
def forget_password():
    email = request.json.get('email')
    clinic = Clinic.query.filter_by(email=email).first()
    if clinic is None:
        return jsonify(Error="Clinic not found"), 404

    reset_token = create_access_token(identity=clinic.email, expires_delta=sessiontime)

    url = app.config['URL_FRONTEND'] + '/clinic/reset/'

    send_email('Reset Your Password',
                sender=app.config['MAIL_USERNAME'],
                recipients=[clinic.email],
                text_body=render_template('reset_password.txt', url=url + reset_token),
                html_body=render_template('reset_password.html', url=url + reset_token))

    return jsonify(Success="Email sended"), 202

@clinic.route('/reset', methods=['POST'])
def reset_password():
    token = request.json.get('token')
    decode = decode_token(token)
    email = decode['sub']
    clinic = Clinic.query.filter_by(email=email).first()
    if clinic is None:
        return jsonify(Error="Clinic not found"), 404
    clinic.password = generate_password_hash(request.json.get('password'))
    db.session.commit()
    return jsonify(Success="Password reset"), 202

@clinic.route('/check/reservations', methods=['GET'])
@jwt_required()
def check_reserved_clinic():
    current_user = get_jwt_identity()
    clinic = Clinic.query.filter_by(email=current_user).first()
    if clinic is None:
        return jsonify(Error="Clinic not found"), 404
    print(clinic.name)
    reservations = Reservation.query.filter_by(id_clinic=clinic.id).all()
    return jsonify([i.serialize() for i in reservations]), 200

@clinic.route('/doctor/register', methods=['POST']) #checked
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

@clinic.route('/doctor', methods=['GET']) #checked
@jwt_required()
def get_doctors():
    current_user = get_jwt_identity()
    clinic = Clinic.query.filter_by(email=current_user).first()
    doctors = Doctor.query.filter_by(id_clinic=clinic.id).all()
    return jsonify([i.serialize() for i in doctors]), 200

@clinic.route('/doctor/<int:id_doctor>', methods=['DELETE'])
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

@clinic.route('/reservations/<int:id_reservation>/change', methods=['PUT'])
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