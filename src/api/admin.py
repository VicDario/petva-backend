from flask import json, request, jsonify, Blueprint, render_template
from api.models import db, User, Pet, Clinic, Doctor, Admin
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
        admin.password = generate_password_hash(password)
        db.session.add(admin)
        db.session.commit()
        return jsonify({'message': 'Successfully registered'}), 200
    else:
        return jsonify({'message': 'Invalid'}), 401