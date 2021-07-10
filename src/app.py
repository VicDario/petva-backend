from flask import Flask, jsonify, request, render_template
from flask_jwt_extended import create_access_token, jwt_required, JWTManager, get_jwt_identity
from flask_migrate import Migrate
from models import db
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

if __name__ == '__main__':
    app.run()
