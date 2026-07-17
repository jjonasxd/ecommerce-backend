from re import search
from app import db
from app.models import registros, registros_temporarios
from flask import render_template, jsonify
from secrets import randbelow
from resend import Emails
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
import os
from cryptography.fernet import Fernet
import hashlib
from flask_jwt_extended import create_access_token, set_access_cookies

load_dotenv()

def verificar_formulario(formulario):
    nome = formulario.get('name', '')
    senha = formulario.get('password', '')
    email = formulario.get('email', '')

    r_nome = r"^[A-Za-zÀ-ÿ ]{3,}"
    if not search(r_nome, nome):
        return False
    
    r_senha = r"^(?=.*[A-Z])(?=.*[a-z])(?=.*[.,!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?~`]).{8,}$"
    if not search(r_senha, senha):
        return False
    
    r_email = r'^[A-Za-z0-9%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
    if not search(r_email, email):
        return False
    
    return True
    # os regex's não fui eu que fiz

def email_existe(Email):
    f = Fernet(os.getenv('FERNET_KEY'))

    Blind_Index = hashlib.sha256(Email.encode()).hexdigest()

    existe = db.session.query(registros.query.filter_by(blind_index=Blind_Index).exists()).scalar()
    
    return existe
    
def enviar_codigo_de_verficacao(email):
    codigo = f'{randbelow(999999):06d}'

    mensagem_html = render_template('email.html', codigo_email=codigo)
    try:
        Emails.send({
            "from": "onboarding@resend.dev",
            "to": email,
            "subject": "Seu codigo de email",
            "html": mensagem_html
        })
        return codigo
    except Exception as e:
        return f'Ocorreu um erro ao tentar enviar o codigo {e}'
    
def armazenar_email_temporario(Email, Senha, Codigo, Blind_Index, Nome):
    try:
        novo_registro = registros_temporarios(email=Email, senha=Senha, codigo=Codigo, blind_index=Blind_Index, nome=Nome)
        
        db.session.add(novo_registro)
        db.session.commit()
        return {'status': '200', 'details': 'sucesso ao enviar'}
    
    except Exception as e:
        return {'status': '0', 'details': f'Ocorreu um erro ao enviar o email para o banco de dados {e}'}
    
def verificar_otp(codigo):
    if len(codigo) == 6 and str(codigo).isnumeric():
        return True
    else:
        return False

def teste_codigo_valido(Code, Email):
    Blind_Index = hashlib.sha256(Email.encode()).hexdigest()
    hash_code = hashlib.sha256(Code.encode()).hexdigest()

    linha = registros_temporarios.query.filter_by(blind_index=Blind_Index).first()

    if linha:
        if hash_code == linha.codigo:
            if validar_expiracao(linha.horario):
                return {'status': 'perfeito', 'value': True} # Agora e so terminar o armazenamento definitivo no banco
            else:
                return {'status': 'o codigo ja expirou'}
        else:
            return {'status': 'o codigo esta errado', 'value': False}
    else:
        return {'status': 'Esse email não esta no registro', 'value': False}
    

def validar_expiracao(horario_criado): # metade dessa funcão foi escrita por ia, não tinha como não fazer isso!
    utc0 = datetime.now(timezone.utc)
    
    hora_objeto = datetime.strptime(str(horario_criado), "%H:%M:%S").time()
    
    horario_objeto = datetime.combine(utc0.date(), hora_objeto, tzinfo=timezone.utc)
    
    expiracao = timedelta(minutes=10)
    utc0_expirado = horario_objeto + expiracao

    return utc0_expirado > utc0

from argon2 import PasswordHasher
def criptografar(senha, email, codigo):
    try:
        # Senha
        ph = PasswordHasher()
        hash_senha = ph.hash(senha)
    except Exception as e:
        return f'erro ao criptografar, senha {e}'

    try:
        # Email
        chave = os.getenv("FERNET_KEY")
        f = Fernet(chave)
        crip_email = f.encrypt(email.encode())
    except Exception as e:
        return f'erro ao criptografar, email {e}'
    
    try:
        # Codigo
        hash_codigo = hashlib.sha256(codigo.encode()).hexdigest()
    except Exception as e:
        return f'erro ao criptografar, codigo {e}'
    
    try:
        # Blind Index
        blind_index = hashlib.sha256(email.encode('utf-8')).hexdigest()
    except Exception as e:
        return f'erro ao criptografar, Blind index'
    
    return hash_senha, crip_email, hash_codigo, blind_index

def armazenar_db_registro(Email):
    Blind_Index = hashlib.sha256(Email.encode()).hexdigest()
    try:
        # Armazenar oficialmente
        encontrar = registros_temporarios.query.filter_by(blind_index=Blind_Index).first()
        novo_registro = registros(email=encontrar.email, senha=encontrar.senha, nome=encontrar.nome, blind_index=encontrar.blind_index)
        db.session.add(novo_registro)

        # Deletar registro temporario
        db.session.delete(encontrar)

        db.session.commit()
        return {'status': 'nada de errado', 'valor': True}

    except Exception as e:
        db.session.rollback()
        return {'status' f'Algo deu errado ao tentar contadar o db, armazenar ou deletar {e}' 'valor': False}
    
def jwt(Email):
    Blind_Index = hashlib.sha256(Email.encode()).hexdigest()
    token = create_access_token(identity=Blind_Index)

    response = jsonify({'status': 'realizado com sucesso'})

    set_access_cookies(response, token)

    return response