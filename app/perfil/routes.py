from flask import Flask, Blueprint, request
from app.perfil.services import *
from flask_jwt_extended import get_jwt_identity, create_access_token, set_access_cookies

BP_perfil = Blueprint('rotas_perfil', __name__)

@BP_perfil.route('/api/perfil-dados', methods=['GET'])
@jwt_required()
def dados_do_perfil():
    user_id = get_jwt_identity()
    print(user_id, flush=True)

    return resgatar_dados_usuario(user_id)

@BP_perfil.route('/api/refresh', methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    user_id = get_jwt_identity()
    print(user_id, flush=True)
    NewAccessToken = create_access_token(identity=str(user_id))

    response = jsonify({'status': 'Cookie atualizado com sucesso'})

    set_access_cookies(response, NewAccessToken)

    return response, 200

@BP_perfil.route('/api/perfil-changes', methods=["POST"])
def mudancas():
    pass