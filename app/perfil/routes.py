from flask import Flask, Blueprint, request, session, g
from app.perfil.services import *
from flask_jwt_extended import get_jwt_identity, create_access_token, set_access_cookies
from app.decorator import login_required

BP_perfil = Blueprint('rotas_perfil', __name__)

@BP_perfil.route('/api/perfil-dados', methods=['PUT'])
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

    return response, 200

@BP_perfil.route('/api/perfil-changes', methods=["PUT"])
@login_required
def mudancas():
    foto = request.files.get('foto')
    banner = request.files.get('banner')

    user_id = g.user_id

    if not user_id:
        return jsonify({'status': 'o token esta vazio'})

    if foto and foto != "":
        status = verificar_existencia(user_id)

        if status["erro"]:
            return jsonify({"status": status['status']})

        resp_uuid = status['uuid']
        if not resp_uuid or resp_uuid == "" or resp_uuid == None:
            if status.get('vazio'):
                res_avatar = atualizar_avatar(user_id, foto)

                if res_avatar['erro']:
                    return jsonify({'status': res_avatar['status']})

                return jsonify({'status': 'certo'})
        else:
            resposta = validar_e_sanitizar_arquivo(foto, "avatar")

            if not resposta["value"]:
                return jsonify({'status': resposta["status"]})

            try:
                foto.save(resposta["path"])
            except Exception as e:
                return jsonify({'status': f'erro ao armazenar a foto {e}'})

            resposta_uuid = armazenar_uuid(resp_uuid, user_id)
            if resposta_uuid["erro"]:
                return jsonify({'status': resposta_uuid["status"]})
                
    if banner and banner != "":

        status = verificar_existencia(user_id)

        if status["erro"]:
            return jsonify({'status': status['status']})

        res_uuid = status['uuid']
        if not res_uuid or res_uuid == "" or res_uuid == None:
            pass
        else:
            resposta = validar_e_sanitizar_arquivo(banner, "banner")

            if not resposta["value"]:
                return jsonify({'status': resposta["status"]})

            try:
                banner.save(resposta["path"])
            except Exception as e:
                return jsonify({'status': 'erro ao salvar a imagem'})

            resposta_uuid = armazenar_uuid(resp_uuid, user_id)
            if resposta_uuid["erro"]:
                return jsonify({'status': resposta_uuid["status"]})
            
    return jsonify({'status': 'sucesso'})