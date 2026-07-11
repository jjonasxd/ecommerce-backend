from re import search
from app import db
from app.models import registros, registros_temporarios
from flask import render_template
from secrets import randbelow
from resend import Emails
from datetime import datetime, timezone, timedelta

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
    existe = db.session.query(registros.query.filter_by(email=Email).exists()).scalar()
    if existe:
        return True
    else:
        return False
    
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
    
def armazenar_email_temporario(Email, Codigo):
    try:
        novo_registro = registros_temporarios(email=Email, codigo=Codigo)
        
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
    linha = registros_temporarios.query.filter_by(email=Email).first()

    if linha:
        if Code == linha.codigo:
            if validar_expiracao(linha.horario):
                print('Esta valido', flush=True)
                return {'status': 'perfeito', 'value': True} # Agora e so terminar o armazenamento definitivo no banco
            else:
                print('ja expirou', flush=True)
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

import argon2
def critografar(senha, email):
    argon2