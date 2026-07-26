from app.models import user_profile
from app import db, upload_folder
from flask import jsonify
from flask_jwt_extended import jwt_required
from werkzeug.utils import secure_filename
from PIL import Image, UnidentifiedImageError
import uuid
import os

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

def imagem_valida(filesteam):
    try:
        img = Image.open(filesteam)
        img.verify()
        filesteam.seek(0)
        return True
    except Exception:
        return False

# pqp to desgastado fazendo isso, amanha nos continua
def validar_e_sanitizar_arquivo(file, nome):
    exetensao = os.path.splitext(file.filename)[1][1:]
    exetensao.lower()

    if not exetensao:
        return {'status': 'extensão não encontrada'}

    if exetensao in allowed_extensions and file.mimetype in allowed_mimetypes:
        nome_seguro = f"{nome}.{exetensao}"
        pasta = uuid.uuid4().hex
        os.makedirs(f'{upload_folder}/{pasta}', exist_ok=True)

        path = os.path.join(f'{upload_folder}/{pasta}', nome_seguro)
    else:
        return {'status': 'extensão não permitida', 'value': False}

    Image.MAX_IMAGE_PIXELS = 10_000_000
    try:
        img = Image.open(file.stream)
        img.verify()

        img = Image.open(file.stream)
        file.stream.seek(0)
        if img.format not in allowed_ext_format:
            return {'status': 'formato de imagem invalido', 'value': False}
        
    except (IOError, SyntaxError, UnidentifiedImageError): # Recomendação
        return {'status': 'a imagem fornecida não e válida', 'value': False}

    return {'status': 'none', 'value': True, 'path': path, 'uuid': pasta}

def verificar_existencia(id):
    try:
        usuario = user_profile.query.filter_by(user_id=id).first()
        s_uuid = usuario.get('uuid')

        if not usuario:
            return {'status': 'arquivos do usuario não encontrado', 'erro': True}
        if not s_uuid:
            return {'status': 'uuid não encontrado', 'erro': False, 'vazio': True}

        return {'status': 'certinho', 'erro': False, 'uuid': s_uuid, }
    except Exception as e:
        return {'status': 'ocorreu um erro ao consutar o db', 'erro': True}

def atualizar_avatar(user_id, file):
    try:
        registro = user_profile.query.filter_by(user_id=user_id).first()

        if not registro:
            return {'status': 'registro não encontrado', 'erro': True}

        user_uuid = registro.get('uuid')

        if not user_uuid:
            return {'status': 'uuid do usuario não encontrado', 'erro': True}

        path = f'{upload_folder}/{user_uuid}'

        if not os.path.exists(path):
            return {'status': 'a pasta com o uuid do usuario não encontrada'}

        arquivos = os.listdir(path)
        print(arquivos, flush=True)

        return {'status': 'tudo bem', 'erro': False}

    except Exception as e:
        return {'status': 'erro ao tentar atualizar avatar', 'erro': True}
    
def armazenar_uuid(Uuid, User_id):
    try:
        registro = user_profile.query.filter_by(user_id=User_id).first()

        if not registro:
            return {'status': 'ocorreu um erro registro vazio', 'erro': True}

        registro.uuid = Uuid
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return {'status': 'ocorreu um erro ao tentar salvar no db', 'erro': True}

    return {'status': 'tudo certo', 'erro': False}
    