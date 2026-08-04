from flask import Blueprint, g
from app.produtos.service import *
from app.decorator import login_required
BP_produtos = Blueprint('routes_produtos', __name__)

@BP_produtos.route('/api/produtos', methods=['GET'])
def resgatar_produtos():
    status, erro, produtos, status_code = pegar_produtos_db()

    if erro:
        return jsonify({'status': status}), status_code

    return jsonify(produtos), status_code

@BP_produtos.route('/api/favoritos', methods=["GET"])
@login_required
def resgatar_favoritos():
    user_id = g.user_id

    if not user_id:
        return jsonify({'status': 'Id não encontrado'}), 401
    
    status, erro, status_code, fav = resgatar_fav(user_id)

    return jsonify({'status': status, 'fav_ids': fav}), status_code