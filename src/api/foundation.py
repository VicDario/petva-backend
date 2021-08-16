from flask import json, request, jsonify, Blueprint, render_template
from api.models import Vaccine, Diagnostic, Surgery, Foundation, History, db, User, Pet, Specie, Pet_state
from werkzeug.security import check_password_hash, generate_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, decode_token
from datetime import timedelta, datetime
from services.mail_service import send_email
from app import app

foundation = Blueprint('api_foundation', __name__)

sessiontime = timedelta(hours=1)

@foundation.route('/register', methods=['POST'])
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

@foundation.route('/login', methods=['POST'])
def login_foundation():
    email = request.json.get("email", None)
    password = request.json.get("password", None)
    foundation = Foundation.query.filter_by(email=email).first()        
    if foundation is not None and check_password_hash(foundation.password, password):
        access_token = create_access_token(identity=email, expires_delta=sessiontime)
        return jsonify(access_token=access_token), 201
    else:
        return jsonify({"Error": "Bad username or password"}), 401

@foundation.route('/info', methods=['GET'])
@jwt_required()
def info_foundation():
    current_user = get_jwt_identity()
    foundation = Foundation.query.filter_by(email=current_user).first()

    return jsonify(foundation.serialize()), 200

@foundation.route('/info', methods=['PUT'])
@jwt_required()
def update_foundation():
    current_user = get_jwt_identity()
    foundation = Foundation.query.filter_by(email=current_user).first()
    if request.json.get('name') is not None:
        foundation.name = request.json.get('name')
    if request.json.get('address') is not None:
        foundation.address = request.json.get('address')
    if request.json.get('phone') is not None:
        foundation.phone = request.json.get('phone')
    if request.json.get('email') is not None:
        foundation.email = request.json.get('email')
    if request.json.get('picture') is not None:
        foundation.picture = request.json.get('picture')
    if request.json.get('password') is not None:
        foundation.password = generate_password_hash(request.json.get('password'))
    db.session.commit()
    return jsonify(Success="Foundation updated"), 202

@foundation.route('/forgot', methods=['POST'])
def forget_password():
    email = request.json.get('email')
    foundation = Foundation.query.filter_by(email=email).first()
    if foundation is None:
        return jsonify(Error="Foundation not found"), 404

    reset_token = create_access_token(identity=foundation.email, expires_delta=sessiontime)

    url = app.config['URL_FRONTEND'] + '/foundation/reset/'

    send_email('Reset Your Password',
                sender=app.config['MAIL_USERNAME'],
                recipients=[foundation.email],
                text_body=render_template('reset_password.txt', url=url + reset_token),
                html_body=render_template('reset_password.html', url=url + reset_token))

    return jsonify(Success="Email sended"), 202

@foundation.route('/reset', methods=['POST'])
def reset_password():
    token = request.json.get('token')
    decode = decode_token(token)
    email = decode['sub']
    foundation = Foundation.query.filter_by(email=email).first()
    if foundation is None:
        return jsonify(Error="Foundation not found"), 404
    foundation.password = generate_password_hash(request.json.get('password'))
    db.session.commit()
    return jsonify(Success="Password reset"), 202

@foundation.route('/pets/add', methods=['POST'])
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

@foundation.route('/pets/in_adoption', methods=['GET'])
@jwt_required()
def foundation_pets_in_adoption():
    current_user = get_jwt_identity()
    foundation = Foundation.query.filter_by(email=current_user).first()
    pets = Pet.query.filter_by(id_foundation=foundation.id, state=Pet_state.adoption).all()

    return jsonify(list(map(lambda pet: pet.serialize(), pets))), 200


@foundation.route('/pets/owned', methods=['GET'])
@jwt_required()
def foundation_pets_owned():
    current_user = get_jwt_identity()
    foundation = Foundation.query.filter_by(email=current_user).first()
    pets = Pet.query.filter_by(id_foundation=foundation.id, state=Pet_state.owned).all()

    return jsonify(list(map(lambda pet: pet.serialize(), pets)))

@foundation.route('/pets/<int:pet_id>', methods=['GET'])
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

@foundation.route('/pets/<int:pet_id>', methods=['PUT'])
@jwt_required()
def update_foundation_pet(pet_id):
    current_user = get_jwt_identity()
    foundation = Foundation.query.filter_by(email=current_user).first()
    if foundation is None:
        return jsonify(Error="Foundation not found"), 404
    pet = Pet.query.filter_by(id_foundation=foundation.id, id=pet_id).first()
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
    return jsonify(Success="Pet updated"), 202

@foundation.route('/transfer', methods=['POST'])
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

@foundation.route('/pets/<int:pet_id>/history', methods=['GET'])
@jwt_required()
def get_history_pet_foundation(pet_id):
    current_user = get_jwt_identity()
    foundation = Foundation.query.filter_by(email=current_user).first()
    pet = Pet.query.filter_by(id_foundation=foundation.id, id=pet_id).first()

    if pet is None:
        return jsonify(Error="Pet not found"), 404
    
    return jsonify(pet.serialize_history()), 200


@foundation.route('/pets/<int:pet_id>/history/vaccine/add', methods=['POST'])
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

@foundation.route('/pets/<int:pet_id>/history/diagnostic/add', methods=['POST'])
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

@foundation.route('/pets/<int:pet_id>/history/surgery/add', methods=['POST'])
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