import os
from flask import Flask, request, jsonify, url_for, send_from_directory
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from api.utils import APIException, generate_sitemap
from config import DevelopmentConfig, ProductionConfig

ENV = os.getenv("FLASK_ENV")
static_file_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../public/')
app = Flask(__name__)
app.url_map.strict_slashes = False
mail = Mail(app)

# database configuration
if ENV == "development":
    app.config.from_object(DevelopmentConfig)
elif ENV == "production":
    app.config.from_object(ProductionConfig)

from api.models import db
from api.routes import api
from api.clinic import clinic
from api.doctor import doctor
from api.user import user
from api.foundation import foundation
from api.admin import setup_admin

MIGRATE = Migrate(app, db)
db.init_app(app)
mail.init_app(app)
jwt = JWTManager(app)

# Allow CORS requests to this API
CORS(app)

# add the admin
setup_admin(app)

# Add all endpoints form the API with a "api" prefix
app.register_blueprint(api, url_prefix='/api')
app.register_blueprint(clinic, url_prefix='/api/clinic')
app.register_blueprint(doctor, url_prefix='/api/doctor')
app.register_blueprint(user, url_prefix='/api/user')
app.register_blueprint(foundation, url_prefix='/api/foundation')

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    if ENV == "development":
        return generate_sitemap(app)
    return send_from_directory(static_file_dir, 'index.html')

# any other endpoint will try to serve it like a static file
@app.route('/<path:path>', methods=['GET'])
def serve_any_other_file(path):
    if not os.path.isfile(os.path.join(static_file_dir, path)):
        path = 'index.html'
    response = send_from_directory(static_file_dir, path)
    response.cache_control.max_age = 0 # avoid cache memory
    return response

# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3001))
    app.run(host='0.0.0.0', port=PORT, debug=True)
