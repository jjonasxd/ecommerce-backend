from flask import Flask, Blueprint, request
from app.perfil.services import *

BP_perfil = Blueprint('rotas_perfil', __name__)

@BP_perfil.route('/api/perfil', methods=['POST', 'GET'])
def configs():
    if request.method == 'GET':
        pass