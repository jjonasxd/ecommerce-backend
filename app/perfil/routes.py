from flask import Flask, Blueprint, request
from app.perfil.services import *
from flask_jwt_extended import get_jwt_identity, create_access_token

BP_perfil = Blueprint('rotas_perfil', __name__)

@BP_perfil.route('/api/perfil-dados', methods=['GET'])
@jwt_required()
def configs():
    user_id = get_jwt_identity()
    print(user_id, flush=True)
    resposta = resgatar_dados_usuario(user_id)

    return resposta

@BP_perfil.route('/api/refresh', methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    user_id = get_jwt_identity()
    NewAccessToken = create_access_token(identity=user_id)

    return jsonify(access_token=NewAccessToken), 200