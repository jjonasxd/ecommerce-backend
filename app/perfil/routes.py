from flask import Flask, Blueprint, request, session, g, send_file
from app.perfil.services import *
from flask_jwt_extended import get_jwt_identity, create_access_token, set_access_cookies
from app.decorator import login_required
from app import upload_folder


BP_perfil = Blueprint('rotas_perfil', __name__)

@BP_perfil.route('/api/perfil-dados', methods=['GET'])
@login_required
def dados_do_perfil():
    user_id = g.user_id
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

    return response, 201

@BP_perfil.route('/api/perfil-avatar', methods=["PUT"])
@login_required
def mudancas():
    foto = request.files.get('foto')
    user_id = g.user_id

    if not user_id:
        return jsonify({'status': 'User_id vazio'}), 422

    if foto:
        v_status, v_erro = validar_arquivo(foto)

        if v_erro:
            return jsonify({'status': v_status})

        a_status, a_erro, a_url, user_uuid = avatar_verificar_existencia(user_id)

        if a_erro:
            return jsonify({'status': a_status})
        
        if a_url:
            return atualizar_avatar(user_uuid, foto, user_id)
        else:
            if user_uuid:
                 return criar_avatar(user_uuid, foto, user_id)
            else:
                c_status, user_uuid, c_erro, c_status_code = criar_perfil(user_id)

                if c_erro:
                    return jsonify({'status': c_status}), c_status_code
                
                if not user_uuid:
                    return jsonify({'status': c_status})
                
                return criar_avatar(user_uuid, foto, user_id)
    else:
        return jsonify({'status': 'foto não enviada'}), 204

@BP_perfil.route('/api/uploads/<string:user_uuid>/<path:filename>')
def uploads(user_uuid, filename):
    path = os.path.abspath(f'{upload_folder}/{user_uuid}/{filename}') # Pqp fiquei 1 hora para descobrir que não era o caminho relativo, mais sim absoluto

    return send_file(path) # Usei send_file mais poderia ser send_from_directory

@BP_perfil.route('/api/perfil-changes', methods=['POST'])
@login_required
def modificar():
    dados = request.json
    user_id = g.user_id

    if not user_id:
        return jsonify({'status': 'Seu JWT esta vazio'})

    if dados:
        status, erro = testar_dados(dados)
        if erro:
            return jsonify({'status', status})
        return alterar_dados(dados, user_id)
    else:
        return jsonify({'status': 'nenhum dado enviado'}), 204

@BP_perfil.route('/api/exluir-conta', methods=['GET']) # Não joguem pedra, e apenas para finalizar o perfil
@jwt_required()
def excluir_conta():
    user_id = get_jwt_identity()

    if not user_id:
        return jsonify({'status': 'ID faltando'})

    return excluir_tudo(user_id)

    