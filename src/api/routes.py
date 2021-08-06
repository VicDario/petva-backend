from flask import json, request, jsonify, Blueprint
from api.models import Reservation, Diagnostic, History, Surgery, Vaccine, db, User, Pet, Clinic, Doctor, Foundation, Specie, Pet_state, Reservation_Status
from werkzeug.security import check_password_hash, generate_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from datetime import timedelta, datetime, timezone

api = Blueprint('api', __name__)

sessiontime = timedelta(hours=1)

@api.route('/', methods=['GET'])
def main():
    return jsonify(Test="Test"), 200

@api.route('/pets/in_adoption/<int:page>', methods=['GET'])
def get_pets_in_adoption(page=1):
    pets = Pet.query.filter_by(state=Pet_state.adoption).paginate(page=page, per_page=12)
    return jsonify([pet.serialize_info_for_adoption() for pet in pets.items], pets.pages, pets.has_next, pets.has_prev), 200

@api.route('/pets/lost/<int:page>', methods=['GET'])
def get_pets_lost(page=1):
    pets = Pet.query.filter_by(state=Pet_state.lost).paginate(page=page, per_page=12)
    return jsonify([pet.serialize_info_for_lost() for pet in pets.items], pets.pages, pets.has_next, pets.has_prev), 200

@api.route('/check', methods=['GET'])
@jwt_required()
def check_key():
    return jsonify(Success="Checked"), 200
