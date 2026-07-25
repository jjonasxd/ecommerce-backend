from flask import Blueprint, request, jsonify
from app.auth.services import *
from flask_jwt_extended import jwt_required, get_jwt_identity

main_authBP = Blueprint('RouteAuth', __name__)

@main_authBP.route('/api/registro', methods=['POST'])
def formulario():
    dados = request.json

    nome = dados.get('name')
    email = dados.get('email')
    senha = dados.get('password')
    remember = dados.get('remember')

    if not nome or not email or not senha or remember is None:
        return jsonify({'status': f'Informações incompletas ou inexistente'})

    if verificar_formulario(dados):
        email_resposta = email_existe(email)

        if email_resposta["erro"]: # Eu deixei direto porque sei que não vou ter KeyError
            return jsonify({'codigo': '500', 'status': 'erro ao tentar contadar o db'})
        elif email_resposta["existe"]:
            return jsonify({'codigo': '1', 'status': 'ja existe'})
        
        else:
            codigo = enviar_codigo_de_verficacao(email)
            
            if codigo.isnumeric():
                hash_senha, crip_email, hash_codigo, blind_index = criptografar(senha, email, codigo)

                status = armazenar_email_temporario(crip_email, hash_senha, hash_codigo, blind_index, nome, remember)

                if status.get('status') == '200':
                    return jsonify({'status': status.get('status')})
                else:
                    return jsonify({'status': '0', 'details': 'erro ao armazenar no banco de dados'})
                  
            else:
                return jsonify({'status': "erro o codigo gerado não atende os requisitos 500"})
    else:
        return jsonify({'status': 'erro, senha/email/nome mal-informados'})

@main_authBP.route('/api/codigo', methods=['POST'])
def codigo():
    dados = request.json

    code = dados.get('codigo')
    email = dados.get('email')

    if not code or not email:
        return jsonify({'status': 'dados incompletos'})
    if verificar_otp(code):
        valido = teste_codigo_valido(code, email)

        if valido.get('value'):
            valor = armazenar_db_registro(email)
            if valor.get('valor'):
                if valor.get('remember'):
                    jsw_response = jwt(email)
                else:
                    jsw_response = criar_session(email)
                
                return jsw_response
            else:
                return jsonify(valor)
            
        elif valido.get('value') == None:
            return jsonify({'status': 'o codigo esta vazio :/'}) # O codigo não e o mesmo :/
        
        else:
            return jsonify({'status': valido.get('status')})

    else:
        return jsonify({'status': 'codigo invalido'})

@main_authBP.route('/api/login', methods=["POST"])
def login():
    dados = request.json
    dados['name'] = 'Joao araujo' # Simulando nome, apenas para validar o nome

    if verificar_formulario(dados):
        return validando_login(dados)
    else:
        return jsonify({'codigo': '2', 'details': 'senha/email-informado'})

@main_authBP.route('/api/me', methods=["GET"])
@jwt_required()
def testar_jwt():
    return jsonify({'status': 'autenticado'}), 200