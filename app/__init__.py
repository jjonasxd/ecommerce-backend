from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import os
from flask_sqlalchemy import SQLAlchemy
import resend
from flask_jwt_extended import JWTManager
from datetime import timedelta

load_dotenv()

db = SQLAlchemy()
upload_folder = 'app/uploads'

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    resend.api_key = os.getenv('RESEND_API')

    #JWT
    jwt = JWTManager()

    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
    app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
    app.config['JWT_COOKIE_SECURE'] = False
    app.config['JWT_COOKIE_CSR_PROTECT'] = False

    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=15)
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=7)

    app.secret_key = os.getenv('APP_SECRET_KEY')

    db.init_app(app)
    jwt.init_app(app)

    CORS(app, supports_credentials=True)

    from app.auth.routes import main_authBP
    app.register_blueprint(main_authBP)

    from app.perfil.routes import BP_perfil
    app.register_blueprint(BP_perfil)

    return(app)