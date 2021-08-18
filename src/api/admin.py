from flask import json, request, jsonify, Blueprint, render_template
from api.models import Foundation, db, User, Pet, Clinic, Doctor, Admin
from werkzeug.security import check_password_hash, generate_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, decode_token
from datetime import timedelta, datetime
from services.mail_service import send_email
from services.token import generate_confirmation_token, confirm_token
from app import app

admin = Blueprint('api_admin', __name__)

sessiontime = timedelta(hours=1)

@admin.route('/login', methods=['POST'])
def login():
    email = request.json.get('email')
    password = request.json.get('password')
    admin = Admin.query.filter_by(email=email).first()
    if admin is None:
        return jsonify({'message': 'Invalid email or password'}), 401
    if admin is not None and check_password_hash(admin.password, password):
        token = create_access_token(identity=email, expires_delta=sessiontime)
        return jsonify(token=token), 200


@admin.route('/register', methods=['POST'])
def register():
    if request.json.get('secret_key') == app.config['SECRET_KEY']:
        email = request.json.get('email')
        password = request.json.get('password')
        admin = Admin()
        admin.email = email
        admin.name = request.json.get('name')
        admin.password = generate_password_hash(password)
        db.session.add(admin)
        db.session.commit()
        return jsonify({'message': 'Successfully registered'}), 200
    else:
        return jsonify({'message': 'Invalid'}), 401

@admin.route('/info', methods=['GET'])
@jwt_required()
def info_user(): 
    current_admin = get_jwt_identity()
    admin = Admin.query.filter_by(email=current_admin).first()
    return jsonify(admin.serialize()), 200

@admin.route('/users', methods=['GET'])
@admin.route('/users/<int:page>', methods=['GET'])
@jwt_required()
def get_users(page = 1):
    current = get_jwt_identity()
    admin = Admin.query.filter_by(email=current).first()
    if admin is None:
        return jsonify({'message': 'Invalid'}), 401
    users = Pet.query.paginate(page=page, per_page=30)
    return jsonify([user.serialize() for user in users.items], users.pages, users.has_next, users.has_prev), 200

@admin.route('/clinics', methods=['GET'])
@admin.route('/clinics/<int:page>', methods=['GET'])
@jwt_required()
def get_clinics(page = 1):
    current = get_jwt_identity()
    admin = Admin.query.filter_by(email=current).first()
    if admin is None:
        return jsonify({'message': 'Invalid'}), 401
    clinics = Clinic.query.paginate(page=page, per_page=30)
    return jsonify([clinic.serialize() for clinic in clinics.items], clinics.pages, clinics.has_next, clinics.has_prev), 200

@admin.route('/doctors', methods=['GET'])
@admin.route('/doctors/<int:page>', methods=['GET'])
@jwt_required()
def get_doctors(page = 1):
    current = get_jwt_identity()
    admin = Admin.query.filter_by(email=current).first()
    if admin is None:
        return jsonify({'message': 'Invalid'}), 401
    doctors = Doctor.query.paginate(page=page, per_page=30)
    return jsonify([doctor.serialize() for doctor in doctors.items], doctors.pages, doctors.has_next, doctors.has_prev), 200

@admin.route('/foundations', methods=['GET'])
@admin.route('/foundations/<int:page>', methods=['GET'])
@jwt_required()
def get_foundations(page = 1):
    current = get_jwt_identity()
    admin = Admin.query.filter_by(email=current).first()
    if admin is None:
        return jsonify({'message': 'Invalid'}), 401
    foundations = Foundation.query.paginate(page=page, per_page=30)
    return jsonify([foundation.serialize() for foundation in foundations.items], foundations.pages, foundations.has_next, foundations.has_prev), 200

@admin.route('/clinics/notauthorized', methods=['GET'])
@jwt_required()
def get_clinics_not_authorized():
    current = get_jwt_identity()
    admin = Admin.query.filter_by(email=current).first()
    if admin is None:
        return jsonify({'message': 'Invalid'}), 401
    clinics = Clinic.query.filter_by(authorized=False).paginate(page=1, per_page=30)
    return jsonify([clinic.serialize() for clinic in clinics.items], clinics.pages, clinics.has_next, clinics.has_prev), 200

@admin.route('/foundations/notauthorized', methods=['GET'])
@jwt_required()
def get_foundations_not_authorized():
    current = get_jwt_identity()
    admin = Admin.query.filter_by(email=current).first()
    if admin is None:
        return jsonify({'message': 'Invalid'}), 401
    foundations = Foundation.query.filter_by(authorized=False).paginate(page=1, per_page=30)
    return jsonify([foundation.serialize() for foundation in foundations.items], foundations.pages, foundations.has_next, foundations.has_prev), 200

@admin.route('/clinics/<int:id>/authorized', methods=['GET'])
@jwt_required()
def confirm_clinic(id):
    current = get_jwt_identity()
    admin = Admin.query.filter_by(email=current).first()
    if admin is None:
        return jsonify({'message': 'Invalid'}), 401
    clinic = Clinic.query.filter_by(id=id).first()
    if clinic is None:
        return jsonify({'message': 'Invalid'}), 401
    clinic.authorized = True
    db.session.commit()
    url = app.config['URL_FRONTEND'] + '/clinic/login'
    send_email('Identidad comprobada',
                sender=app.config['MAIL_USERNAME'],
                recipients=[clinic.email],
                text_body=render_template('new_organization_completed.txt', url=url),
                html_body=render_template('new_organization_completed.html', url=url))
    return jsonify({'message': 'Clinic confirmed'}), 200

@admin.route('/foundations/<int:id>/authorized', methods=['GET'])
@jwt_required()
def confirm_foundations(id):
    current = get_jwt_identity()
    admin = Admin.query.filter_by(email=current).first()
    if admin is None:
        return jsonify({'message': 'Invalid'}), 401
    clinic = Clinic.query.filter_by(id=id).first()
    if clinic is None:
        return jsonify({'message': 'Invalid'}), 401
    clinic.authorized = True
    db.session.commit()
    url = app.config['URL_FRONTEND'] + '/foundation/login'
    send_email('Identidad comprobada',
                sender=app.config['MAIL_USERNAME'],
                recipients=[clinic.email],
                text_body=render_template('new_organization_completed.txt', url=url),
                html_body=render_template('new_organization_completed.html', url=url))
    return jsonify({'message': 'Clinic confirmed'}), 200
