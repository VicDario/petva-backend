from flask import json, request, jsonify, Blueprint, render_template
from api.models import Reservation, History, db, User, Pet, Clinic, Doctor, Specie, Pet_state, Reservation_Status
from werkzeug.security import check_password_hash, generate_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, decode_token
from datetime import timedelta, datetime
from services.mail_service import send_email
from services.token import generate_confirmation_token, confirm_token
from app import app

admin = Blueprint('api_admin', __name__)

@admin.route('/login', methods=['POST'])
def login():
    pass