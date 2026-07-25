from app.models import user_profile
from app import db
from flask import jsonify
from flask_jwt_extended import jwt_required
from werkzeug.utils import secure_filename
from PIL import Image
import uuid

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
def validar_e_sanitizar_arquivo(file):
    exetensao = str(file.filename).lower().rsplit(".", 1)[1]

    if exetensao in allowed_extensions and file.mimetype in allowed_mimetypes:
        nome = f"avatar_{uuid.uuid4().hex}.{exetensao}"
    else:
        return {'status': 'extensão não permitida', 'value': False}

    Image.MAX_IMAGE_PIXELS = 10_000_000
    try:
        img = Image.open(file.stream)
        img.verify()

        file.stream.seek(0)
        img = Image.open(file.stream)
        if img.format not in allowed_ext_format:
            return {'status': 'formato de imagem invalido', 'value': False}
    except Exception:
        return {'status': 'a imagem fornecida não e válida', 'value': False}

    return {'status': 'none', 'value': True, 'nome': nome}