from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import os
from flask_sqlalchemy import SQLAlchemy
import resend

load_dotenv()

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    resend.api_key = os.getenv('RESEND_API')

    db.init_app(app)

    CORS(app, supports_credentials=True)

    from app.auth.routes import main_authBP
    app.register_blueprint(main_authBP)



    return(app)