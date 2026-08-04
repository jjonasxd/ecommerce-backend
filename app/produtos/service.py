from app.models import produtos, favoritos
from app import db
from sqlalchemy import func
import logging
from flask import jsonify

def pegar_produtos_db():
    try:
        registro_produtos = produtos.query.order_by(func.random()).limit(15).all()

        if not registro_produtos:
            return 'Registro não encontrado', True, None, 404
        
        produtos_aleatorios = [{'id': getattr(produto, 'id'),  # eu queria criar o slug, mais esse projeto já ta ficando grande demais
                                'nome': getattr(produto, 'nome'), 
                                'descricao': getattr(produto, 'descricao'),
                                'imagem': getattr(produto, 'imagem'),
                                'preco': getattr(produto, 'preco'),
                                'marca': getattr(produto, 'marca')
                                } for produto in registro_produtos]

        return 'Sucesso', False, produtos_aleatorios, 200
    except Exception as e:
        logging.error(e)
        return 'Algum erro ao buscar os produto', True, None, 500

def resgatar_fav(user_id):
    try:
        registros = favoritos.query.filter_by(user_id=user_id).all()
        favoritos_id = []

        if not registros:
            return 'Registro vazio', True, 404, None

        for registro in registros:
            fav_id = getattr(registro, 'produto_id')
            favoritos_id.append(fav_id)

        return 'Sucesso', False, 200, favoritos_id
    
    except Exception as e:
        logging.error(e)
        return 'Algum erro ao tentar resgatar favoritos', True, 500, None

def registrar_fav(user_id, product_id):
    try:
        registro = favoritos.query.filter_by(usuario_id=user_id).all()
        if not registro:
            raise Exception
        
        setattr(registro, 'usuario_id', user_id)
        setattr(registro, 'produto_id', product_id)
        db.session.commit()
        return jsonify({'status': 'Favoritos adicionado'}), 200
    
    except Exception as e:
        try:
            registro = favoritos(usuario_id=user_id, produto_id=product_id)
            db.session.add(registro)
            db.session.commit()
            return jsonify({'status': 'Favoritos criado'}), 201
        except Exception as e:
            db.session.rollback()
            logging.error(e)
            return jsonify({'status': 'erro ao tentar criar'}), 500