from flask import Flask, Blueprint, request, session, g
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

@BP_perfil.route('/api/perfil-changes', methods=["PUT"])
@login_required
def mudancas():
    foto = request.files.get('foto')
    banner = request.files.get('banner')

    user_id = g.user_id

    if not user_id:
        return jsonify({'status': 'User_id vazio'}), 422
    
    if foto:
        v_status, v_erro, url = verificar_existencia(user_id, 'avatar_url', 'banner_url')

        if v_erro:
            return jsonify({'status': v_status})

        s_status, s_erro, avatar_seguro = validar_arquivo(foto)

        if s_erro:
            return jsonify({'status': s_status}), 422
    
        if not url: # Não tem url no db, e quer colocar um novo
            c_status, c_erro = criar_arquivo(avatar_seguro, 'avatar', user_id)

            if c_erro:
                return jsonify({'status': c_status}), 500
        else:
            a_status = atualizar_arquivo(url, avatar_seguro, 'avatar', user_id)

    if banner:
        v_status, v_erro, url = verificar_existencia(user_id, 'banner_url', 'avatar_url')

        if v_erro:
            return jsonify({'status': v_status})
    
        s_status, s_erro, banner_seguro = validar_arquivo(banner)
    
        if s_erro:
            return jsonify({'status': s_status}), 422
        
        if not url: # Não tem url no db, e quer colocar um novo
            c_status, c_erro = criar_arquivo(banner_seguro, 'banner', user_id)
    
            if c_erro:
                return jsonify({'status': c_status}), 500
            else:
                return jsonify({'status': c_status}), 201
        else:
            a_status = atualizar_arquivo(url, banner_seguro, 'banner', user_id)
            return jsonify({'status': a_status})
        

from flask import send_file

@BP_perfil.route('/api/uploads/<string:user_uuid>/<path:filename>')
def uploads(user_uuid, filename):
    path = os.path.abspath(f'{upload_folder}/{user_uuid}/{filename}') # Pqp fiquei 1 hora para descobrir que não era o caminho relativo, mais sim absoluto

    return send_file(path) # Usei send_file mais poderia ser send_from_directory