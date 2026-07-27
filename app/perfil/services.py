from app.models import user_profile
from app import db, upload_folder
from flask import jsonify, send_from_directory
from flask_jwt_extended import jwt_required
from werkzeug.utils import secure_filename
from PIL import Image, UnidentifiedImageError
from PIL.Image import DecompressionBombError
import uuid
import os
import logging
import glob

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
        return 'extensao do arquivo não encontrada', True, None

    if exetensao in allowed_extensions and file.mimetype in allowed_mimetypes:
        pass
    else:
        return 'Extensão não permitida', True, None

    try:
        Image.MAX_IMAGE_PIXELS = 10_000_000
        img = Image.open(file.stream)
        img.verify()

        file.stream.seek(0)

        img = Image.open(file.stream)

        file.stream.seek(0)

        if img.format not in allowed_ext_format:
            return 'Formato de imagem não permitido', True, None
        
    except (IOError, SyntaxError, UnidentifiedImageError, DecompressionBombError): # Recomendação
        return 'A imagem fornecida não e válida', True, None

    return 'Checagem concluida imagem válida', False, file

def verificar_existencia(id, nome_url):
    try:
        registro = user_profile.query.filter_by(user_id=id).first()

        if not registro:
            logging.error(f'Registro não encontrado UserID: {id}')
            return "Registro não encontrado", True, None

        url = getattr(registro, nome_url, None)
        print(url, flush=True)

        if not url:
            return 'URL não encontrada', False, None

        return "Encontrada", False, url
    except Exception as e:
        return f"Erro ao consultar o DB {e}", True, None

def criar_arquivo(file_secure, nome, user_id):
    extensao = os.path.splitext(file_secure.filename)[1]
    nome_arquivo = f'{nome}{extensao}'
    user_uuid = uuid.uuid4().hex
    path = f'{upload_folder}/{user_uuid}'
    nome_url = f'{nome}_url'

    try:
        os.makedirs(path, exist_ok=False)
        avatar_path = os.path.join(path, nome_arquivo)

        file_secure.save(avatar_path)
    except FileExistsError:
        return 'Erro avatar já criado, tente novamente', True

    url = f'http://127.0.0.1:5000/api/uploads/{user_uuid}/{nome_arquivo}'

    try:
        registro = user_profile.query.filter_by(user_id=user_id).first()

        if not registro:
            logging.error(f'Registro não encontrado UserID: {user_id}')
            return 'registro não encontrado', True

        setattr(registro, nome_url, url)

        db.session.commit()

        return 'Sucesso', False
    except Exception as e:
        db.session.rollback()
        logging.error(f'Erro ao tentar atualizar/criar o registro UserID: {user_id} Erro: {e}')
        return 'Erro ao tentar atualizar/criar o registro', True

def atualizar_arquivo(user_uuid, secure_file, nome):
    try:
        arquivo_path = glob.glob(f'{upload_folder}/{user_uuid}/{nome}.*')[0]
    except IndexError:
        return 'Nenhum arquivo encontrado', True
    
    arquivo_nome = os.path.basename(arquivo_path)

    for ext in allowed_extensions:
        if f'{nome}.{ext}' == arquivo_nome:
            break
    else:
        return 'Extensão de arquivo não permitida', True

    extensao = os.path.splitext(secure_file.filename)[1]
    try:
        os.path.join(arquivo_path, )
        os.replace(arquivo_path, f'{upload_folder}/{user_uuid}/{nome}{extensao}')
    except Exception as e:
        return f'Erro ao tentar manipular arquivos {e}', True