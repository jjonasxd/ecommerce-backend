from app.models import user_profile, registros, RefreshTokens
from app import db, upload_folder
from flask import jsonify, send_from_directory, session
from flask_jwt_extended import jwt_required, unset_jwt_cookies
from werkzeug.utils import secure_filename
from PIL import Image, UnidentifiedImageError
from PIL.Image import DecompressionBombError
import uuid
import os
import logging
import glob
from datetime import date, datetime

def resgatar_dados_usuario(UserId):
    try:
        user_profiles = user_profile.query.filter_by(user_id=UserId).first()
    except Exception as e:
        return jsonify({'status': "erro ao tentar contatadar o db"}), 500

    if not user_profiles:
        return jsonify({'status': 'usuario não encontrado'})

    user_data = {
        "nome_completo": user_profiles.primeiro_nome,
        "primeiro_nome": getattr(user_profiles, 'primeiro_nome', None),
        "avatar_url": getattr(user_profiles, 'avatar_url', None),
        "banner_url": getattr(user_profiles, 'banner_url', None),
        "bio": getattr(user_profiles, 'bio', None),
        "data_de_nascimento": getattr(user_profiles, 'data_de_nascimento', None),
        "vendedor": getattr(user_profiles, 'vendedor', None),
        "nivel": getattr(user_profiles, 'nivel', None),
        "compras": getattr(user_profiles, 'compras', None),
    }

    return jsonify(user_data)

allowed_extensions = ['png', 'jpg', 'jpeg', 'webp']
allowed_mimetypes = ['image/png', 'image/jpeg', 'image/webp']
allowed_ext_format = {
    "PNG": 'png',
    "JPEG": 'jpg',
    "WEBP": 'webp'
}

def validar_arquivo(file):
    exetensao = os.path.splitext(file.filename)[1][1:]
    exetensao.lower()

    if not exetensao:
        return 'extensao do arquivo não encontrada', True

    if exetensao in allowed_extensions and file.mimetype in allowed_mimetypes:
        pass
    else:
        return 'Extensão não permitida', True

    try:
        Image.MAX_IMAGE_PIXELS = 10_000_000
        img = Image.open(file.stream)
        img.verify()

        file.stream.seek(0)

        img = Image.open(file.stream)

        file.stream.seek(0)

        if img.format not in allowed_ext_format:
            return 'Formato de imagem não permitido', True
        
    except (IOError, SyntaxError, UnidentifiedImageError, DecompressionBombError): # Recomendação
        return 'A imagem fornecida não e válida', True

    return 'Checagem concluida imagem válida', False

def avatar_verificar_existencia(user_id):
    try:
        registro = user_profile.query.filter_by(user_id=user_id).first()
    except Exception as e:
        logging.error(e)
        return 'Erro ao tentar procurar no db', True, None

    if not registro:
        return 'Registro sem conteudo', True, None

    avatar_url = registro.avatar_url
    user_uuid = registro.uuid

    if not avatar_url:
        return 'Avatar não encontrado', False, None, user_uuid
    
    return 'Avatar encontrado', False, avatar_url, user_uuid

def atualizar_avatar(uuid, file, user_id):
    ext = os.path.splitext(file.filename)[1]
    path = f'app/uploads/{uuid}/avatar{ext}'

    try:
        arquivo_local = glob.glob(f'{os.path.dirname(path)}/avatar.*')[0]
        os.remove(arquivo_local)
        file.save(path)
    except IndexError:
        return jsonify({'status': 'Arquivo local não encontrado'}), 404
    except Exception as e:
        logging.error(e)
        return jsonify({'status': 'Erro ao tentar atualizar arquivo'}), 500

    url = f'http://127.0.0.1:5000/api/uploads/{uuid}/avatar{ext}'

    try:
        registro = user_profile.query.filter_by(user_id=user_id).first()
        if not registro:
            return jsonify({'status': 'Registro não encontrado'}), 404
        setattr(registro, 'avatar_url', url)
        db.session.commit()
        return jsonify({'status': 'Foto atualizada com sucesso'}), 200
    
    except Exception as e:
        return jsonify({'status': 'erro ao tentar salvar o avatar_url'}), 500

