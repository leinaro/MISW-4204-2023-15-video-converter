import os
import time
from flask import Flask
from flask_cors import CORS
from flask_restful import Api
from views import *
from models import db
from flask_jwt_extended import JWTManager
from sqlalchemy.exc import OperationalError

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "postgresql://postgres:1234@localhost:5432/nube1")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["PROPAGATE_EXCEPTIONS"] = True
app.config["JWT_SECRET_KEY"] = "frase-secreta"
app.config['UPLOAD_FOLDER'] = os.environ.get('UPLOAD_FOLDER', '/app/videos/uploaded')
app.config['CONVERTED_FOLDER'] = os.environ.get('CONVERTED_FOLDER', '/app/videos/converted')


app_context = app.app_context()
app_context.push()

db.init_app(app)

max_retires = 5
retry_interval = 1
for retry in range(max_retires):
    try:
        with app.app_context():
            db.create_all()
        break
    except OperationalError as e:
        if retry < max_retires - 1:
            print(f"Database connection failed. Retrying in {retry_interval} seconds...")
            time.sleep(retry_interval)
            continue
        else:
            raise e

cors = CORS(app, resources={r"/*": {"origins": "*"}})

api = Api(app)

api.add_resource(ViewSignInUser, "/api/auth/signup")
api.add_resource(ViewLogin, "/api/auth/login")
api.add_resource(ViewConverter, "/api/tasks")
api.add_resource(ViewConverterStatus, "/api/tasks/<string:task_id>")
api.add_resource(ViewFileDownload, "/api/download")

jwt = JWTManager(app)
