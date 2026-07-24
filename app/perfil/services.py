from app.models import user_profile
from app import db
from flask import jsonify
from flask_jwt_extended import jwt_required

def resgatar_dados_usuario(UserId):
    try:
        user_profiles = user_profile.query.filter_by(user_id=UserId).first()
    except Exception as e:
        return jsonify({'status': "erro ao tentar contatadar o db"}), 500

    if not user_profiles:
        return jsonify({'status': 'usuario não encontrado'})

    user_data = {
        "nome_completo": getattr(user_profiles, 'nome_completo', None),
        "primeiro_nome": getattr(user_profiles, 'primeiro_nome', None),
        "foto_url": getattr(user_profiles, 'foto_url', None),
        "bio": getattr(user_profiles, 'bio', None),
        "data_de_nascimento": getattr(user_profiles, 'data_de_nascimento', None),
        "vendedor": getattr(user_profiles, 'vendedor', None),
        "nivel": getattr(user_profiles, 'nivel', None),
        "compras": getattr(user_profiles, 'compras', None),
    }

    return jsonify(user_data)