def criar_avatar(uuid, file, user_id):
    ext = os.path.splitext(file.filename)[1]
    path = f'app/uploads/{uuid}/avatar{ext}'

    try:
        file.save(path)
    except Exception as e:
        logging.error(e)
        return jsonify({'status': 'Erro ao tentar criar avatar'}), 500

    url = f'http://127.0.0.1:5000/api/uploads/{uuid}/avatar{ext}'

    try:
        registro = user_profile.query.filter_by(user_id=user_id).first()

        if not registro:
            return jsonify({'status': 'Registro não encontrado'}), 404

        setattr(registro, 'avatar_url', url)
        db.session.commit()

        return jsonify({'status': 'sucesso'}), 201
    
    except Exception as e:
        db.session.rollback()
        logging.error(e)
        return jsonify({'status': 'Erro ao tentar salvar no db'}), 500

def criar_perfil(user_id) -> None:
    user_uuid = uuid.uuid4().hex
    try:
        registro = user_profile.query.filter_by(user_id=user_id).first()
        if not registro:
            return 'registro não encontrado', None, True, 404
        setattr(registro, 'uuid', user_uuid)
        db.session.commit()
    
    except Exception as e:
        db.session.rollback()
        logging.error(e)
        return 'Erro ao criar UUID', None, True, 500

    try:
        os.makedirs(f'app/uploads/{user_uuid}', exist_ok=False)
        return 'sucesso', user_uuid, False, 201
    except FileExistsError:
        return 'Isso e muito raro, uuid já existente crie tente novamente', None, True, 500

def testar_dados(dados):
    bio = dados.get('bio')
    nome = dados.get('name')
    data = dados.get('data')

    if bio:
        if len(bio) > 50:
            return 'A bio esta muito grande', True

    if nome:
        if len(nome) > 100:
            return 'O nome esta muito grande', True

    if data:
        if not datetime.strptime(data, '%d/%m/%Y'):
            return 'Data invalida', True

    if not bio and not nome and not data:
        return 'Não tem nada', True
    
    return 'Tudo certinho', False

def alterar_dados(dados, user_id):
    bio = dados.get('bio')
    nome = dados.get('name')
    data = dados.get('data')

    try:
        registro = user_profile.query.filter_by(user_id=user_id).first()
        if not registro:
            return jsonify({'status': 'Registro vazio'}), 404
    except Exception as e:
        logging.error(e)
        return jsonify({'status': 'Erro ao tentar buscar registro'}), 500

    if bio:
        try:
            setattr(registro, 'bio', bio)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({'status': 'erro ao tentar adicionar bio'}), 500
    if nome:
        try:
            setattr(registro, 'nome_completo', nome)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({'status': 'erro ao tentar adicionar nome'}), 500
        primeiro_nome = nome.split()[0]
        try:
            setattr(registro, 'primeiro_nome', primeiro_nome)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({'status': 'erro ao tentar adicionar primeiro nome'}), 500


    if data: # Formato DD/MM/AAAA
        datas = data.split('/')
        timestamp_string = date(int(datas[2]), int(datas[1]), int(datas[0]))
        try:
            setattr(registro, 'data_de_nascimento', timestamp_string)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({'status': 'erro ao tentar adicionar data de nascimento'}), 500
        
    return jsonify({'status': 'atualizado com sucesso'}), 200

def excluir_tudo(user_id):
    try:
        user_profile_registro = user_profile.query.filter_by(user_id=user_id).first()
        cadastro_registro = registros.query.filter_by(id=user_id).first()
        RefreshTokens_registro = RefreshTokens.query.filter_by(userid=user_id).all()

        if user_profile_registro:
            db.session.delete(user_profile_registro)

        if cadastro_registro:
            db.session.delete(cadastro_registro)

        for token in RefreshTokens_registro:
            db.session.delete(token)

        db.session.commit()

    except Exception as e:
        logging.error(f'Erro ao tentar excluir id de usuario ID: {user_id} Erro: {e}')
        db.session.rollback()
        return jsonify({'status': 'erro ao tentar excluir sua conta'}), 500

    session.clear()
    response = jsonify({'status': 'conta excluida com sucesso'})
    unset_jwt_cookies(response)
    
    return response, 200