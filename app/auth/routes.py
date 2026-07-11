from flask import Blueprint, request, jsonify
from app.auth.services import *

main_authBP = Blueprint('RouteAuth', __name__)

@main_authBP.route('/api/registro', methods=['POST'])
def formulario():
    dados = request.json
    try:
        email = dados.get('email')
    except Exception as e:
        return jsonify({'status': f'erro na hora de pegar o email, {e}'})

    if verificar_formulario(dados):
        if email_existe(email):
            return jsonify({'codigo': '1', 'status': 'ja existe'})
        
        else:
            codigo = enviar_codigo_de_verficacao(email)
            
            if codigo.isnumeric():
                status = armazenar_email_temporario(email, codigo)
                print(codigo, flush=True)

                if status.get('status') == '200':
                    return jsonify({'status': status.get('status')})
                else:
                    return jsonify({'status': '0', 'details': 'erro ao armazenar no banco de dados'})
                  
            else:
                print(codigo, flush=True)
                return jsonify({'status': "erro o codigo gerado não atende os requisitos 500"})
    else:
        return jsonify({'status': 'erro, senha/email/nome mal-informados'})

@main_authBP.route('/api/codigo', methods=['POST'])
def codigo():
    dados = request.json

    code = dados.get('codigo')
    email = dados.get('email')
    senha = dados.get('senha')
    if code == None or email == None or senha == None:
        return jsonify({'status': 'vazio'})
    
    if verificar_otp(code):
        valido = teste_codigo_valido(code, email)

        if valido.get('value'):
            return jsonify({'status': 'codigo correto'})
        
        elif valido.get('value') == None:
            return jsonify({'status': 'o codigo esta vazio :/'}) # O codigo não e o mesmo :/
        
        else:
            return jsonify({'status': valido.get('status')})

    else:
        return jsonify({'status': 'codigo invalido'})