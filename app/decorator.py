from functools import wraps
from flask import request, session, redirect, url_for, jsonify, abort, g
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity

def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        user_id = None

        try:
            verify_jwt_in_request(optional=True)
            user_id = get_jwt_identity()
        except Exception:
            pass

        if not user_id:
            user_id = session.get('user_id') or request.cookies.get('user_id')

        if not user_id:
            return jsonify({'status': 'Não autorizado'}), 401

        g.user_id = user_id
        return func(*args, **kwargs)
    
    return wrapper