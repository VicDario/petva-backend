from flask import Flask, jsonify, request, render_template
from flask_jwt_extended import create_access_token, jwt_required, JWTManager, get_jwt_identity
from flask_migrate import Migrate
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import timedelta
from models import db, User, Clinic, Doctor, Fundation, Pet
from dotenv import dotenv_values

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['ENV'] = bool(dotenv_values(".env")["DEVELOPMENT"])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config["JWT_SECRET_KEY"] = dotenv_values(".env")["SECRET_KEY"]

db.init_app(app)
Migrate(app, db)
jwt = JWTManager(app)

@app.route('/', methods=['GET'])
def main():
    return jsonify(Test="Test"), 200

@app.route('/api/user/register', methods=['POST'])
def register_user():
    user = User()
    user.email = request.json.get('email')
    user.name = request.json.get('name')
    user.lastname = request.json.get('lastname')
    user.password = generate_password_hash(request.json.get('password'))

    user.save()

    return jsonify(Success='User created'), 201

@app.route('/api/user/login', methods=['POST'])
def login_user():
    email = request.json.get("email", None)
    password = request.json.get("password", None)
    user = User.query.filter_by(email=email).first()        
    if user is not None and check_password_hash(user.password, password):
        access_token = create_access_token(identity=email, expires=timedelta(hours=23))
        return jsonify(access_token=access_token), 201
    else:
        return jsonify({"Error": "Bad username or password"}), 401

@app.route('/api/clinic/register', methods=['POST'])
def register_clinic():
    clinic = Clinic()
    clinic.email = request.json.get('email')
    clinic.name = request.json.get('name')
    clinic.address = request.json.get('address')
    clinic.phone = request.json.get('phone')
    clinic.password = generate_password_hash(request.json.get('password'))

    clinic.save()

    return jsonify(Success='Clinic created'), 201

@app.route('/api/clinic/login', methods=['POST'])
def login_clinic():
    email = request.json.get("email", None)
    password = request.json.get("password", None)
    clinic = Clinic.query.filter_by(email=email).first()        
    if clinic is not None and check_password_hash(clinic.password, password):
        access_token = create_access_token(identity=email, expires=timedelta(hours=23))
        return jsonify(access_token=access_token), 201
    else:
        return jsonify({"Error": "Bad username or password"}), 401


@app.route('/api/doctor/register', methods=['POST']) #Incomplete
def register_doctor():
    doctor = Doctor()
    doctor.email = request.json.get('email')
    doctor.name = request.json.get('name')
    doctor.lastname = request.json.get('lastname')
    doctor.specialty = request.json.get('specialty')
    doctor.password = generate_password_hash(request.json.get('password'))

    doctor.save()

    return jsonify(Success='Clinic created'), 201

@app.route('/api/doctor/login', methods=['POST'])
def login_doctor():
    email = request.json.get("email", None)
    password = request.json.get("password", None)
    doctor = Doctor.query.filter_by(email=email).first()        
    if doctor is not None and check_password_hash(doctor.password, password):
        access_token = create_access_token(identity=email, expires=timedelta(hours=23))
        return jsonify(access_token=access_token), 201
    else:
        return jsonify({"Error": "Bad username or password"}), 401

@app.route('/api/fundation/register', methods=['POST'])
def register_fundation():
    fundation = Fundation()
    fundation.email = request.json.get('email')
    fundation.name = request.json.get('name')
    fundation.lastname = request.json.get('lastname')
    fundation.specialty = request.json.get('specialty')
    fundation.password = generate_password_hash(request.json.get('password'))

    fundation.save()

    return jsonify(Success='Clinic created'), 201

@app.route('/api/fundation/login', methods=['POST'])
def login_fundation():
    email = request.json.get("email", None)
    password = request.json.get("password", None)
    fundation = Doctor.query.filter_by(email=email).first()        
    if fundation is not None and check_password_hash(fundation.password, password):
        access_token = create_access_token(identity=email, expires=timedelta(hours=23))
        return jsonify(access_token=access_token), 201
    else:
        return jsonify({"Error": "Bad username or password"}), 401


if __name__ == '__main__':
    app.run()
