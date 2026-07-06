from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from argon2 import PasswordHasher
from dotenv import load_dotenv
import os
import secrets
import resend

load_dotenv()

resend_api = os.getenv("RESEND_API")


#Banco de dados falso por enquanto
registros = {
    'nome': [],
    'email': ['genisolgestor@gmail.com'],
    'senha': []
}

email_temporario = {}
id_email_temporario = 0


def cr_senha(senha):
    ph = PasswordHasher()
    cript_senha = ph.hash(senha)

    return(cript_senha)



app = Flask(__name__)
CORS(app)

@app.route('/api/login', methods=['POST'])
def login():
   dados = request.get_json()
   email = dados["email"]
   


@app.route('/api/register', methods=['POST'])
def armazenar():
    dados = request.get_json()

    rota_email = dados['email']

    for emails in registros.get('email'):
        if emails == rota_email:
            return jsonify({'stats_conta': '0'}) #0 = conta já existente
        
    else:
        codigo = f"{secrets.randbelow(999999):06d}"
        email_temporario[rota_email] = codigo

        #rota_senha = dados['password']
        #final_senha = cr_senha(rota_senha)
        #rota_nome = dados['name']

        try:
            html = render_template('emails/email.html', codigo_email=str(codigo))
            resend.api_key = resend_api
            r = resend.Emails.send({
                "from": "onboarding@resend.dev",
                "to": rota_email,
                "subject": "Seu codigo de testação de email.",
                "html": html
            })
            return jsonify({'stats_conta': 1}) #conta nao existente == bom
        
        except:
            return jsonify({"erro": "email mal-informado"})

@app.route('/api/codigo', methods=['POST'])
def testar_email():
    dados = request.get_json()
    try:
        usuario_codigo = dados['codigo']
        usuario_email = dados['email']
    except:
        return jsonify({'stats_conta': '4'}) # email ou codigo invalido

    if str(usuario_codigo).isnumeric():
        if email_temporario.get(usuario_email) == usuario_codigo:
            return jsonify({'stats_conta': '2'}) # sucesso total
        else:
            return jsonify({'stats_conta': '3'}) # Email errado
    else:
        return jsonify({'stats_conta': '4'})
    
if __name__ == '__main__':
    app.run(debug=False)