from re import search
from app import db
from app.models import registros, registros_temporarios, RefreshTokens, user_profile
from flask import render_template, jsonify
from secrets import randbelow
from resend import Emails
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
import os
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerifyMismatchError
from cryptography.fernet import Fernet
import hashlib
from flask_jwt_extended import create_access_token, set_access_cookies, create_refresh_token, set_refresh_cookies
import logging
from app import JWTManager

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

        db.session.flush() # Recomendação

        registro_basico = dados_basicos_profile(novo_registro.id, encontrar.nome) # são informações básicas para criar a tabela de profile
        db.session.add(registro_basico)

        db.session.commit()

        return {'status': 'nada de errado', 'valor': True}

    except Exception as e:
        db.session.rollback()
        return {'status': f'Algo deu errado ao tentar contadar o db, armazenar ou deletar {e}', 'valor': False}
    
def jwt(email):
    Blind_Index = hashlib.sha256(email.encode()).hexdigest()

    try:
        usuario = registros.query.filter_by(blind_index=Blind_Index).first()
    except Exception as e:
        logging.error(e)
        return jsonify({'status': 'erro ao procurar por blind index no db', 'details': e})
    
    if not usuario:
        return jsonify({'status': 'nenhum usuario encontrado'})

    try:
        RefreshTokens.query.filter_by(userid=usuario.id).delete()
        db.session.commit()
    except:
        pass

    try:
        access_token = create_access_token(identity=str(usuario.id))
        refresh_token = create_refresh_token(identity=str(usuario.id))
        response = jsonify({'status': 'realizado com sucesso', 'codigo': '1'})

        set_access_cookies(response, access_token)
        set_refresh_cookies(response, refresh_token)
    except Exception as e:
        return jsonify({'status': 'ocorreu um erro ao criar os tokens', 'details': e})
    
    try:
        TableRefreshToken = RefreshTokens(token=refresh_token, userid=int(usuario.id))
        db.session.add(TableRefreshToken)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'erro ao enviar o refresh_token no db', 'details': e})
    
    return response

def dados_basicos_profile(User_Id, nome):
    Nome_Final = str(nome).strip()
    Primeiro_Nome = Nome_Final.split()
    perfil_basico = user_profile(user_id=User_Id, nome_completo=Nome_Final, primeiro_nome=Primeiro_Nome[0])

    return perfil_basico

def validando_login(dados):
    # Pegando dados
    email = dados.get('email')
    senha = dados.get('password')

    if not email or not senha:
        return jsonify({'codigo': '3', 'details': 'senha vazia'})

    # Procurando no db
    Blind_Index = hashlib.sha256(email.encode()).hexdigest()
    try:
        userlogin = registros.query.filter_by(blind_index=Blind_Index).first()
    except Exception as e:
        return jsonify({'codigo': '4', 'details': 'erro ao tentar encontrar dentro do db'})

    if not userlogin:
        return jsonify({'codigo': '8', 'details': 'erro ao tentar buscar usuario do dbl, retorno vazio'})
    # Validando senha
    ph = PasswordHasher()

    try:
        ph.verify(userlogin.senha, senha)
        return jwt(email)
    
    except VerifyMismatchError:
        return jsonify({'codigo': '5', 'details': 'senha incorreta'})
    except InvalidHashError:
        return jsonify({'codigo': '6', 'details': 'Formato do hash armazenado e incorreto'})