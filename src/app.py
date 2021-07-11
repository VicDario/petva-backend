from flask import Flask, jsonify, request, render_template
from flask_jwt_extended import create_access_token, jwt_required, JWTManager, get_jwt_identity
from flask_migrate import Migrate
from werkzeug.security import check_password_hash, generate_password_hash
from models import db, User
from dotenv import dotenv_values

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['ENV'] = 'development'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config["JWT_SECRET_KEY"] = dotenv_values(".env")["SECRET_KEY"]

db.init_app(app)
Migrate(app, db)
jwt = JWTManager(app)

@app.route('/', methods=['GET'])
def main():
    return jsonify(Test="Test"), 200

@app.route('/api/register', methods=['POST'])
def register_user():
    user = User()
    user.email = request.json.get('email')
    user.name = request.json.get('name')
    user.lastname = request.json.get('lastname')
    user.password = generate_password_hash(request.json.get('password'))

    user.save()

    return jsonify(Success='User created'), 201

@app.route('/api/login', methods=['POST'])
def login():
    email = request.json.get("email", None)
    password = request.json.get("password", None)
    user = User.query.filter_by(email=email).first()        
    if user is not None and check_password_hash(user.password, password):
        access_token = create_access_token(identity=email)
        return jsonify(access_token=access_token), 201
    else:
        return jsonify({"Error": "Bad username or password"}), 401

if __name__ == '__main__':
    app.run()
