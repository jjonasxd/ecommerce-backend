from app.models import user_profile
from app import db
from flask_jwt_extended import jwt_required
from flask import jsonify

def resgatar_dados_usuario(UserId):
    try:
        user_profile = user_profile.query.filter_by(user_id=UserId).first()
    except Exception as e:
        return jsonify({'status': e})

    return jsonify(user_profile)